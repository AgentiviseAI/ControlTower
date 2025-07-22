"""
Authentication Service implementation
"""
from typing import List, Optional, Dict, Any
from app.repositories import UserRepository
from app.core.logging import get_logger


class AuthService:
    """Service for Authentication operations"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository
        self.logger = get_logger(self.__class__.__name__)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password"""
        try:
            user = self.user_repo.get_by_username(username)
            if not user:
                self.logger.warning(f"Authentication failed: user '{username}' not found")
                return None
            
            # In a real app, you'd hash the password and compare hashes
            # For this demo, we'll do a simple string comparison
            if user.password == password and user.status == "active":
                self.logger.info(f"User '{username}' authenticated successfully")
                return self._to_dict(user, exclude_fields=['password'])
            else:
                self.logger.warning(f"Authentication failed: invalid credentials for user '{username}'")
                return None
        except Exception as e:
            self.logger.error(f"Error during authentication for user '{username}': {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        user = self.user_repo.get_by_username(username)
        if user:
            return self._to_dict(user, exclude_fields=['password'])
        return None
    
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
