"""
IntentData service for business logic operations
"""
from typing import List, Dict, Any, Optional
from app.repositories.intent_data_repository import IntentDataRepository
from app.models.intent_data import IntentData
from app.core.exceptions import NotFoundError
from app.services.base import BaseService
from app.core.logging import get_logger

logger = get_logger(__name__)


class IntentDataService(BaseService):
    """Service for IntentData business logic"""
    
    def __init__(self, repository: IntentDataRepository):
        super().__init__(repository)
    
    def create_intent_data(self, organization_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new intent data record"""
        intent_data = IntentData(
            organization_id=organization_id,
            name=data["name"],
            description=data.get("description"),
            source_type=data["source_type"],
            source_id=data["source_id"],
            category=data.get("category"),
            tags=data.get("tags"),
            enabled=data.get("enabled", True)
        )
        
        created_intent_data = self.repository.create(intent_data)
        return self._to_dict(created_intent_data)
    
    def update_intent_data(self, intent_data_id: str, organization_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an intent data record"""
        intent_data = self.repository.get_by_id_and_org(intent_data_id, organization_id)
        if not intent_data:
            raise NotFoundError(f"IntentData with ID '{intent_data_id}' not found")
        
        # Update fields
        if "name" in data:
            intent_data.name = data["name"]
        if "description" in data:
            intent_data.description = data["description"]
        if "category" in data:
            intent_data.category = data["category"]
        if "tags" in data:
            intent_data.tags = data["tags"]
        if "enabled" in data:
            intent_data.enabled = data["enabled"]
        
        updated_intent_data = self.repository.update(intent_data)
        return self._to_dict(updated_intent_data)
    
    def get_intent_data(self, intent_data_id: str, organization_id: str) -> Dict[str, Any]:
        """Get intent data by ID"""
        intent_data = self.repository.get_by_id_and_org(intent_data_id, organization_id)
        if not intent_data:
            raise NotFoundError(f"IntentData with ID '{intent_data_id}' not found")
        return self._to_dict(intent_data)
    
    def list_intent_data(self, organization_id: str, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """List all intent data for an organization"""
        if enabled_only:
            intent_data_list = self.repository.list_enabled(organization_id)
        else:
            intent_data_list = self.repository.list_by_organization(organization_id)
        return [self._to_dict(intent_data) for intent_data in intent_data_list]
    
    def list_by_source_type(self, organization_id: str, source_type: str) -> List[Dict[str, Any]]:
        """List intent data by source type"""
        intent_data_list = self.repository.list_by_source_type(organization_id, source_type)
        return [self._to_dict(intent_data) for intent_data in intent_data_list]
    
    def search_intent_data(self, organization_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search intent data by name or description"""
        intent_data_list = self.repository.search_by_name_or_description(organization_id, search_term)
        return [self._to_dict(intent_data) for intent_data in intent_data_list]
    
    def get_by_category(self, organization_id: str, category: str) -> List[Dict[str, Any]]:
        """Get intent data by category"""
        intent_data_list = self.repository.get_by_category(organization_id, category)
        return [self._to_dict(intent_data) for intent_data in intent_data_list]
    
    def delete_intent_data(self, intent_data_id: str, organization_id: str) -> bool:
        """Delete an intent data record"""
        intent_data = self.repository.get_by_id_and_org(intent_data_id, organization_id)
        if not intent_data:
            raise NotFoundError(f"IntentData with ID '{intent_data_id}' not found")
        
        return self.repository.delete(intent_data_id)
    
    def create_from_rest_api(self, organization_id: str, rest_api_id: str, name: str, description: str = None, category: str = None) -> Dict[str, Any]:
        """Create intent data from a REST API"""
        data = {
            "name": name,
            "description": description,
            "source_type": "rest_api",
            "source_id": rest_api_id,
            "category": category or "API",
            "enabled": True
        }
        return self.create_intent_data(organization_id, data)
    
    def create_from_mcp_tool(self, organization_id: str, mcp_tool_id: str, name: str, description: str = None, category: str = None) -> Dict[str, Any]:
        """Create intent data from an MCP tool"""
        data = {
            "name": name,
            "description": description,
            "source_type": "mcp_tool",
            "source_id": mcp_tool_id,
            "category": category or "Tool",
            "enabled": True
        }
        return self.create_intent_data(organization_id, data)
    
    def sync_from_source(self, organization_id: str, source_type: str, source_id: str, intents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sync intent data from a source (REST API or MCP tool)"""
        # Delete existing intent data for this source
        deleted_count = self.repository.delete_by_source(organization_id, source_type, source_id)
        logger.info(f"Deleted {deleted_count} existing intent data records for {source_type}:{source_id}")
        
        # Create new intent data records
        created_intents = []
        failed_intents = []
        
        for intent in intents:
            try:
                data = {
                    "name": intent["name"],
                    "description": intent.get("description"),
                    "source_type": source_type,
                    "source_id": source_id,
                    "category": intent.get("category", "API" if source_type == "rest_api" else "Tool"),
                    "tags": intent.get("tags"),
                    "enabled": intent.get("enabled", True)
                }
                created_intent = self.create_intent_data(organization_id, data)
                created_intents.append(created_intent)
            except Exception as e:
                logger.error(f"Failed to create intent data for {intent.get('name', 'unknown')}: {e}")
                failed_intents.append({
                    "name": intent.get("name", "unknown"),
                    "error": str(e)
                })
        
        return {
            "created": created_intents,
            "failed": failed_intents,
            "total_requested": len(intents),
            "total_created": len(created_intents),
            "deleted_count": deleted_count
        }
    
    def bulk_create(self, organization_id: str, intent_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk create intent data"""
        created_intents = []
        failed_intents = []
        
        for data in intent_data_list:
            try:
                created_intent = self.create_intent_data(organization_id, data)
                created_intents.append(created_intent)
            except Exception as e:
                logger.error(f"Failed to create intent data for {data.get('name', 'unknown')}: {e}")
                failed_intents.append({
                    "name": data.get("name", "unknown"),
                    "error": str(e)
                })
        
        return {
            "created": created_intents,
            "failed": failed_intents,
            "total_requested": len(intent_data_list),
            "total_created": len(created_intents)
        }
