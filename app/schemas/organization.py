from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
from enum import Enum


class OrganizationRole(str, Enum):
    """Organization role enumeration"""
    OWNER = "owner"
    ADMIN = "admin" 
    MEMBER = "member"
    VIEWER = "viewer"


class OrganizationBase(BaseModel):
    """Base organization schema."""
    name: str
    type: str = "personal"
    description: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None


class OrganizationResponse(BaseModel):
    """Schema for organization response."""
    id: uuid.UUID
    name: str
    type: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_orm(cls, organization):
        """Create response from Organization model"""
        return cls(
            id=organization.id,
            name=organization.name,
            type="personal" if organization.is_personal else "organization",
            description=organization.description,
            created_at=organization.created_at,
            updated_at=organization.updated_at
        )
    
    class Config:
        from_attributes = True


class OrganizationUserBase(BaseModel):
    """Base organization user schema."""
    role: str = "admin"


class OrganizationUserCreate(OrganizationUserBase):
    """Schema for creating organization user."""
    user_id: uuid.UUID
    organization_id: uuid.UUID


class OrganizationUserResponse(OrganizationUserBase):
    """Schema for organization user response."""
    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserOrganizationResponse(BaseModel):
    """Schema for user organization response."""
    id: uuid.UUID
    name: str
    type: str
    description: Optional[str] = None
    role: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AddUserToOrganizationRequest(BaseModel):
    """Schema for adding user to organization."""
    user_id: uuid.UUID
    role: str = "member"


class UpdateUserRoleRequest(BaseModel):
    """Schema for updating user role in organization."""
    role: str
