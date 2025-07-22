"""
Security Role Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import SecurityRole
from .base import BaseRepository


class SecurityRoleRepository(BaseRepository):
    """Repository for Security Role operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, SecurityRole)
    
    def get_active_roles(self) -> List[SecurityRole]:
        """Get all active security roles"""
        return self.filter_by(status="active")
    
    def get_by_name(self, name: str) -> Optional[SecurityRole]:
        """Get security role by name"""
        return self.get_by_field("name", name)
