from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app.config import settings

# Import exception handlers
from app.exceptions import (
    PortfolioBaseException,
    portfolio_exception_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)

# Import monitoring and logging
from app.utils.logging import RequestLoggingMiddleware, app_logger
from app.utils.monitoring import health_checker, metrics_collector

# Import security middleware
from app.middleware.security import (
    SecurityHeadersMiddleware,
    RateLimitingMiddleware,
    InputSanitizationMiddleware,
    RequestSizeMiddleware
)

# Import monitoring middleware
from app.middleware.monitoring import (
    MetricsMiddleware,
    DatabaseMetricsMiddleware,
    system_metrics_collector
)

# Import performance middleware
from app.middleware.performance import (
    CacheMiddleware,
    CompressionMiddleware,
    PerformanceMonitoringMiddleware
)

# Import cache utilities
from app.utils.cache import cache_manager, warm_cache

# Import routers
from app.routers import about, skills, projects, experience, education, contact, site_config, monitoring

# Import admin panel
from app.admin import create_admin, register_admin_views

app = FastAPI(
    title="Portfolio Backend API",
    description="A robust, scalable backend API for personal portfolio website",
    version="1.0.0",
    debug=settings.debug
)

# Configure CORS - Permissive for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware for admin authentication
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Add security middleware (order matters - add these first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitingMiddleware, requests_per_minute=settings.rate_limit_per_minute)
app.add_middleware(InputSanitizationMiddleware)
app.add_middleware(RequestSizeMiddleware, max_size=settings.max_upload_size)

# Add performance middleware
if settings.enable_compression:
    app.add_middleware(CompressionMiddleware, minimum_size=1000)
if settings.enable_http_cache:
    app.add_middleware(CacheMiddleware, default_ttl=settings.cache_ttl_content)
app.add_middleware(PerformanceMonitoringMiddleware, slow_request_threshold=1.0)

# Add monitoring middleware
app.add_middleware(MetricsMiddleware)
app.add_middleware(DatabaseMetricsMiddleware)


# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)


# Register exception handlers
app.add_exception_handler(PortfolioBaseException, portfolio_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Create and mount admin panel
admin = create_admin(app)
register_admin_views(admin)

# Include routers (public API - no authentication needed)
app.include_router(site_config.router, prefix="/api/v1")
app.include_router(about.router, prefix="/api/v1")
app.include_router(skills.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(experience.router, prefix="/api/v1")
app.include_router(education.router, prefix="/api/v1")
app.include_router(contact.router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")

# Admin redirect route
from starlette.responses import RedirectResponse
from starlette.requests import Request

@app.get("/")
async def root():
    return {"message": "Portfolio Backend API", "version": "1.0.0"}

@app.get("/admin")
async def admin_auth_check(request: Request):
    """Redirect to admin login if not authenticated, otherwise to admin panel."""
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/admin/login", status_code=302)
    return RedirectResponse(url="/admin/", status_code=302)

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    return health_checker.get_application_health()

@app.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    return metrics_collector.get_metrics()

@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    app_logger.info("Portfolio Backend API starting up", extra={
        "event": "application_startup", 
        "version": "1.0.0",
        "debug_mode": settings.debug
    })
    
    # Ensure admin user exists
    from app.utils.admin_setup import create_default_admin
    create_default_admin()
    
    # Initialize cache connection
    await cache_manager.connect(settings.redis_url)
    app_logger.info("Cache system initialized")
    
    # Start system metrics collection
    await system_metrics_collector.start_collection()
    app_logger.info("System metrics collection started")
    
    # Warm up cache with frequently accessed data
    await warm_cache()
    app_logger.info("Cache warmed up")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    app_logger.info("Portfolio Backend API shutting down", extra={
        "event": "application_shutdown"
    })
    
    # Stop system metrics collection
    await system_metrics_collector.stop_collection()
    app_logger.info("System metrics collection stopped")