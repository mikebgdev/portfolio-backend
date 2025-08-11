from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from app.config import settings
from app.deps.auth import get_db

# Import monitoring and logging
from app.utils.logging import RequestLoggingMiddleware, app_logger
from app.utils.monitoring import health_checker, metrics_collector

# Import routers
from app.routers import auth, about, skills, projects, experience, education

# Import admin panel
from app.admin import create_admin, register_admin_views

app = FastAPI(
    title="Portfolio Backend API",
    description="A robust, scalable backend API for personal portfolio website",
    version="1.0.0",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware for admin authentication
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Create and mount admin panel
admin = create_admin(app)
register_admin_views(admin)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(about.router, prefix="/api/v1")
app.include_router(skills.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(experience.router, prefix="/api/v1")
app.include_router(education.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Portfolio Backend API", "version": "1.0.0"}

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

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    app_logger.info("Portfolio Backend API shutting down", extra={
        "event": "application_shutdown"
    })