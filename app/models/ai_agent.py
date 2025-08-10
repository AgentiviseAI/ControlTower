"""
AI Agent model with organization support
"""
from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING
from .base import BaseModel

if TYPE_CHECKING:
    from .organization import Organization


class AIAgent(BaseModel):
    __tablename__ = "ai_agents"

    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    preview_enabled = Column(Boolean, default=False)
    workflow_id = Column(String(36), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="agents")
