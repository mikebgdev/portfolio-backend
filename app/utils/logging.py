import logging
import sys
from typing import Any, Dict
from datetime import datetime
import json

from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time

from app.config import settings


class StructuredLogger:
    """Structured logging utility for the application."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self._setup_logger()
    
    def _setup_logger(self):
        """Setup structured logging configuration."""
        formatter = StructuredFormatter()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Set log level based on environment
        if settings.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        """Log info message with structured data."""
        self.logger.info(message, extra=extra or {})
    
    def error(self, message: str, extra: Dict[str, Any] = None, exc_info: bool = False):
        """Log error message with structured data."""
        self.logger.error(message, extra=extra or {}, exc_info=exc_info)
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Log warning message with structured data."""
        self.logger.warning(message, extra=extra or {})
    
    def debug(self, message: str, extra: Dict[str, Any] = None):
        """Log debug message with structured data."""
        self.logger.debug(message, extra=extra or {})


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, "extra") and record.extra:
            log_data.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = StructuredLogger("portfolio.requests")
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response details."""
        start_time = time.time()
        
        # Extract request details
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        # Log request
        self.logger.info("Request started", extra={
            "event": "request_started",
            "request": request_data
        })
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Extract response details
            response_data = {
                "status_code": response.status_code,
                "response_time_ms": round(response_time * 1000, 2),
                "content_length": response.headers.get("content-length"),
                "content_type": response.headers.get("content-type"),
            }
            
            # Log response
            log_level = "error" if response.status_code >= 400 else "info"
            getattr(self.logger, log_level)("Request completed", extra={
                "event": "request_completed",
                "request": request_data,
                "response": response_data
            })
            
            return response
            
        except Exception as e:
            # Calculate response time for errors
            response_time = time.time() - start_time
            
            # Log error
            self.logger.error("Request failed", extra={
                "event": "request_failed",
                "request": request_data,
                "error": str(e),
                "response_time_ms": round(response_time * 1000, 2)
            }, exc_info=True)
            
            raise


class DatabaseLoggingHandler:
    """Handler for logging database operations."""
    
    def __init__(self):
        self.logger = StructuredLogger("portfolio.database")
    
    def log_query(self, query: str, params: Dict[str, Any] = None, execution_time: float = None):
        """Log database query execution."""
        extra_data = {
            "event": "database_query",
            "query": query,
            "params": params or {},
        }
        
        if execution_time is not None:
            extra_data["execution_time_ms"] = round(execution_time * 1000, 2)
        
        self.logger.debug("Database query executed", extra=extra_data)
    
    def log_transaction(self, operation: str, success: bool, execution_time: float = None):
        """Log database transaction."""
        extra_data = {
            "event": "database_transaction",
            "operation": operation,
            "success": success,
        }
        
        if execution_time is not None:
            extra_data["execution_time_ms"] = round(execution_time * 1000, 2)
        
        log_level = "info" if success else "error"
        getattr(self.logger, log_level)("Database transaction", extra=extra_data)


class SecurityLogger:
    """Logger for security-related events."""
    
    def __init__(self):
        self.logger = StructuredLogger("portfolio.security")
    
    def log_auth_attempt(self, email: str, success: bool, ip_address: str = None, user_agent: str = None):
        """Log authentication attempt."""
        extra_data = {
            "event": "authentication_attempt",
            "email": email,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }
        
        log_level = "info" if success else "warning"
        message = "Authentication successful" if success else "Authentication failed"
        
        getattr(self.logger, log_level)(message, extra=extra_data)
    
    def log_access_denied(self, user_id: int, resource: str, ip_address: str = None):
        """Log access denied events."""
        self.logger.warning("Access denied", extra={
            "event": "access_denied",
            "user_id": user_id,
            "resource": resource,
            "ip_address": ip_address,
        })
    
    def log_token_validation(self, token_valid: bool, error: str = None, ip_address: str = None):
        """Log JWT token validation."""
        extra_data = {
            "event": "token_validation",
            "valid": token_valid,
            "ip_address": ip_address,
        }
        
        if error:
            extra_data["error"] = error
        
        log_level = "debug" if token_valid else "warning"
        message = "Token validation successful" if token_valid else "Token validation failed"
        
        getattr(self.logger, log_level)(message, extra=extra_data)


# Global logger instances
app_logger = StructuredLogger("portfolio.app")
db_logger = DatabaseLoggingHandler()
security_logger = SecurityLogger()


# Utility functions
def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


def log_api_error(endpoint: str, error: Exception, user_id: int = None, request_data: Dict[str, Any] = None):
    """Log API errors with context."""
    extra_data = {
        "event": "api_error",
        "endpoint": endpoint,
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    if user_id:
        extra_data["user_id"] = user_id
    
    if request_data:
        extra_data["request_data"] = request_data
    
    app_logger.error("API error occurred", extra=extra_data, exc_info=True)