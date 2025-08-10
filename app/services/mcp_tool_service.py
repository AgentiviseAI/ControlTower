"""
MCP Tool Service implementation
"""
from typing import List, Optional, Dict, Any
from app.repositories import MCPToolRepository
from app.core.exceptions import NotFoundError, ConflictError
from .base import BaseService


class MCPToolService(BaseService):
    """Service for MCP Tool business logic"""
    
    def __init__(self, repository: MCPToolRepository):
        super().__init__(repository)
    
    def create_tool(self, organization_id: str, name: str, description: str = None, enabled: bool = True,
                   endpoint_url: str = None, transport: str = "Streamable HTTP", 
                   required_permissions: List[str] = None, 
                   auth_headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Create a new MCP tool"""
        self._validate_data({'name': name, 'endpoint_url': endpoint_url}, 
                          ['name', 'endpoint_url'])
        
        # Check if MCP tool with same name exists in this organization
        existing_tool = self.repository.get_by_name_and_organization(name, organization_id)
        if existing_tool:
            raise ConflictError(f"MCP Tool with name '{name}' already exists in this organization")
        
        self.logger.info(f"Creating MCP tool: {name} for organization: {organization_id}")
        
        tool = self.repository.create(
            name=name,
            description=description,
            enabled=enabled,
            endpoint_url=endpoint_url,
            organization_id=organization_id,  # ✅ Always include organization_id
            transport=transport,
            required_permissions=required_permissions or [],
            auth_headers=auth_headers or {}
        )
        
        return self._to_dict(tool)
    
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get MCP tool by ID"""
        tool = self.repository.get_by_id(tool_id)
        if not tool:
            raise NotFoundError("MCP Tool", tool_id)
        return self._to_dict(tool)
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all MCP tools"""
        tools = self.repository.get_all()
        return [self._to_dict(tool) for tool in tools]
    
    def list_tools(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all MCP tools for a specific organization"""
        tools = self.repository.get_by_organization(organization_id)
        return [self._to_dict(tool) for tool in tools]
    
    def update_tool(self, tool_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update MCP tool"""
        self.logger.info(f"Updating MCP tool: {tool_id}")
        
        tool = self.repository.update(tool_id, **kwargs)
        if not tool:
            raise NotFoundError("MCP Tool", tool_id)
        
        return self._to_dict(tool)
    
    def delete_tool(self, tool_id: str) -> bool:
        """Delete MCP tool"""
        self.logger.info(f"Deleting MCP tool: {tool_id}")
        
        success = self.repository.delete(tool_id)
        if not success:
            raise NotFoundError("MCP Tool", tool_id)
        
        return success
