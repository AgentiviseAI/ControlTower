"""
Service interfaces and base implementations following SOLID principles
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.core.logging import get_logger

logger = get_logger(__name__)


class IService(ABC):
    """Base service interface following Interface Segregation Principle"""
    pass


class BaseService:
    """
    Base service class providing common functionality
    Following Single Responsibility Principle
    """
    
    def __init__(self, repository):
        self.repository = repository
        self.logger = get_logger(self.__class__.__name__)
    
    def _validate_data(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate required fields in data"""
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values and sanitize data"""
        return {k: v for k, v in data.items() if v is not None}
    
    def _to_dict(self, model_instance, exclude_fields: List[str] = None) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        if not model_instance:
            return None
        
        exclude_fields = exclude_fields or []
        result = {}
        
        for column in model_instance.__table__.columns:
            field_name = column.name
            if field_name not in exclude_fields:
                value = getattr(model_instance, field_name)
                # Handle datetime serialization
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                # Handle UUID serialization - convert UUID objects to strings
                elif isinstance(value, UUID):
                    value = str(value)
                result[field_name] = value
        
        return result
