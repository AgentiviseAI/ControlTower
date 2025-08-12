"""
Organization Repository for data access operations
"""
from typing import List, Dict, Any, Optional
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy.orm import Session, selectinload
from app.models.organization import Organization, OrganizationUser, OrganizationRole, OrganizationStatus
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository):
    """Repository for Organization entity operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, Organization)
    
    def get_by_name(self, name: str) -> Optional[Organization]:
        """Get organization by name"""
        return self.db.query(Organization).filter(Organization.name == name).first()
    
    def get_by_domain(self, domain: str) -> Optional[Organization]:
        """Get organization by domain"""
        return self.db.query(Organization).filter(Organization.domain == domain).first()
    
    def search_by_name(self, name_pattern: str) -> List[Organization]:
        """Search organizations by name pattern"""
        return self.db.query(Organization).filter(
            Organization.name.ilike(f"%{name_pattern}%")
        ).all()
    
    def get_verified_organizations(self) -> List[Organization]:
        """Get all domain-verified organizations"""
        return self.db.query(Organization).filter(
            Organization.domain_verified == True
        ).all()

    def create_organization(self, name: str, description: Optional[str] = None, is_personal: bool = False) -> Organization:
        """Create a new organization"""
        organization = Organization(
            name=name,
            description=description,
            is_personal=is_personal,
            status=OrganizationStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        return organization
    
    def get_organization_by_id(self, organization_id: UUID) -> Optional[Organization]:
        """Get organization by ID"""
        return self.db.query(Organization).filter(Organization.id == organization_id).first()
    
    def get_organization_by_name(self, name: str) -> Optional[Organization]:
        """Get organization by name"""
        return self.db.query(Organization).filter(Organization.name == name).first()
    
    def add_user_to_organization(
        self, 
        organization_id: UUID, 
        user_id: UUID, 
        role: OrganizationRole
    ) -> OrganizationUser:
        """Add a user to an organization with a specific role"""
        org_user = OrganizationUser(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(org_user)
        self.db.commit()
        self.db.refresh(org_user)
        return org_user
    
    def get_user_organizations(self, user_id: UUID) -> List[tuple]:
        """Get all organizations for a user with their roles"""
        return self.db.query(Organization, OrganizationUser.role)\
            .join(OrganizationUser, Organization.id == OrganizationUser.organization_id)\
            .filter(OrganizationUser.user_id == user_id)\
            .filter(Organization.status == OrganizationStatus.ACTIVE)\
            .all()
    
    def get_organization_users(self, organization_id: UUID) -> List[OrganizationUser]:
        """Get all users in an organization"""
        return self.db.query(OrganizationUser)\
            .filter(OrganizationUser.organization_id == organization_id)\
            .options(selectinload(OrganizationUser.organization))\
            .all()
    
    def get_user_role_in_organization(
        self, 
        organization_id: UUID, 
        user_id: UUID
    ) -> Optional[OrganizationRole]:
        """Get user's role in an organization"""
        result = self.db.query(OrganizationUser.role)\
            .filter(OrganizationUser.organization_id == organization_id)\
            .filter(OrganizationUser.user_id == user_id)\
            .first()
        return result[0] if result else None
    
    def remove_user_from_organization(self, organization_id: UUID, user_id: UUID):
        """Remove a user from an organization"""
        org_user = self.db.query(OrganizationUser)\
            .filter(OrganizationUser.organization_id == organization_id)\
            .filter(OrganizationUser.user_id == user_id)\
            .first()
        if org_user:
            self.db.delete(org_user)
            self.db.commit()
