"""
Workflow Component Definition Service
"""
from typing import List, Dict, Any, Optional

from app.repositories.workflow_component_definition_repository import WorkflowComponentDefinitionRepository
from app.core.exceptions import NotFoundError
from app.services.base import BaseService


class WorkflowComponentDefinitionService(BaseService):
    """Service for workflow component definition business logic"""
    
    def __init__(self, repository: WorkflowComponentDefinitionRepository):
        super().__init__(repository)
    
    def get_component(self, component_id: str) -> Dict[str, Any]:
        """Get component definition by ID"""
        component = self.repository.get_by_component_id(component_id)
        if not component:
            raise NotFoundError(f"Component definition with ID '{component_id}' not found")
        return self._to_dict(component)
    
    def list_components(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """List all component definitions"""
        if enabled_only:
            components = self.repository.list_enabled()
        else:
            components = self.repository.list_all()
        return [self._to_dict(component) for component in components]
    
    def list_components_by_category(self, category: str) -> List[Dict[str, Any]]:
        """List component definitions in a specific category"""
        components = self.repository.list_by_category(category)
        return [self._to_dict(component) for component in components]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return self.repository.get_categories()
    
    def search_components(self, search_term: str) -> List[Dict[str, Any]]:
        """Search component definitions by name or description"""
        components = self.repository.search_by_name_or_description(search_term)
        return [self._to_dict(component) for component in components]
    
    def get_components_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Get components that have any of the specified tags"""
        components = self.repository.get_by_tags(tags)
        return [self._to_dict(component) for component in components]