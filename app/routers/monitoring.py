"""
Monitoring and metrics endpoints for Portfolio Backend API.
"""
from fastapi import APIRouter, Query
from typing import Optional
from app.utils.enhanced_monitoring import metrics_collector, enhanced_health_checker
from app.utils.monitoring import health_checker, metrics_collector as basic_metrics
from app.utils.cache import cache_manager

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/health")
async def get_basic_health():
    """Get basic health status (public endpoint)."""
    return health_checker.get_application_health()

@router.get("/health/detailed")
async def get_detailed_health(
):
    """Get comprehensive health status with detailed metrics (admin only)."""
    return enhanced_health_checker.get_comprehensive_health()

@router.get("/metrics")
async def get_basic_metrics():
    """Get basic application metrics (public endpoint)."""
    return basic_metrics.get_metrics()

@router.get("/metrics/requests")
async def get_request_metrics(
):
    """Get detailed request metrics (admin only)."""
    return metrics_collector.get_request_metrics()

@router.get("/metrics/system")
async def get_system_metrics(
    hours: int = Query(default=1, ge=1, le=24, description="Hours of metrics to retrieve")
):
    """Get system resource metrics for specified time period (admin only)."""
    return metrics_collector.get_system_metrics(hours=hours)

@router.get("/metrics/database")
async def get_database_metrics(
):
    """Get database performance metrics (admin only)."""
    return metrics_collector.get_database_metrics()

@router.get("/metrics/security")
async def get_security_metrics(
):
    """Get security event metrics (admin only)."""
    return metrics_collector.get_security_metrics()

@router.get("/metrics/dashboard")
async def get_dashboard_metrics(
    hours: int = Query(default=1, ge=1, le=24, description="Hours of metrics for dashboard")
):
    """Get comprehensive dashboard metrics (admin only)."""
    
    # Collect all metrics for dashboard
    dashboard_data = {
        "overview": {
            "health": enhanced_health_checker.get_comprehensive_health(),
            "uptime_seconds": (enhanced_health_checker.startup_time - enhanced_health_checker.startup_time).total_seconds()
        },
        "requests": metrics_collector.get_request_metrics(),
        "system": metrics_collector.get_system_metrics(hours=hours),
        "database": metrics_collector.get_database_metrics(),
        "security": metrics_collector.get_security_metrics(),
        "time_range_hours": hours
    }
    
    return dashboard_data

@router.get("/alerts")
async def get_active_alerts(
):
    """Get active system alerts based on current metrics (admin only)."""
    
    health = enhanced_health_checker.get_comprehensive_health()
    alerts = []
    
    # Check for failed health checks
    if health["status"] != "healthy":
        failed_checks = health.get("failed_checks", [])
        warning_checks = health.get("warning_checks", [])
        
        for check in failed_checks:
            check_data = health["checks"][check]
            alerts.append({
                "type": "health_check_failed",
                "severity": "critical",
                "component": check,
                "message": check_data.get("message", f"{check} health check failed"),
                "timestamp": health["timestamp"]
            })
        
        for check in warning_checks:
            check_data = health["checks"][check]
            alerts.append({
                "type": "health_check_warning",
                "severity": "warning",
                "component": check,
                "message": check_data.get("message", f"{check} health check warning"),
                "timestamp": health["timestamp"]
            })
    
    # Check for high error rates
    request_metrics = metrics_collector.get_request_metrics()
    if request_metrics["error_rate"] > 10:
        alerts.append({
            "type": "high_error_rate",
            "severity": "critical" if request_metrics["error_rate"] > 25 else "warning",
            "component": "api",
            "message": f"High error rate: {request_metrics['error_rate']:.1f}%",
            "details": {"error_rate": request_metrics["error_rate"]}
        })
    
    # Check for security events
    security_metrics = metrics_collector.get_security_metrics()
    severity_breakdown = security_metrics.get("severity_breakdown", {})
    
    if severity_breakdown.get("critical", 0) > 0:
        alerts.append({
            "type": "critical_security_events",
            "severity": "critical",
            "component": "security",
            "message": f"Critical security events detected: {severity_breakdown['critical']}",
            "details": severity_breakdown
        })
    
    return {
        "total_alerts": len(alerts),
        "alerts": alerts,
        "severity_counts": {
            "critical": len([a for a in alerts if a["severity"] == "critical"]),
            "warning": len([a for a in alerts if a["severity"] == "warning"]),
            "info": len([a for a in alerts if a["severity"] == "info"])
        }
    }

@router.get("/metrics/cache")
async def get_cache_metrics(
):
    """Get cache performance metrics (admin only)."""
    return cache_manager.get_stats()

@router.get("/stats/summary")
async def get_stats_summary():
    """Get high-level stats summary (public endpoint)."""
    
    request_metrics = metrics_collector.get_request_metrics()
    health = enhanced_health_checker.get_comprehensive_health()
    cache_stats = cache_manager.get_stats()
    
    return {
        "status": health["status"],
        "uptime_hours": round(health["uptime_seconds"] / 3600, 1),
        "total_requests": request_metrics.get("total_requests", 0),
        "error_rate": round(request_metrics.get("error_rate", 0), 1),
        "active_endpoints": len(request_metrics.get("endpoints", {})),
        "cache_hit_rate": cache_stats.get("hit_rate_percent", 0),
        "version": health.get("version", "1.0.0"),
        "environment": health.get("environment", "development")
    }