"""
Security Role model
"""
from sqlalchemy import Column, String, Text, JSON, Enum as SQLEnum
from enum import Enum
from .base import BaseModel


class RoleType(Enum):
    SYSTEM = "system"
    ORGANIZATION = "organization"


class SecurityRole(BaseModel):
    __tablename__ = "security_roles"

    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    status = Column(String(50), default="active")
    permissions = Column(JSON)  # Store role permissions
    type = Column(SQLEnum(RoleType), default=RoleType.ORGANIZATION, nullable=False)
