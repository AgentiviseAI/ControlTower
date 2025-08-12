"""
Workflow schemas with organization support
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = "inactive"
    nodes: Optional[List[Dict[str, Any]]] = []
    edges: Optional[List[Dict[str, Any]]] = []
    agent_id: Optional[str] = None
    is_default: bool = False  # Mark as default workflow for agent
    execution_order: int = 0  # Order of execution (0 = highest priority)


class WorkflowCreate(WorkflowBase):
    """Create Workflow schema - organization_id is injected via dependency"""
    pass


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    agent_id: Optional[str] = None
    is_default: Optional[bool] = None  # Allow updating default status
    execution_order: Optional[int] = None  # Allow updating execution order
    # organization_id cannot be changed after creation


class Workflow(WorkflowBase):
    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
