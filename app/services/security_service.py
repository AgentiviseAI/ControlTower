"""
Security Service implementation
"""
from typing import List, Optional, Dict, Any
from app.repositories import SecurityRoleRepository
from app.core.exceptions import NotFoundError, ConflictError
from app.core.logging import get_logger


class SecurityService:
    """Service for Security and RBAC operations"""
    
    def __init__(self, role_repository: SecurityRoleRepository):
        self.role_repo = role_repository
        self.logger = get_logger(self.__class__.__name__)

    def create_role(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new security role"""
        self._validate_data(role_data, ['name'])
        
        # Check if role name already exists
        existing_role = self.role_repo.get_by_name(role_data['name'])
        if existing_role:
            raise ConflictError(f"Role with name '{role_data['name']}' already exists")
        
        self.logger.info(f"Creating role: {role_data['name']}")
        
        role = self.role_repo.create(**role_data)
        return self._to_dict(role)
   
    def _validate_data(self, data: Dict[str, Any], required_fields: List[str]):
        """Validate required fields in data"""
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
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
                result[field_name] = value
        
        return result
