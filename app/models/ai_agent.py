"""
AI Agent model
"""
from sqlalchemy import Column, String, Boolean, Text
from .base import BaseModel


class AIAgent(BaseModel):
    __tablename__ = "ai_agents"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    preview_enabled = Column(Boolean, default=False)
    workflow_id = Column(String(36), nullable=True)
