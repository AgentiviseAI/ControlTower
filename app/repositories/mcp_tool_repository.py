"""
MCP Tool Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import MCPTool
from .base import BaseRepository


class MCPToolRepository(BaseRepository):
    """Repository for MCP Tool operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, MCPTool)
    
    def get_enabled_tools(self) -> List[MCPTool]:
        """Get all enabled MCP tools"""
        return self.filter_by(enabled=True)
    
    def get_by_transport(self, transport: str) -> List[MCPTool]:
        """Get MCP tools by transport"""
        return self.filter_by(transport=transport)
    
    def get_by_organization(self, organization_id: str) -> List[MCPTool]:
        """Get all MCP tools for a specific organization"""
        return self.db.query(MCPTool).filter(MCPTool.organization_id == organization_id).all()
    
    def get_by_name_and_organization(self, name: str, organization_id: str) -> Optional[MCPTool]:
        """Get MCP tool by name within a specific organization"""
        return self.db.query(MCPTool).filter(
            MCPTool.name == name,
            MCPTool.organization_id == organization_id
        ).first()
    
    def get_enabled_tools_by_organization(self, organization_id: str) -> List[MCPTool]:
        """Get all enabled MCP tools for a specific organization"""
        return self.db.query(MCPTool).filter(
            MCPTool.organization_id == organization_id,
            MCPTool.enabled == True
        ).all()
