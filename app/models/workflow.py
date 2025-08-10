"""
Workflow model with organization support
"""
from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Workflow(BaseModel):
    __tablename__ = "workflows"

    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    agent_id = Column(String(36), nullable=True)  # Link to agent
    nodes = Column(JSON)  # Store workflow configuration
    edges = Column(JSON)  # Store workflow edges/connections
    status = Column(String(50), default="draft")
    
    # Relationships
    organization = relationship("Organization", back_populates="workflows")
