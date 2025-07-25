"""
Workflow model
"""
from sqlalchemy import Column, String, Text, JSON
from .base import BaseModel


class Workflow(BaseModel):
    __tablename__ = "workflows"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    agent_id = Column(String(36), nullable=True)  # Link to agent
    nodes = Column(JSON)  # Store workflow configuration
    edges = Column(JSON)  # Store workflow edges/connections
    status = Column(String(50), default="draft")
