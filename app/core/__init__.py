"""
Core module - Common utilities and base classes
"""
from .config import settings, get_database_url, get_log_config
from .database import Base, get_db, create_tables, DatabaseManager
from .logging import setup_logging, get_logger
from .metrics import MetricsCollector, setup_metrics
from .exceptions import APIException, ValidationException, NotFoundError, UnauthorizedError

__all__ = [
    "settings",
    "get_database_url", 
    "get_log_config",
    "Base",
    "get_db",
    "create_tables",
    "DatabaseManager",
    "setup_logging",
    "get_logger",
    "MetricsCollector",
    "setup_metrics",
    "APIException",
    "ValidationException", 
    "NotFoundError",
    "UnauthorizedError",
]
