"""
Security Role Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models import SecurityRole
from app.models.security_role import RoleType
from .base import BaseRepository


class SecurityRoleRepository(BaseRepository):
    """Repository for Security Role operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, SecurityRole)
    
    def get_active_roles(self) -> List[SecurityRole]:
        """Get all active security roles"""
        return self.filter_by(status="active")
    
    def get_active_system_roles(self) -> List[SecurityRole]:
        """Get all active system roles (no organization_id)"""
        return self.db.query(self.model).filter(
            self.model.status == "active",
            self.model.type == RoleType.SYSTEM,
            self.model.organization_id.is_(None)
        ).all()
    
    def get_active_organization_roles(self, organization_id: UUID) -> List[SecurityRole]:
        """Get all active organization roles for a specific organization"""
        return self.db.query(self.model).filter(
            self.model.status == "active",
            self.model.type == RoleType.ORGANIZATION,
            self.model.organization_id == organization_id
        ).all()
    
    def get_by_name(self, name: str) -> Optional[SecurityRole]:
        """Get security role by name"""
        return self.get_by_field("name", name)
