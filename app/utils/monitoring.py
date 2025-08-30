import time
from datetime import datetime
from typing import Any, Dict

import psutil
from sqlalchemy import text

from app.database import SessionLocal
from app.utils.logging import get_logger

logger = get_logger("portfolio.monitoring")


class HealthChecker:
    """Health checking utilities for the application."""

    def __init__(self):
        self.start_time = datetime.utcnow()

    def get_application_health(self) -> Dict[str, Any]:
        """Get overall application health status."""
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "version": "1.0.0",
            "environment": "development",
        }

        # Check database health
        db_health = self.check_database_health()
        health_data["database"] = db_health

        # Check system resources
        system_health = self.check_system_health()
        health_data["system"] = system_health

        # Determine overall status
        if not db_health["connected"] or system_health["memory_usage_percent"] > 90:
            health_data["status"] = "unhealthy"
        elif system_health["memory_usage_percent"] > 75:
            health_data["status"] = "degraded"

        return health_data

    def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            start_time = time.time()
            db = SessionLocal()

            # Simple connectivity test
            _ = db.execute(text("SELECT 1")).scalar()

            # Measure query time
            query_time = time.time() - start_time

            db.close()

            return {
                "connected": True,
                "query_time_ms": round(query_time * 1000, 2),
                "status": "healthy" if query_time < 0.1 else "slow",
            }

        except Exception as e:
            logger.error(
                "Database health check failed",
                extra={"event": "database_health_check_failed", "error": str(e)},
            )

            return {"connected": False, "error": str(e), "status": "unhealthy"}

    def check_system_health(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            # Memory usage
            memory = psutil.virtual_memory()

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Disk usage
            disk = psutil.disk_usage("/")

            return {
                "memory_usage_percent": memory.percent,
                "memory_available_mb": round(memory.available / 1024 / 1024, 2),
                "cpu_usage_percent": cpu_percent,
                "disk_usage_percent": round((disk.used / disk.total) * 100, 2),
                "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                "status": "healthy",
            }

        except Exception as e:
            logger.error(
                "System health check failed",
                extra={"event": "system_health_check_failed", "error": str(e)},
            )

            return {"status": "unknown", "error": str(e)}


class MetricsCollector:
    """Collect application metrics."""

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.auth_attempts = 0
        self.auth_failures = 0

    def record_request(self, response_time: float, status_code: int):
        """Record request metrics."""
        self.request_count += 1
        self.response_times.append(response_time)

        if status_code >= 400:
            self.error_count += 1

        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]

    def record_auth_attempt(self, success: bool):
        """Record authentication attempt."""
        self.auth_attempts += 1
        if not success:
            self.auth_failures += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        if not self.response_times:
            avg_response_time = 0
            max_response_time = 0
        else:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            max_response_time = max(self.response_times)

        error_rate = (
            (self.error_count / self.request_count * 100)
            if self.request_count > 0
            else 0
        )
        auth_failure_rate = (
            (self.auth_failures / self.auth_attempts * 100)
            if self.auth_attempts > 0
            else 0
        )

        return {
            "requests": {
                "total": self.request_count,
                "errors": self.error_count,
                "error_rate_percent": round(error_rate, 2),
            },
            "response_times": {
                "average_ms": round(avg_response_time * 1000, 2),
                "max_ms": round(max_response_time * 1000, 2),
            },
            "authentication": {
                "attempts": self.auth_attempts,
                "failures": self.auth_failures,
                "failure_rate_percent": round(auth_failure_rate, 2),
            },
        }

    def reset_metrics(self):
        """Reset all metrics (useful for periodic reporting)."""
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.auth_attempts = 0
        self.auth_failures = 0


class PerformanceMonitor:
    """Monitor application performance and detect anomalies."""

    def __init__(self):
        self.slow_query_threshold = 1.0  # seconds
        self.error_rate_threshold = 5.0  # percent
        self.response_time_threshold = 2.0  # seconds

    def check_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics and detect issues."""
        issues = []

        # Check error rate
        error_rate = metrics["requests"]["error_rate_percent"]
        if error_rate > self.error_rate_threshold:
            issues.append(
                {
                    "type": "high_error_rate",
                    "severity": "warning",
                    "message": (
                        f"Error rate ({error_rate}%) exceeds threshold "
                        f"({self.error_rate_threshold}%)"
                    ),
                    "value": error_rate,
                    "threshold": self.error_rate_threshold,
                }
            )

        # Check response time
        avg_response_time = metrics["response_times"]["average_ms"] / 1000
        if avg_response_time > self.response_time_threshold:
            issues.append(
                {
                    "type": "high_response_time",
                    "severity": "warning",
                    "message": (
                        f"Average response time ({avg_response_time:.2f}s) exceeds threshold "
                        f"({self.response_time_threshold}s)"
                    ),
                    "value": avg_response_time,
                    "threshold": self.response_time_threshold,
                }
            )

        # Check authentication failure rate
        auth_failure_rate = metrics["authentication"]["failure_rate_percent"]
        if auth_failure_rate > 10.0:  # 10% threshold
            issues.append(
                {
                    "type": "high_auth_failure_rate",
                    "severity": "critical",
                    "message": (
                        f"Authentication failure rate ({auth_failure_rate}%) is suspiciously high"
                    ),
                    "value": auth_failure_rate,
                    "threshold": 10.0,
                }
            )

        return {
            "status": "degraded" if issues else "healthy",
            "issues": issues,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global instances
health_checker = HealthChecker()
metrics_collector = MetricsCollector()
performance_monitor = PerformanceMonitor()


def log_performance_metrics():
    """Log current performance metrics."""
    metrics = metrics_collector.get_metrics()
    performance_analysis = performance_monitor.check_performance(metrics)

    logger.info(
        "Performance metrics",
        extra={
            "event": "performance_metrics",
            "metrics": metrics,
            "performance_analysis": performance_analysis,
        },
    )

    # Log any performance issues
    for issue in performance_analysis["issues"]:
        logger.warning(
            "Performance issue detected",
            extra={"event": "performance_issue", "issue": issue},
        )
