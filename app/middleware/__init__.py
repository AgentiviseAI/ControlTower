"""
Middleware for request/response logging and metrics
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import api_logger
from app.core.metrics import api_metrics


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging API requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Log request
        api_logger.log_request(
            method=request.method,
            path=request.url.path,
            request_id=request_id,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            content_length=request.headers.get("content-length")
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            api_logger.log_response(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                request_id=request_id,
                content_length=response.headers.get("content-length")
            )
            
            # Record metrics
            api_metrics.record_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms
            )
            
            # Add response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            
            return response
            
        except Exception as e:
            # Calculate duration for error case
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            api_logger.log_error(
                method=request.method,
                path=request.url.path,
                error=str(e),
                request_id=request_id,
                duration_ms=duration_ms
            )
            
            # Record error metrics
            api_metrics.record_request(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=duration_ms
            )
            
            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting detailed metrics"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Record request start
        start_time = time.time()
        
        # Increment active requests counter
        api_metrics.metrics_collector.increment_counter("active_requests")
        
        try:
            response = await call_next(request)
            
            # Calculate metrics
            duration_ms = (time.time() - start_time) * 1000
            
            # Record detailed metrics
            self._record_detailed_metrics(request, response, duration_ms)
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Record error metrics
            self._record_error_metrics(request, str(e), duration_ms)
            
            raise
        finally:
            # Decrement active requests counter
            api_metrics.metrics_collector.increment_counter("active_requests", -1)
    
    def _record_detailed_metrics(self, request: Request, response: Response, duration_ms: float):
        """Record detailed metrics for successful requests"""
        tags = {
            "method": request.method,
            "path": self._normalize_path(request.url.path),
            "status_code": str(response.status_code),
            "status_class": f"{response.status_code // 100}xx"
        }
        
        # Request metrics
        api_metrics.metrics_collector.increment_counter("http_requests_total", tags=tags)
        api_metrics.metrics_collector.record_histogram("http_request_duration_ms", duration_ms, tags=tags)
        
        # Response size metrics
        content_length = response.headers.get("content-length")
        if content_length:
            api_metrics.metrics_collector.record_histogram(
                "http_response_size_bytes", 
                float(content_length), 
                tags=tags
            )
    
    def _record_error_metrics(self, request: Request, error: str, duration_ms: float):
        """Record metrics for error requests"""
        tags = {
            "method": request.method,
            "path": self._normalize_path(request.url.path),
            "error_type": type(Exception).__name__
        }
        
        api_metrics.metrics_collector.increment_counter("http_errors_total", tags=tags)
        api_metrics.metrics_collector.record_histogram("http_error_duration_ms", duration_ms, tags=tags)
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path for metrics (replace IDs with placeholders)"""
        import re
        # Replace UUID patterns with {id}
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{id}', path)
        # Replace other numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        return path


class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware with logging"""
    
    def __init__(self, app, allowed_origins: list = None, allowed_methods: list = None, allowed_headers: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = allowed_headers or ["*"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            self._add_cors_headers(response, request)
            return response
        
        # Process normal request
        response = await call_next(request)
        self._add_cors_headers(response, request)
        
        return response
    
    def _add_cors_headers(self, response: Response, request: Request):
        """Add CORS headers to response"""
        origin = request.headers.get("origin")
        
        # For credentials to work, we need to set Access-Control-Allow-Origin to the specific origin
        if origin and (origin in self.allowed_origins or "*" in self.allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        elif "*" in self.allowed_origins and not origin:
            # Only set wildcard if no origin header and wildcard is allowed
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
