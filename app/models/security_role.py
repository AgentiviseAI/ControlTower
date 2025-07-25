"""
Security Role model
"""
from sqlalchemy import Column, String, Text, JSON
from .base import BaseModel


class SecurityRole(BaseModel):
    __tablename__ = "security_roles"

    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    status = Column(String(50), default="active")
    permissions = Column(JSON)  # Store role permissions
