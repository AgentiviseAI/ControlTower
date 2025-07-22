"""
Metrics middleware for collecting application metrics
"""
import time
import psutil
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger
from app.core.metrics import metrics_collector

logger = get_logger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting HTTP and system metrics"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Record request start time
        start_time = time.time()
        
        # Increment request counter
        metrics_collector.increment_counter(
            "http_requests_total",
            labels={"method": request.method, "endpoint": request.url.path}
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record success metrics
            duration = time.time() - start_time
            metrics_collector.record_histogram(
                "http_request_duration_seconds",
                duration,
                labels={
                    "method": request.method,
                    "endpoint": request.url.path,
                    "status_code": str(response.status_code)
                }
            )
            
            # Record response size if available
            if "content-length" in response.headers:
                size = int(response.headers["content-length"])
                metrics_collector.record_histogram(
                    "http_response_size_bytes",
                    size,
                    labels={"method": request.method, "endpoint": request.url.path}
                )
            
            return response
            
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            metrics_collector.increment_counter(
                "http_requests_errors_total",
                labels={
                    "method": request.method,
                    "endpoint": request.url.path,
                    "error_type": type(e).__name__
                }
            )
            metrics_collector.record_histogram(
                "http_request_duration_seconds",
                duration,
                labels={
                    "method": request.method,
                    "endpoint": request.url.path,
                    "status_code": "500"
                }
            )
            
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                    "duration_seconds": round(duration, 4)
                }
            )
            
            raise
