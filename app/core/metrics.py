"""
Metrics collection and monitoring
"""
import time
import psutil
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading
import json
from pathlib import Path

from .config import settings
from .logging import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Collects and manages application metrics"""
    
    def __init__(self):
        self._metrics = defaultdict(list)
        self._counters = defaultdict(int)
        self._gauges = defaultdict(float)
        self._histograms = defaultdict(lambda: deque(maxlen=1000))
        self._lock = threading.Lock()
        self._start_time = time.time()
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        with self._lock:
            key = self._build_key(name, tags)
            self._counters[key] += value
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        with self._lock:
            key = self._build_key(name, tags)
            self._gauges[key] = value
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram value"""
        with self._lock:
            key = self._build_key(name, tags)
            self._histograms[key].append({
                'value': value,
                'timestamp': time.time()
            })
    
    def record_timing(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """Record timing metric"""
        self.record_histogram(f"{name}_duration_ms", duration_ms, tags)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        with self._lock:
            uptime = time.time() - self._start_time
            
            # System metrics
            system_metrics = self._get_system_metrics()
            
            # Application metrics
            app_metrics = {
                'uptime_seconds': uptime,
                'counters': dict(self._counters),
                'gauges': dict(self._gauges),
                'histograms': self._summarize_histograms()
            }
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'system': system_metrics,
                'application': app_metrics
            }
    
    def reset_metrics(self):
        """Reset all metrics"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            logger.info("Metrics reset")
    
    def _build_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Build metric key with tags"""
        if not tags:
            return name
        
        tag_string = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_string}]"
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / 1024 / 1024,
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / 1024 / 1024 / 1024
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {}
    
    def _summarize_histograms(self) -> Dict[str, Dict[str, float]]:
        """Summarize histogram data"""
        summaries = {}
        
        for key, values in self._histograms.items():
            if not values:
                continue
            
            data = [v['value'] for v in values]
            summaries[key] = {
                'count': len(data),
                'min': min(data),
                'max': max(data),
                'mean': sum(data) / len(data),
                'p50': self._percentile(data, 50),
                'p95': self._percentile(data, 95),
                'p99': self._percentile(data, 99)
            }
        
        return summaries
    
    def _percentile(self, data: list, percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * percentile / 100
        f = int(k)
        c = k - f
        if f == len(sorted_data) - 1:
            return sorted_data[f]
        return sorted_data[f] * (1 - c) + sorted_data[f + 1] * c


class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, metrics_collector: MetricsCollector, metric_name: str, tags: Optional[Dict[str, str]] = None):
        self.metrics_collector = metrics_collector
        self.metric_name = metric_name
        self.tags = tags
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.metrics_collector.record_timing(self.metric_name, duration_ms, self.tags)


class APIMetrics:
    """Specific metrics for API operations"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
    
    def record_request(self, method: str, path: str, status_code: int, duration_ms: float):
        """Record API request metrics"""
        tags = {
            'method': method,
            'path': path,
            'status_code': str(status_code)
        }
        
        self.metrics_collector.increment_counter('api_requests_total', tags=tags)
        self.metrics_collector.record_timing('api_request', duration_ms, tags=tags)
        
        # Track error rates
        if status_code >= 400:
            self.metrics_collector.increment_counter('api_errors_total', tags=tags)
    
    def record_database_operation(self, operation: str, table: str, duration_ms: float, success: bool):
        """Record database operation metrics"""
        tags = {
            'operation': operation,
            'table': table,
            'success': str(success)
        }
        
        self.metrics_collector.increment_counter('db_operations_total', tags=tags)
        self.metrics_collector.record_timing('db_operation', duration_ms, tags=tags)


# Global metrics collector instance
metrics_collector = MetricsCollector()
api_metrics = APIMetrics(metrics_collector)


def setup_metrics():
    """Setup metrics collection"""
    if settings.metrics_enabled:
        logger.info("Metrics collection enabled")
        
        # Start periodic metrics logging
        def log_metrics():
            while True:
                time.sleep(60)  # Log metrics every minute
                metrics = metrics_collector.get_metrics()
                logger.info(f"Metrics snapshot: {json.dumps(metrics, indent=2)}")
        
        import threading
        metrics_thread = threading.Thread(target=log_metrics, daemon=True)
        metrics_thread.start()
    else:
        logger.info("Metrics collection disabled")
