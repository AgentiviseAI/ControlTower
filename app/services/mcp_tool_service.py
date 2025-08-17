"""
MCP Tool Service implementation
"""
from typing import List, Optional, Dict, Any
from app.repositories import MCPToolRepository
from app.repositories.intent_data_repository import IntentDataRepository
from app.core.exceptions import NotFoundError, ConflictError
from .base import BaseService


class MCPToolService(BaseService):
    """Service for MCP Tool business logic"""
    
    def __init__(self, repository: MCPToolRepository, intent_data_repository: Optional[IntentDataRepository] = None):
        super().__init__(repository)
        self.intent_data_repository = intent_data_repository
    
    def _create_intent_data_for_tool(self, organization_id: str, tool_id: str, tool_name: str, tool_description: str = None):
        """Helper method to create intent data for MCP tool"""
        if self.intent_data_repository:
            try:
                intent_data = self.intent_data_repository.create(
                    organization_id=organization_id,
                    name=f"Tool: {tool_name}",
                    description=tool_description or f"Intent data for MCP tool: {tool_name}",
                    source_type="mcp_tool",
                    source_id=tool_id,
                    category="Tool",
                    enabled=True
                )
                self.logger.info(f"Created intent data for MCP tool: {tool_name}")
            except Exception as e:
                self.logger.error(f"Failed to create intent data for MCP tool {tool_name}: {e}")
    
    def _update_intent_data_for_tool(self, organization_id: str, tool_id: str, tool_name: str, tool_description: str = None):
        """Helper method to update intent data for MCP tool"""
        if self.intent_data_repository:
            try:
                # Find existing intent data for this MCP tool
                intent_data_list = self.intent_data_repository.list_by_source_type(organization_id, "mcp_tool")
                for intent_data in intent_data_list:
                    if intent_data.source_id == tool_id:
                        intent_data.name = f"Tool: {tool_name}"
                        intent_data.description = tool_description or f"Intent data for MCP tool: {tool_name}"
                        self.intent_data_repository.update(intent_data)
                        self.logger.info(f"Updated intent data for MCP tool: {tool_name}")
                        break
            except Exception as e:
                self.logger.error(f"Failed to update intent data for MCP tool {tool_name}: {e}")
    
    def _delete_intent_data_for_tool(self, organization_id: str, tool_id: str):
        """Helper method to delete intent data for MCP tool"""
        if self.intent_data_repository:
            try:
                deleted_count = self.intent_data_repository.delete_by_source(organization_id, "mcp_tool", tool_id)
                if deleted_count > 0:
                    self.logger.info(f"Deleted {deleted_count} intent data records for MCP tool: {tool_id}")
            except Exception as e:
                self.logger.error(f"Failed to delete intent data for MCP tool {tool_id}: {e}")
    
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
        
        # Create intent data for the new MCP tool
        self._create_intent_data_for_tool(organization_id, str(tool.id), name, description)
        
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
        
        # Update intent data if name or description changed
        if 'name' in kwargs or 'description' in kwargs:
            self._update_intent_data_for_tool(tool.organization_id, tool_id, tool.name, tool.description)
        
        return self._to_dict(tool)
    
    def delete_tool(self, tool_id: str) -> bool:
        """Delete MCP tool"""
        self.logger.info(f"Deleting MCP tool: {tool_id}")
        
        # Get the tool first to retrieve organization_id
        tool = self.repository.get_by_id(tool_id)
        if not tool:
            raise NotFoundError("MCP Tool", tool_id)
        
        organization_id = tool.organization_id
        
        success = self.repository.delete(tool_id)
        if not success:
            raise NotFoundError("MCP Tool", tool_id)
        
        # Delete associated intent data
        self._delete_intent_data_for_tool(organization_id, tool_id)
        
        return success
