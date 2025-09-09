"""Portfolio Backend API main application module."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.admin import create_admin, register_admin_views
from app.config import settings
from app.exceptions import (
    PortfolioBaseException,
    general_exception_handler,
    http_exception_handler,
    portfolio_exception_handler,
    sqlalchemy_exception_handler,
)
from app.middleware.monitoring import (
    DatabaseMetricsMiddleware,
    MetricsMiddleware,
    system_metrics_collector,
)
from app.middleware.performance import (
    CacheMiddleware,
    CompressionMiddleware,
    PerformanceMonitoringMiddleware,
)
from app.middleware.security import (
    InputSanitizationMiddleware,
    RateLimitingMiddleware,
    RequestSizeMiddleware,
    SecurityHeadersMiddleware,
)
from app.routers import (
    about,
    contact,
    education,
    experience,
    projects,
    site_config,
    skills,
)
from app.utils.cache import cache_manager, warm_cache
from app.utils.logging import RequestLoggingMiddleware, app_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    app_logger.info(
        "Portfolio Backend API starting up",
        extra={
            "event": "application_startup",
            "version": "1.0.0",
            "debug_mode": settings.debug,
        },
    )

    # Ensure admin user exists
    from app.utils.admin_setup import create_default_admin

    create_default_admin()

    # Initialize cache connection
    await cache_manager.connect()
    app_logger.info("Cache system initialized")

    # Start system metrics collection
    await system_metrics_collector.start_collection()
    app_logger.info("System metrics collection started")

    # Warm up cache with frequently accessed data (only in production)
    if settings.should_enable_cache:
        await warm_cache()
        app_logger.info("Cache warmed up")
    else:
        app_logger.info("Cache warming skipped for development environment")

    yield

    # Shutdown
    app_logger.info(
        "Portfolio Backend API shutting down", extra={"event": "application_shutdown"}
    )

    # Stop system metrics collection
    await system_metrics_collector.stop_collection()
    app_logger.info("System metrics collection stopped")


app = FastAPI(
    title="Portfolio Backend API",
    description="A robust, scalable backend API for personal portfolio website",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# Add session middleware for admin authentication (before CORS)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Configure CORS with configurable origins (MUST be early in middleware stack)
effective_origins = settings.effective_cors_origins
app_logger.info(
    f"CORS configured with origins: {effective_origins}, "
    f"credentials: {settings.cors_allow_credentials}"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=effective_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add security middleware (after CORS to avoid conflicts)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RateLimitingMiddleware, requests_per_minute=settings.rate_limit_per_minute
)
app.add_middleware(InputSanitizationMiddleware)
app.add_middleware(RequestSizeMiddleware, max_size=settings.max_upload_size)

# Add performance middleware (cache before compression to avoid encoding issues)
if settings.should_enable_cache:
    app.add_middleware(CacheMiddleware, default_ttl=settings.cache_ttl_content)
    app_logger.info("HTTP cache enabled for production environment")
else:
    app_logger.info(f"HTTP cache disabled for {settings.environment} environment")

if settings.enable_compression:
    app.add_middleware(CompressionMiddleware, minimum_size=1000)

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

# Mount static files for uploads
uploads_dir = os.path.join(os.getcwd(), settings.uploads_path)
if os.path.exists(uploads_dir):
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
    app_logger.info(f"Static files mounted at /uploads -> {uploads_dir}")
else:
    app_logger.warning(f"Uploads directory not found: {uploads_dir}")

# Mount static files for templates (if they exist) - helps with Coolify deployment
templates_static_dir = os.path.join(os.getcwd(), "templates", "static")
if os.path.exists(templates_static_dir):
    app.mount("/static", StaticFiles(directory=templates_static_dir), name="static")
    app_logger.info(
        f"Template static files mounted at /static -> {templates_static_dir}"
    )


@app.get("/admin", include_in_schema=False)
async def admin_auth_check(request: Request):
    """Redirect to admin login if not authenticated, otherwise to admin panel."""
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/admin/login", status_code=302)
    return RedirectResponse(url="/admin/", status_code=302)


@app.get("/api/v1/debug/cors", include_in_schema=False)
async def debug_cors():
    """Debug endpoint to check CORS configuration."""
    return {
        "cors_origins": settings.effective_cors_origins,
        "cors_allow_credentials": settings.cors_allow_credentials,
        "environment": settings.environment,
        "debug": settings.debug,
    }
