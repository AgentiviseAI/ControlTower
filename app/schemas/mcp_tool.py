"""
MCP Tool schemas with organization support
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class MCPToolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: bool = True
    endpoint_url: str = Field(..., min_length=1, max_length=500)
    transport: str = "Streamable HTTP"
    required_permissions: Optional[List[str]] = []
    auth_headers: Optional[Dict[str, str]] = {}


class MCPToolCreate(MCPToolBase):
    """Create MCP Tool schema - organization_id is injected via dependency"""
    pass


class MCPToolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: Optional[bool] = None
    endpoint_url: Optional[str] = Field(None, min_length=1, max_length=500)
    transport: Optional[str] = None
    required_permissions: Optional[List[str]] = None
    auth_headers: Optional[Dict[str, str]] = None
    # organization_id cannot be changed after creation


class MCPTool(MCPToolBase):
    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
