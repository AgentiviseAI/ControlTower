"""
Custom exceptions for the application
"""
from typing import Any, Dict, Optional


class APIException(Exception):
    """Base API exception"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(APIException):
    """Validation error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class NotFoundError(APIException):
    """Resource not found exception"""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status_code=404)


class UnauthorizedError(APIException):
    """Unauthorized access exception"""
    
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, status_code=401)


class ForbiddenError(APIException):
    """Forbidden access exception"""
    
    def __init__(self, message: str = "Forbidden access"):
        super().__init__(message, status_code=403)


class ConflictError(APIException):
    """Resource conflict exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, details=details)


class DatabaseError(APIException):
    """Database operation error"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class ExternalServiceError(APIException):
    """External service error"""
    
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        full_message = f"External service '{service}' error: {message}"
        super().__init__(full_message, status_code=503, details=details)
