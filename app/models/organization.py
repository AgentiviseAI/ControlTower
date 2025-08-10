"""
Organization Models
Contains organization-related SQLAlchemy models for ControlTower
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum, Boolean, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from .base import BaseModel

if TYPE_CHECKING:
    from .ai_agent import AIAgent
    from .mcp_tool import MCPTool
    from .llm import LLM
    from .rag_connector import RAGConnector
    from .workflow import Workflow


class OrganizationRole(PyEnum):
    """Organization role enumeration"""
    OWNER = "owner"
    ADMIN = "admin" 
    MEMBER = "member"
    VIEWER = "viewer"


class OrganizationStatus(PyEnum):
    """Organization status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Organization(BaseModel):
    """Organization model for ControlTower"""
    __tablename__ = "organizations"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Organization type and settings
    is_personal = Column(Boolean, default=False, nullable=False)
    status = Column(Enum(OrganizationStatus), default=OrganizationStatus.ACTIVE, nullable=False)
    
    # Relationships
    users: Mapped[List["OrganizationUser"]] = relationship("OrganizationUser", back_populates="organization", cascade="all, delete-orphan")
    agents: Mapped[List["AIAgent"]] = relationship("AIAgent", back_populates="organization")
    mcp_tools: Mapped[List["MCPTool"]] = relationship("MCPTool", back_populates="organization")
    llms: Mapped[List["LLM"]] = relationship("LLM", back_populates="organization")
    rag_connectors: Mapped[List["RAGConnector"]] = relationship("RAGConnector", back_populates="organization")
    workflows: Mapped[List["Workflow"]] = relationship("Workflow", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', is_personal={self.is_personal})>"


class OrganizationUser(BaseModel):
    """Organization-User association model"""
    __tablename__ = "organization_users"
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # References AuthService user (UUID)
    role = Column(Enum(OrganizationRole), default=OrganizationRole.MEMBER, nullable=False)
    
    # Timestamps (inherited from BaseModel but override for clarity)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="users")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="unique_org_user"),
    )
    
    def __repr__(self):
        return f"<OrganizationUser(org_id={self.organization_id}, user_id={self.user_id}, role={self.role.value})>"
