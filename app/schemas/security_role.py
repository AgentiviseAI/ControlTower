"""
Security Role schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SecurityRoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    permissions: List[str] = []


class SecurityRoleCreate(SecurityRoleBase):
    pass


class SecurityRoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class SecurityRole(SecurityRoleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
