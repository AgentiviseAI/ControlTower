"""
Workflow model with organization support
"""
from sqlalchemy import Column, String, Text, JSON, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel
from app.core.database_types import UniversalID


class Workflow(BaseModel):
    __tablename__ = "workflows"

    organization_id = Column(UniversalID(), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    agent_id = Column(UniversalID(), nullable=True)  # Link to agent as UUID
    nodes = Column(JSON)  # Store workflow configuration
    edges = Column(JSON)  # Store workflow edges/connections
    status = Column(String(50), default="draft")
    is_default = Column(Boolean, default=False)  # Mark as default workflow for agent
    execution_order = Column(Integer, default=0)  # Order of execution (0 = highest priority)
    
    # Relationships
    organization = relationship("Organization", back_populates="workflows")
