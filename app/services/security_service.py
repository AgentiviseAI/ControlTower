"""
Security Service implementation
"""
from typing import List, Optional, Dict, Any
from app.repositories import SecurityRoleRepository, UserRepository
from app.core.exceptions import NotFoundError, ConflictError
from app.core.logging import get_logger


class SecurityService:
    """Service for Security and RBAC operations"""
    
    def __init__(self, role_repository: SecurityRoleRepository, user_repository: UserRepository):
        self.role_repo = role_repository
        self.user_repo = user_repository
        self.logger = get_logger(self.__class__.__name__)
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        self._validate_data(user_data, ['username', 'password', 'name', 'email', 'role'])
        
        # Check if username already exists
        existing_user = self.user_repo.get_by_username(user_data['username'])
        if existing_user:
            raise ConflictError(f"User with username '{user_data['username']}' already exists")
        
        # Check if email already exists
        existing_email = self.user_repo.get_by_email(user_data['email'])
        if existing_email:
            raise ConflictError(f"User with email '{user_data['email']}' already exists")
        
        self.logger.info(f"Creating user: {user_data['username']}")
        
        user = self.user_repo.create(**user_data)
        return self._to_dict(user, exclude_fields=['password'])
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return self._to_dict(user, exclude_fields=['password'])
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        users = self.user_repo.get_all()
        return [self._to_dict(user, exclude_fields=['password']) for user in users]
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user"""
        self.logger.info(f"Updating user: {user_id}")
        
        user = self.user_repo.update(user_id, **user_data)
        if not user:
            raise NotFoundError("User", user_id)
        
        return self._to_dict(user, exclude_fields=['password'])
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        self.logger.info(f"Deleting user: {user_id}")
        
        success = self.user_repo.delete(user_id)
        if not success:
            raise NotFoundError("User", user_id)
        
        return success

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

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        user = self.user_repo.get_by_username(username)
        if user:
            return self._to_dict(user, exclude_fields=['password'])
        return None
    
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
