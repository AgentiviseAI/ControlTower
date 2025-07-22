"""
User Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import User
from .base import BaseRepository


class UserRepository(BaseRepository):
    """Repository for User operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.get_by_field("username", username)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.get_by_field("email", email)
    
    def get_active_users(self) -> List[User]:
        """Get all active users"""
        return self.filter_by(status="active")
    
    def get_by_role(self, role: str) -> List[User]:
        """Get users by role"""
        return self.filter_by(role=role)
