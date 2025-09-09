"""
Proxy middleware for handling reverse proxy headers.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to handle proxy headers for HTTPS detection."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        # Handle common proxy headers
        forwarded_proto = request.headers.get("x-forwarded-proto")
        forwarded_host = request.headers.get("x-forwarded-host")
        forwarded_port = request.headers.get("x-forwarded-port")

        # Update request scope for SQLAdmin URL generation
        if forwarded_proto:
            # Force HTTPS scheme detection
            request.scope["scheme"] = forwarded_proto.lower()

        if forwarded_host:
            # Update host information
            request.scope["server"] = (forwarded_host, int(forwarded_port or 443))
            # Ensure headers reflect the forwarded host
            headers = dict(request.scope.get("headers", []))
            headers[b"host"] = forwarded_host.encode()
            request.scope["headers"] = list(headers.items())

        response = await call_next(request)
        return response
