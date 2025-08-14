"""
Monitoring middleware for automated metrics collection.
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.utils.enhanced_monitoring import metrics_collector
from app.utils.logging import get_logger

logger = get_logger("portfolio.monitoring.middleware")


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically collect request metrics."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract user info if available
        user_id = None
        if hasattr(request.state, 'user') and request.state.user:
            user_id = getattr(request.state.user, 'id', None)
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Record metrics
            metrics_collector.record_request(
                method=request.method,
                path=self._normalize_path(request.url.path),
                status_code=response.status_code,
                response_time=response_time,
                user_id=user_id
            )
            
            # Add metrics headers
            response.headers["X-Response-Time"] = f"{response_time:.3f}s"
            
            return response
            
        except Exception as e:
            # Record error metrics
            response_time = time.time() - start_time
            metrics_collector.record_request(
                method=request.method,
                path=self._normalize_path(request.url.path),
                status_code=500,
                response_time=response_time,
                user_id=user_id
            )
            
            # Record security event if suspicious
            if self._is_suspicious_error(e, request):
                metrics_collector.record_security_event(
                    event_type="application_error",
                    severity="medium",
                    details={
                        "error": str(e),
                        "path": request.url.path,
                        "method": request.method,
                        "client_ip": request.client.host if request.client else "unknown",
                        "user_agent": request.headers.get("user-agent", "unknown")
                    }
                )
            
            raise
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path for consistent metrics (replace IDs with placeholders)."""
        import re
        # Replace numeric IDs with placeholder
        path = re.sub(r'/\d+(?=/|$)', '/{id}', path)
        # Replace UUID patterns
        path = re.sub(r'/[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}(?=/|$)', '/{uuid}', path)
        return path
    
    def _is_suspicious_error(self, error: Exception, request: Request) -> bool:
        """Determine if an error might be suspicious/security-related."""
        error_str = str(error).lower()
        suspicious_patterns = [
            'sql', 'injection', 'script', 'xss', 'csrf',
            'unauthorized', 'forbidden', 'permission'
        ]
        
        # Check if error contains suspicious patterns
        if any(pattern in error_str for pattern in suspicious_patterns):
            return True
        
        # Check if request contains suspicious elements
        path = request.url.path.lower()
        if any(pattern in path for pattern in ['admin', 'config', '.env', 'password']):
            return True
        
        return False


class DatabaseMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor database operations."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Track database queries for this request
        request.state.db_query_start = time.time()
        request.state.db_queries = []
        
        response = await call_next(request)
        
        # Record database metrics if any queries were made
        if hasattr(request.state, 'db_queries') and request.state.db_queries:
            total_db_time = sum(query['duration'] for query in request.state.db_queries)
            metrics_collector.record_database_operation(
                operation=f"{request.method} {request.url.path}",
                duration=total_db_time,
                success=response.status_code < 400
            )
        
        return response


class SystemMetricsCollector:
    """Background collector for system metrics."""
    
    def __init__(self):
        self.is_running = False
        self._task = None
    
    async def start_collection(self):
        """Start collecting system metrics in background."""
        if self.is_running:
            return
        
        self.is_running = True
        import asyncio
        
        async def collect_loop():
            while self.is_running:
                try:
                    metrics_collector.record_system_metrics()
                    await asyncio.sleep(300)  # Collect every 5 minutes
                except Exception as e:
                    logger.error(f"Error collecting system metrics: {str(e)}")
                    await asyncio.sleep(60)  # Retry in 1 minute on error
        
        self._task = asyncio.create_task(collect_loop())
    
    async def stop_collection(self):
        """Stop collecting system metrics."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


# Global instance
system_metrics_collector = SystemMetricsCollector()