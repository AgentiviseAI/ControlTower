"""
MCP Tool model with organization support
"""
from sqlalchemy import Column, String, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
from app.core.database_types import UniversalID


class MCPTool(BaseModel):
    __tablename__ = "mcp_tools"

    organization_id = Column(UniversalID(), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    endpoint_url = Column(String(500), nullable=False)
    transport = Column(String(100), default="Streamable HTTP")
    required_permissions = Column(JSON)
    auth_headers = Column(JSON)
    
    # Relationships
    organization = relationship("Organization", back_populates="mcp_tools")
