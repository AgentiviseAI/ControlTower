"""
AI Agent schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AIAgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: bool = True
    preview_enabled: bool = False
    workflow_id: Optional[str] = None


class AIAgentCreate(AIAgentBase):
    pass


class AIAgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: Optional[bool] = None
    preview_enabled: Optional[bool] = None
    workflow_id: Optional[str] = None


class AIAgent(AIAgentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
