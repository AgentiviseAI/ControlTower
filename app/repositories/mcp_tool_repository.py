"""
MCP Tool Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List

from app.models import MCPTool
from .base import BaseRepository


class MCPToolRepository(BaseRepository):
    """Repository for MCP Tool operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, MCPTool)
    
    def get_enabled_tools(self) -> List[MCPTool]:
        """Get all enabled MCP tools"""
        return self.filter_by(enabled=True)
    
    def get_by_status(self, status: str) -> List[MCPTool]:
        """Get MCP tools by status"""
        return self.filter_by(status=status)
