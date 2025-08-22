"""
Custom exceptions and error handlers for the Portfolio Backend API.
"""

import logging
from typing import Any, Dict

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class PortfolioBaseException(Exception):
    """Base exception for portfolio-specific errors."""

    def __init__(
        self, message: str, error_code: str = None, details: Dict[str, Any] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ContentNotFoundError(PortfolioBaseException):
    """Raised when requested content is not found."""

    def __init__(self, content_type: str, content_id: int):
        self.content_type = content_type
        self.content_id = content_id
        super().__init__(
            message=f"{content_type.title()} with ID {content_id} not found",
            error_code="content_not_found",
            details={"content_type": content_type, "content_id": content_id},
        )


class ValidationError(PortfolioBaseException):
    """Raised when data validation fails."""

    def __init__(self, field: str, value: Any, message: str):
        self.field = field
        self.value = value
        super().__init__(
            message=f"Validation failed for field '{field}': {message}",
            error_code="validation_error",
            details={
                "field": field,
                "value": str(value),
                "validation_message": message,
            },
        )


class AuthenticationError(PortfolioBaseException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, error_code="authentication_error")


class AuthorizationError(PortfolioBaseException):
    """Raised when user lacks required permissions."""

    def __init__(self, required_role: str = None, current_role: str = None):
        message = "Insufficient permissions"
        details = {}
        if required_role:
            message = f"Requires {required_role} role"
            details["required_role"] = required_role
        if current_role:
            details["current_role"] = current_role

        super().__init__(
            message=message, error_code="authorization_error", details=details
        )


class DatabaseError(PortfolioBaseException):
    """Raised when database operations fail."""

    def __init__(self, operation: str, original_error: str = None):
        self.operation = operation
        self.original_error = original_error
        super().__init__(
            message=f"Database error during {operation}",
            error_code="database_error",
            details={"operation": operation, "original_error": original_error},
        )


class ExternalServiceError(PortfolioBaseException):
    """Raised when external service calls fail."""

    def __init__(self, service: str, message: str):
        self.service = service
        super().__init__(
            message=f"External service '{service}' error: {message}",
            error_code="external_service_error",
            details={"service": service},
        )


# Exception handlers
async def portfolio_exception_handler(
    request: Request, exc: PortfolioBaseException
) -> JSONResponse:
    """Handle custom portfolio exceptions."""
    status_code_map = {
        "content_not_found": status.HTTP_404_NOT_FOUND,
        "validation_error": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "authentication_error": status.HTTP_401_UNAUTHORIZED,
        "authorization_error": status.HTTP_403_FORBIDDEN,
        "database_error": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "external_service_error": status.HTTP_503_SERVICE_UNAVAILABLE,
    }

    status_code = status_code_map.get(
        exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    # Log the error
    logger.error(
        f"Portfolio exception: {exc.error_code}",
        extra={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path,
            "timestamp": (
                str(request.state.start_time)
                if hasattr(request.state, "start_time")
                else None
            ),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions with consistent format."""
    logger.warning(
        f"HTTP exception: {exc.status_code}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "details": {"status_code": exc.status_code},
            "path": request.url.path,
            "timestamp": (
                str(request.state.start_time)
                if hasattr(request.state, "start_time")
                else None
            ),
        },
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Handle SQLAlchemy database exceptions."""
    logger.error(
        "Database error occurred",
        extra={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "database_error",
            "message": "An internal database error occurred",
            "details": {"error_type": type(exc).__name__},
            "path": request.url.path,
            "timestamp": (
                str(request.state.start_time)
                if hasattr(request.state, "start_time")
                else None
            ),
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        "Unexpected error occurred",
        extra={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "details": {"error_type": type(exc).__name__},
            "path": request.url.path,
            "timestamp": (
                str(request.state.start_time)
                if hasattr(request.state, "start_time")
                else None
            ),
        },
    )
