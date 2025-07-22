"""
Logging configuration and utilities
"""
import logging
import logging.config
import os
import sys
from typing import Any, Dict
from pathlib import Path

from .config import settings, get_log_config


def setup_logging() -> None:
    """Setup logging configuration"""
    
    # Ensure logs directory exists
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(exist_ok=True)
    
    # Apply logging configuration
    log_config = get_log_config()
    logging.config.dictConfig(log_config)
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {settings.log_level}")
    logger.info(f"Log file: {settings.log_file}")
    logger.info(f"Environment: {settings.environment}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)


class StructuredLogger:
    """Structured logger for consistent log formatting"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with structured data"""
        self._log(logging.ERROR, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal log method with structured data"""
        extra_data = {f"extra_{k}": v for k, v in kwargs.items()}
        self.logger.log(level, message, extra=extra_data)


class APILogger:
    """Logger specifically for API operations"""
    
    def __init__(self):
        self.logger = get_logger("api")
    
    def log_request(self, method: str, path: str, user_id: str = None, **kwargs):
        """Log API request"""
        self.logger.info(
            f"API Request: {method} {path}",
            extra={
                "method": method,
                "path": path,
                "user_id": user_id,
                **kwargs
            }
        )
    
    def log_response(self, method: str, path: str, status_code: int, duration_ms: float, **kwargs):
        """Log API response"""
        self.logger.info(
            f"API Response: {method} {path} - {status_code} ({duration_ms}ms)",
            extra={
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                **kwargs
            }
        )
    
    def log_error(self, method: str, path: str, error: str, **kwargs):
        """Log API error"""
        self.logger.error(
            f"API Error: {method} {path} - {error}",
            extra={
                "method": method,
                "path": path,
                "error": error,
                **kwargs
            }
        )


class DatabaseLogger:
    """Logger specifically for database operations"""
    
    def __init__(self):
        self.logger = get_logger("database")
    
    def log_query(self, operation: str, table: str, duration_ms: float = None, **kwargs):
        """Log database query"""
        message = f"DB {operation}: {table}"
        if duration_ms:
            message += f" ({duration_ms}ms)"
        
        self.logger.debug(
            message,
            extra={
                "operation": operation,
                "table": table,
                "duration_ms": duration_ms,
                **kwargs
            }
        )
    
    def log_error(self, operation: str, table: str, error: str, **kwargs):
        """Log database error"""
        self.logger.error(
            f"DB Error {operation}: {table} - {error}",
            extra={
                "operation": operation,
                "table": table,
                "error": error,
                **kwargs
            }
        )


# Global logger instances
api_logger = APILogger()
db_logger = DatabaseLogger()
