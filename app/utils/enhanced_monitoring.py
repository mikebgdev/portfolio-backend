"""
Enhanced monitoring and metrics collection for Portfolio Backend API.
"""

import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil
from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal
from app.utils.logging import get_logger

logger = get_logger("portfolio.monitoring")


class MetricsCollector:
    """Advanced metrics collection for application monitoring."""

    def __init__(self):
        self.startup_time = datetime.now()
        self.request_metrics = defaultdict(
            lambda: {
                "count": 0,
                "total_time": 0,
                "errors": 0,
                "recent_response_times": deque(maxlen=100),
            }
        )
        self.endpoint_metrics = defaultdict(
            lambda: {
                "total_requests": 0,
                "success_count": 0,
                "error_count": 0,
                "avg_response_time": 0,
                "recent_times": deque(maxlen=50),
            }
        )
        self.system_metrics_history = deque(maxlen=144)  # 12 hours of 5-min intervals
        self.database_metrics = deque(maxlen=100)
        self.security_events = deque(maxlen=1000)
        self.lock = threading.Lock()

    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        response_time: float,
        user_id: Optional[int] = None,
    ):
        """Record request metrics."""
        with self.lock:
            key = f"{method} {path}"
            metrics = self.request_metrics[key]
            metrics["count"] += 1
            metrics["total_time"] += response_time
            metrics["recent_response_times"].append(response_time)

            if status_code >= 400:
                metrics["errors"] += 1

            # Endpoint-specific metrics
            endpoint_metrics = self.endpoint_metrics[path]
            endpoint_metrics["total_requests"] += 1
            endpoint_metrics["recent_times"].append(response_time)

            if status_code < 400:
                endpoint_metrics["success_count"] += 1
            else:
                endpoint_metrics["error_count"] += 1

            # Calculate running average
            if endpoint_metrics["recent_times"]:
                endpoint_metrics["avg_response_time"] = sum(
                    endpoint_metrics["recent_times"]
                ) / len(endpoint_metrics["recent_times"])

    def record_database_operation(self, operation: str, duration: float, success: bool):
        """Record database operation metrics."""
        with self.lock:
            self.database_metrics.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "operation": operation,
                    "duration_ms": duration * 1000,
                    "success": success,
                }
            )

    def record_security_event(
        self, event_type: str, severity: str, details: Dict[str, Any]
    ):
        """Record security events for monitoring."""
        with self.lock:
            self.security_events.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": event_type,
                    "severity": severity,
                    "details": details,
                }
            )

    def get_request_metrics(self) -> Dict[str, Any]:
        """Get aggregated request metrics."""
        with self.lock:
            total_requests = sum(m["count"] for m in self.request_metrics.values())
            total_errors = sum(m["errors"] for m in self.request_metrics.values())

            return {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": (
                    (total_errors / total_requests * 100) if total_requests > 0 else 0
                ),
                "endpoints": {
                    path: {
                        "requests": metrics["total_requests"],
                        "success_rate": (
                            (metrics["success_count"] / metrics["total_requests"] * 100)
                            if metrics["total_requests"] > 0
                            else 0
                        ),
                        "avg_response_time_ms": round(
                            metrics["avg_response_time"] * 1000, 2
                        ),
                    }
                    for path, metrics in self.endpoint_metrics.items()
                },
                "top_errors": self._get_top_error_endpoints(),
            }

    def get_database_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics."""
        with self.lock:
            if not self.database_metrics:
                return {"operations": 0, "avg_duration_ms": 0, "success_rate": 100}

            total_ops = len(self.database_metrics)
            successful_ops = sum(1 for op in self.database_metrics if op["success"])
            avg_duration = (
                sum(op["duration_ms"] for op in self.database_metrics) / total_ops
            )

            return {
                "operations_last_hour": total_ops,
                "avg_duration_ms": round(avg_duration, 2),
                "success_rate": (
                    round(successful_ops / total_ops * 100, 2) if total_ops > 0 else 100
                ),
                "recent_operations": list(self.database_metrics)[-10:],
            }

    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security event metrics."""
        with self.lock:
            if not self.security_events:
                return {"total_events": 0, "severity_breakdown": {}}

            severity_count: dict[str, int] = defaultdict(int)
            type_count: dict[str, int] = defaultdict(int)

            for event in self.security_events:
                severity_count[event["severity"]] += 1
                type_count[event["type"]] += 1

            return {
                "total_events": len(self.security_events),
                "severity_breakdown": dict(severity_count),
                "event_types": dict(type_count),
                "recent_events": list(self.security_events)[-20:],
            }

    def _get_top_error_endpoints(self) -> List[Dict[str, Any]]:
        """Get endpoints with highest error rates."""
        error_endpoints = []
        for path, metrics in self.endpoint_metrics.items():
            if metrics["error_count"] > 0:
                error_rate = metrics["error_count"] / metrics["total_requests"] * 100
                error_endpoints.append(
                    {
                        "path": path,
                        "error_rate": round(error_rate, 2),
                        "error_count": metrics["error_count"],
                        "total_requests": metrics["total_requests"],
                    }
                )

        return sorted(error_endpoints, key=lambda x: x["error_rate"], reverse=True)[:5]

    def record_system_metrics(self):
        """Record current system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory": {
                    "used_mb": memory.used / 1024 / 1024,
                    "available_mb": memory.available / 1024 / 1024,
                    "percent_used": memory.percent,
                },
                "disk": {
                    "used_gb": disk.used / 1024 / 1024 / 1024,
                    "free_gb": disk.free / 1024 / 1024 / 1024,
                    "percent_used": (disk.used / disk.total) * 100,
                },
                "process": self._get_process_metrics(),
            }

            with self.lock:
                self.system_metrics_history.append(metrics)

        except Exception as e:
            logger.error(f"Error recording system metrics: {str(e)}")

    def _get_process_metrics(self) -> Dict[str, Any]:
        """Get current process metrics."""
        try:
            process = psutil.Process()
            with process.oneshot():
                return {
                    "cpu_percent": process.cpu_percent(),
                    "memory_mb": process.memory_info().rss / 1024 / 1024,
                    "threads": process.num_threads(),
                    "connections": (
                        len(process.connections())
                        if hasattr(process, "connections")
                        else 0
                    ),
                }
        except Exception:
            return {"cpu_percent": 0, "memory_mb": 0, "threads": 0, "connections": 0}

    def get_system_metrics(self, hours: int = 1) -> Dict[str, Any]:
        """Get system metrics summary."""
        with self.lock:
            if not self.system_metrics_history:
                return {"status": "no_data"}

            # Get recent metrics
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [
                m
                for m in self.system_metrics_history
                if datetime.fromisoformat(m["timestamp"]) > cutoff_time
            ]

            if not recent_metrics:
                return {"status": "no_recent_data"}

            # Calculate averages
            avg_cpu = sum(m["cpu_percent"] for m in recent_metrics) / len(
                recent_metrics
            )
            avg_memory = sum(m["memory"]["percent_used"] for m in recent_metrics) / len(
                recent_metrics
            )
            avg_disk = sum(m["disk"]["percent_used"] for m in recent_metrics) / len(
                recent_metrics
            )

            current = recent_metrics[-1] if recent_metrics else {}

            return {
                "current": current,
                "averages": {
                    "cpu_percent": round(avg_cpu, 2),
                    "memory_percent": round(avg_memory, 2),
                    "disk_percent": round(avg_disk, 2),
                },
                "data_points": len(recent_metrics),
                "time_range_hours": hours,
            }


class EnhancedHealthChecker:
    """Enhanced health checking with detailed diagnostics."""

    def __init__(self, metrics_collector: MetricsCollector):
        self.startup_time = datetime.now()
        self.metrics_collector = metrics_collector
        self.last_health_check: Optional[datetime] = None
        self.health_cache: Optional[Dict[str, Any]] = None
        self.cache_duration = 30  # Cache health results for 30 seconds

    def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health status with caching."""
        now = datetime.now()

        # Return cached result if recent
        if (
            self.last_health_check
            and self.health_cache
            and (now - self.last_health_check).total_seconds() < self.cache_duration
        ):
            return self.health_cache

        health_data = {
            "status": "healthy",
            "timestamp": now.isoformat(),
            "uptime_seconds": (now - self.startup_time).total_seconds(),
            "version": "1.0.0",
            "environment": "development" if settings.debug else "production",
            "checks": {
                "database": self._check_database(),
                "system": self._check_system_resources(),
                "application": self._check_application_health(),
                "security": self._check_security_status(),
            },
            "metrics": {
                "requests": self.metrics_collector.get_request_metrics(),
                "database": self.metrics_collector.get_database_metrics(),
                "system": self.metrics_collector.get_system_metrics(),
                "security": self.metrics_collector.get_security_metrics(),
            },
        }

        # Determine overall status
        failed_checks = []
        warning_checks = []

        checks_dict = health_data.get("checks", {})
        if isinstance(checks_dict, dict):
            for name, check in checks_dict.items():
                check_dict = check if isinstance(check, dict) else {}
                if check_dict.get("status") == "unhealthy":
                    failed_checks.append(name)
                elif check_dict.get("status") == "warning":
                    warning_checks.append(name)

        if failed_checks:
            health_data["status"] = "unhealthy"
            health_data["failed_checks"] = failed_checks
        elif warning_checks:
            health_data["status"] = "degraded"
            health_data["warning_checks"] = warning_checks

        # Cache the result
        self.health_cache = health_data
        self.last_health_check = now

        return health_data

    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            start_time = time.time()
            db = SessionLocal()

            # Test basic connectivity
            db.execute(text("SELECT 1"))

            # Test table existence
            db.execute(text("SELECT COUNT(*) FROM about LIMIT 1"))

            db.close()

            response_time = (time.time() - start_time) * 1000

            status = "healthy"
            if response_time > 1000:  # > 1 second
                status = "warning"
            elif response_time > 5000:  # > 5 seconds
                status = "unhealthy"

            return {
                "status": status,
                "response_time_ms": round(response_time, 2),
                "connected": True,
                "message": f"Database responding in {response_time:.2f}ms",
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "message": "Database connection failed",
            }

    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Determine status based on resource usage
            status = "healthy"
            warnings = []

            if memory.percent > 85:
                status = "warning"
                warnings.append(f"High memory usage: {memory.percent:.1f}%")
            elif memory.percent > 95:
                status = "unhealthy"
                warnings.append(f"Critical memory usage: {memory.percent:.1f}%")

            if cpu_percent > 80:
                status = "warning"
                warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
            elif cpu_percent > 95:
                status = "unhealthy"
                warnings.append(f"Critical CPU usage: {cpu_percent:.1f}%")

            disk_usage = (disk.used / disk.total) * 100
            if disk_usage > 85:
                status = "warning"
                warnings.append(f"High disk usage: {disk_usage:.1f}%")
            elif disk_usage > 95:
                status = "unhealthy"
                warnings.append(f"Critical disk usage: {disk_usage:.1f}%")

            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk_usage,
                "warnings": warnings,
                "message": (
                    "System resources within normal range"
                    if not warnings
                    else "; ".join(warnings)
                ),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Could not check system resources",
            }

    def _check_application_health(self) -> Dict[str, Any]:
        """Check application-specific health metrics."""
        try:
            request_metrics = self.metrics_collector.get_request_metrics()

            error_rate = request_metrics.get("error_rate", 0)
            total_requests = request_metrics.get("total_requests", 0)

            status = "healthy"
            warnings = []

            if error_rate > 10:
                status = "warning"
                warnings.append(f"High error rate: {error_rate:.1f}%")
            elif error_rate > 25:
                status = "unhealthy"
                warnings.append(f"Critical error rate: {error_rate:.1f}%")

            return {
                "status": status,
                "total_requests": total_requests,
                "error_rate": error_rate,
                "warnings": warnings,
                "message": (
                    "Application functioning normally"
                    if not warnings
                    else "; ".join(warnings)
                ),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Could not check application health",
            }

    def _check_security_status(self) -> Dict[str, Any]:
        """Check security event status."""
        try:
            security_metrics = self.metrics_collector.get_security_metrics()

            total_events = security_metrics.get("total_events", 0)
            severity_breakdown = security_metrics.get("severity_breakdown", {})

            status = "healthy"
            warnings = []

            if severity_breakdown.get("critical", 0) > 0:
                status = "unhealthy"
                warnings.append(
                    f"Critical security events: {severity_breakdown['critical']}"
                )
            elif severity_breakdown.get("high", 0) > 10:
                status = "warning"
                warnings.append(
                    f"High-severity security events: {severity_breakdown['high']}"
                )

            return {
                "status": status,
                "total_events": total_events,
                "severity_breakdown": severity_breakdown,
                "warnings": warnings,
                "message": (
                    "No security concerns" if not warnings else "; ".join(warnings)
                ),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Could not check security status",
            }


# Global instances
metrics_collector = MetricsCollector()
enhanced_health_checker = EnhancedHealthChecker(metrics_collector)
