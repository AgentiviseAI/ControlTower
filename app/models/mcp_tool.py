"""
MCP Tool model
"""
from sqlalchemy import Column, String, Boolean, Text, JSON
from .base import BaseModel


class MCPTool(BaseModel):
    __tablename__ = "mcp_tools"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    endpoint_url = Column(String(500), nullable=False)
    transport = Column(String(100), default="Streamable HTTP")
    required_permissions = Column(JSON)
    auth_headers = Column(JSON)
