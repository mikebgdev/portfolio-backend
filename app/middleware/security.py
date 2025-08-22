"""
Security middleware for the Portfolio Backend API.
"""

import re
import time
from typing import List

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings
from app.utils.logging import security_logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # More lenient headers for admin and docs
        if path.startswith(("/admin", "/docs", "/redoc", "/openapi.json")):
            response.headers["X-Frame-Options"] = "SAMEORIGIN"  # Allow iframe for admin
            # Very permissive CSP for API docs (FastAPI needs external CDNs)
            if path.startswith("/docs") or path.startswith("/redoc"):
                # Disable CSP for docs - FastAPI docs need external resources
                response.headers["Content-Security-Policy"] = ""
            else:
                # Less restrictive CSP for admin
                csp_directives = [
                    "default-src 'self'",
                    (
                        "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                        "https://cdn.jsdelivr.net https://unpkg.com"
                    ),
                    (
                        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net "
                        "https://unpkg.com https://fonts.googleapis.com"
                    ),
                    "img-src 'self' data: https: blob:",
                    "font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net",
                    "connect-src 'self'",
                    "frame-ancestors 'self'",
                ]
                response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        else:
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Permissions-Policy"] = (
                "geolocation=(), microphone=(), camera=()"
            )
            # Stricter CSP for API endpoints
            csp_directives = [
                "default-src 'self'",
                "script-src 'self'",
                "style-src 'self'",
                "img-src 'self' data: https:",
                "font-src 'self'",
                "connect-src 'self'",
                "frame-ancestors 'none'",
            ]

        # Add HSTS header in production
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # Set CSP only if not already set above
        if "Content-Security-Policy" not in response.headers:
            response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware."""

    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_history = {}  # In production, use Redis
        self.window_size = 60  # 1 minute window

        # Paths with more lenient rate limits
        self.lenient_paths = ["/admin", "/docs", "/redoc", "/openapi.json"]
        self.lenient_limit = requests_per_minute * 3  # 3x more requests for admin/docs

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Clean old entries
        self._clean_old_entries(current_time)

        # Determine rate limit based on path
        path = request.url.path
        is_lenient_path = any(
            path.startswith(lenient_path) for lenient_path in self.lenient_paths
        )
        current_limit = (
            self.lenient_limit if is_lenient_path else self.requests_per_minute
        )

        # Check rate limit
        if self._is_rate_limited(client_ip, current_time, current_limit):
            security_logger.logger.warning(
                "Rate limit exceeded",
                extra={
                    "event": "rate_limit_exceeded",
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "method": request.method,
                    "limit_used": current_limit,
                },
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Too many requests. Limit: {current_limit} requests per minute",
                    "retry_after": 60,
                },
                headers={"Retry-After": "60"},
            )

        # Record request
        self._record_request(client_ip, current_time)

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address, considering proxy headers."""
        # Check for X-Forwarded-For header (from proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"

    def _clean_old_entries(self, current_time: float):
        """Remove entries older than the window size."""
        cutoff_time = current_time - self.window_size
        for ip in list(self.requests_history.keys()):
            self.requests_history[ip] = [
                timestamp
                for timestamp in self.requests_history[ip]
                if timestamp > cutoff_time
            ]
            if not self.requests_history[ip]:
                del self.requests_history[ip]

    def _is_rate_limited(
        self, client_ip: str, current_time: float, limit: int = None
    ) -> bool:
        """Check if client has exceeded rate limit."""
        if client_ip not in self.requests_history:
            return False

        used_limit = limit or self.requests_per_minute
        return len(self.requests_history[client_ip]) >= used_limit

    def _record_request(self, client_ip: str, current_time: float):
        """Record request timestamp for client."""
        if client_ip not in self.requests_history:
            self.requests_history[client_ip] = []

        self.requests_history[client_ip].append(current_time)


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Middleware for basic input sanitization and validation."""

    # Patterns that might indicate malicious input
    SUSPICIOUS_PATTERNS = [
        re.compile(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", re.IGNORECASE),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),
        re.compile(r"<iframe\b", re.IGNORECASE),
        re.compile(r"<object\b", re.IGNORECASE),
        re.compile(r"<embed\b", re.IGNORECASE),
        re.compile(r"vbscript:", re.IGNORECASE),
        re.compile(r"data:text/html", re.IGNORECASE),
    ]

    # SQL injection patterns (more conservative)
    SQL_INJECTION_PATTERNS = [
        re.compile(r"\b(union\s+select|drop\s+table|delete\s+from)\b", re.IGNORECASE),
        re.compile(r";\s*(drop|delete|insert|update)\b", re.IGNORECASE),
        re.compile(r"/\*.*?\*/", re.IGNORECASE),
    ]

    # Paths to exclude from sanitization (admin panel, docs, etc.)
    EXCLUDED_PATHS = [
        "/admin",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/static",
        "/_starlette",  # Starlette internal routes
    ]

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Skip sanitization for excluded paths
        path = request.url.path
        if any(path.startswith(excluded_path) for excluded_path in self.EXCLUDED_PATHS):
            return await call_next(request)

        # Check query parameters
        if await self._check_query_params(request):
            return self._create_security_error_response(
                request, "Suspicious query parameters detected"
            )

        # Check headers (basic) - only for API endpoints
        if path.startswith("/api/") and self._check_headers(request):
            return self._create_security_error_response(
                request, "Suspicious headers detected"
            )

        return await call_next(request)

    async def _check_query_params(self, request: Request) -> bool:
        """Check query parameters for suspicious content."""
        for key, value in request.query_params.items():
            if self._is_suspicious_input(value):
                security_logger.logger.warning(
                    "Suspicious query parameter detected",
                    extra={
                        "event": "suspicious_input",
                        "parameter": key,
                        "value": value[:100],  # Log first 100 chars only
                        "client_ip": (
                            request.client.host if request.client else "unknown"
                        ),
                        "path": request.url.path,
                    },
                )
                return True
        return False

    def _check_headers(self, request: Request) -> bool:
        """Check headers for suspicious content."""
        # Check User-Agent for obvious attacks
        user_agent = request.headers.get("user-agent", "")
        if self._is_suspicious_input(user_agent):
            security_logger.logger.warning(
                "Suspicious User-Agent detected",
                extra={
                    "event": "suspicious_user_agent",
                    "user_agent": user_agent[:200],
                    "client_ip": request.client.host if request.client else "unknown",
                    "path": request.url.path,
                },
            )
            return True

        return False

    def _is_suspicious_input(self, value: str) -> bool:
        """Check if input value contains suspicious patterns."""
        if not value:
            return False

        # Check for XSS patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.search(value):
                return True

        # Check for SQL injection patterns (basic)
        for pattern in self.SQL_INJECTION_PATTERNS:
            if pattern.search(value):
                return True

        return False

    def _create_security_error_response(
        self, request: Request, message: str
    ) -> JSONResponse:
        """Create standardized security error response."""
        return JSONResponse(
            status_code=400,
            content={
                "error": "security_violation",
                "message": message,
                "path": request.url.path,
                "timestamp": time.time(),
            },
        )


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request body size."""

    def __init__(self, app: ASGIApp, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    security_logger.logger.warning(
                        "Request size limit exceeded",
                        extra={
                            "event": "request_size_exceeded",
                            "content_length": size,
                            "max_size": self.max_size,
                            "client_ip": (
                                request.client.host if request.client else "unknown"
                            ),
                            "path": request.url.path,
                        },
                    )

                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "request_too_large",
                            "message": (
                                f"Request body too large. Maximum size: {self.max_size} bytes"
                            ),
                            "max_size": self.max_size,
                        },
                    )
            except ValueError:
                # Invalid Content-Length header
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "invalid_content_length",
                        "message": "Invalid Content-Length header",
                    },
                )

        return await call_next(request)


# Utility functions
def is_safe_redirect_url(url: str, allowed_hosts: List[str] = None) -> bool:
    """Check if redirect URL is safe (prevents open redirect attacks)."""
    if not url:
        return False

    # Allow relative URLs
    if url.startswith("/") and not url.startswith("//"):
        return True

    # Check against allowed hosts
    if allowed_hosts:
        for host in allowed_hosts:
            if url.startswith(f"https://{host}") or url.startswith(f"http://{host}"):
                return True

    return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    if not filename:
        return "unnamed"

    # Remove path traversal attempts
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")

    # Remove or replace dangerous characters
    dangerous_chars = ["<", ">", ":", '"', "|", "?", "*", "\x00"]
    for char in dangerous_chars:
        filename = filename.replace(char, "_")

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:250] + "." + ext if ext else name[:255]

    return filename or "unnamed"
