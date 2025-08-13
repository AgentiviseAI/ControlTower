"""
AI Agent model with organization support
"""
from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING
from .base import BaseModel
from app.core.database_types import UniversalID

if TYPE_CHECKING:
    from .organization import Organization


class AIAgent(BaseModel):
    __tablename__ = "ai_agents"

    organization_id = Column(UniversalID(), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    preview_enabled = Column(Boolean, default=False)
    # Removed workflow_id - workflows now reference agents with is_default flag
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="agents")
