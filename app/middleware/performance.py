"""
Performance middleware for Portfolio Backend API.
"""

import gzip
import time
from typing import List

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.cache import cache_manager
from app.utils.logging import get_logger

logger = get_logger("portfolio.performance")


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for HTTP response caching."""

    def __init__(
        self, app: ASGIApp, cacheable_paths: List[str] = None, default_ttl: int = 300
    ):
        super().__init__(app)
        self.cacheable_paths = cacheable_paths or [
            "/api/v1/about",
            "/api/v1/skills",
            "/api/v1/projects",
            "/api/v1/experience",
            "/api/v1/education",
            "/api/v1/contact",
        ]
        self.default_ttl = default_ttl

    async def dispatch(self, request: Request, call_next):
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        path = request.url.path

        # Check if path should be cached
        if not any(
            path.startswith(cacheable_path) for cacheable_path in self.cacheable_paths
        ):
            return await call_next(request)

        # Generate cache key including query parameters
        query_string = str(request.query_params)
        cache_key = f"http_cache:{path}:{query_string}"

        # Try to get from cache
        try:
            cached_response = await cache_manager.get(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for {path}")

                # Reconstruct response
                return JSONResponse(
                    content=cached_response["content"],
                    status_code=cached_response["status_code"],
                    headers={
                        **cached_response["headers"],
                        "X-Cache": "HIT",
                        "X-Cache-Key": cache_key[:16]
                        + "...",  # Truncated key for debugging
                    },
                )
        except Exception as e:
            logger.error(f"Cache retrieval error: {str(e)}")

        # Cache miss, execute request
        response = await call_next(request)

        # Only cache successful responses
        if response.status_code == 200:
            try:
                # Read response body
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                # Parse JSON response
                import json

                content = json.loads(response_body.decode())

                # Prepare cache entry
                cache_entry = {
                    "content": content,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                }

                # Cache the response
                await cache_manager.set(cache_key, cache_entry, self.default_ttl)

                # Create new response with cache headers
                new_response = JSONResponse(
                    content=content,
                    status_code=response.status_code,
                    headers={
                        **dict(response.headers),
                        "X-Cache": "MISS",
                        "Cache-Control": f"public, max-age={self.default_ttl}",
                        "X-Cache-Key": cache_key[:16] + "...",
                    },
                )

                logger.debug(f"Cached response for {path}")
                return new_response

            except Exception as e:
                logger.error(f"Cache storage error: {str(e)}")

        # Add cache miss header
        response.headers["X-Cache"] = "SKIP"
        return response


class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware for response compression."""

    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 1000,
        compressible_types: List[str] = None,
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compressible_types = compressible_types or [
            "application/json",
            "application/javascript",
            "text/html",
            "text/css",
            "text/plain",
            "text/xml",
        ]

    async def dispatch(self, request: Request, call_next):
        # Check if client accepts gzip encoding
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return await call_next(request)

        response = await call_next(request)

        # Check if response should be compressed
        if not self._should_compress(response):
            return response

        try:
            # Read response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # Check minimum size
            if len(response_body) < self.minimum_size:
                # Reconstruct response without compression
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

            # Compress the body
            compressed_body = gzip.compress(response_body)
            compression_ratio = len(response_body) / len(compressed_body)

            # Only use compression if it provides significant savings
            if compression_ratio < 1.1:  # Less than 10% savings
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

            # Create compressed response
            headers = dict(response.headers)
            headers["content-encoding"] = "gzip"
            headers["content-length"] = str(len(compressed_body))
            headers["x-compression-ratio"] = f"{compression_ratio:.2f}"

            logger.debug(
                f"Compressed response: {len(response_body)} -> {len(compressed_body)} bytes "
                f"(ratio: {compression_ratio:.2f})"
            )

            return Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type,
            )

        except Exception as e:
            logger.error(f"Compression error: {str(e)}")
            return response

    def _should_compress(self, response: Response) -> bool:
        """Check if response should be compressed."""
        # Don't compress if already compressed
        if response.headers.get("content-encoding"):
            return False

        # Don't compress if not successful
        if response.status_code != 200:
            return False

        # Check content type
        content_type = response.headers.get("content-type", "").split(";")[0].lower()
        return content_type in self.compressible_types


class RateLimitEnhancedMiddleware(BaseHTTPMiddleware):
    """Enhanced rate limiting with sliding window."""

    def __init__(
        self, app: ASGIApp, requests_per_minute: int = 60, burst_requests: int = 10
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_requests = burst_requests
        self.window_size = 60  # 1 minute

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Check sliding window rate limit
        rate_limit_key = f"rate_limit:{client_ip}"

        try:
            # Get current request timestamps
            timestamps_json = await cache_manager.get(rate_limit_key)
            if timestamps_json:
                timestamps = timestamps_json
            else:
                timestamps = []

            # Remove old timestamps
            cutoff_time = current_time - self.window_size
            timestamps = [ts for ts in timestamps if ts > cutoff_time]

            # Check if within rate limit
            if len(timestamps) >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded for IP {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "rate_limit_exceeded",
                        "message": (
                            f"Rate limit of {self.requests_per_minute} requests per minute exceeded"
                        ),
                        "retry_after": 60,
                    },
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": str(self.requests_per_minute),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(current_time + 60)),
                    },
                )

            # Add current timestamp
            timestamps.append(current_time)

            # Store updated timestamps
            await cache_manager.set(rate_limit_key, timestamps, self.window_size)

            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(
                self.requests_per_minute - len(timestamps)
            )
            response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))

            return response

        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Fallback to allowing the request
            return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded IP
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring performance metrics."""

    def __init__(self, app: ASGIApp, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        response_time = time.time() - start_time

        # Add performance headers
        response.headers["X-Response-Time"] = f"{response_time:.3f}s"

        # Log slow requests
        if response_time > self.slow_request_threshold:
            logger.warning(
                "Slow request detected",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "query_params": dict(request.query_params),
                },
            )

        # Log performance metrics
        logger.debug(
            "Request performance",
            extra={
                "path": request.url.path,
                "method": request.method,
                "response_time": response_time,
                "status_code": response.status_code,
            },
        )

        return response
