"""
RAG Connector Service implementation
"""
from typing import List, Optional, Dict, Any
from app.repositories import RAGConnectorRepository
from app.core.exceptions import NotFoundError, ConflictError
from .base import BaseService


class RAGConnectorService(BaseService):
    """Service for RAG Connector business logic"""
    
    def __init__(self, repository: RAGConnectorRepository):
        super().__init__(repository)
    
    def create_connector(self, organization_id: str, name: str, type: str, enabled: bool = True,
                        connection_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new RAG connector"""
        self._validate_data({'name': name, 'type': type}, ['name', 'type'])
        
        # Check if RAG connector with same name exists in this organization
        existing_connector = self.repository.get_by_name_and_organization(name, organization_id)
        if existing_connector:
            raise ConflictError(f"RAG Connector with name '{name}' already exists in this organization")
        
        self.logger.info(f"Creating RAG connector: {name} for organization: {organization_id}")
        
        connector = self.repository.create(
            name=name,
            type=type,
            enabled=enabled,
            connection_details=connection_details or {},
            organization_id=organization_id  # ✅ Always include organization_id
        )
        
        return self._to_dict(connector)
    
    def get_connector(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """Get RAG connector by ID"""
        connector = self.repository.get_by_id(connector_id)
        if not connector:
            raise NotFoundError("RAG Connector", connector_id)
        return self._to_dict(connector)
    
    def get_all_connectors(self) -> List[Dict[str, Any]]:
        """Get all RAG connectors"""
        connectors = self.repository.get_all()
        return [self._to_dict(connector) for connector in connectors]
    
    def list_connectors(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all RAG connectors for a specific organization"""
        connectors = self.repository.get_by_organization(organization_id)
        return [self._to_dict(connector) for connector in connectors]
    
    def update_connector(self, connector_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update RAG connector"""
        self.logger.info(f"Updating RAG connector: {connector_id}")
        
        connector = self.repository.update(connector_id, **kwargs)
        if not connector:
            raise NotFoundError("RAG Connector", connector_id)
        
        return self._to_dict(connector)
    
    def delete_connector(self, connector_id: str) -> bool:
        """Delete RAG connector"""
        self.logger.info(f"Deleting RAG connector: {connector_id}")
        
        success = self.repository.delete(connector_id)
        if not success:
            raise NotFoundError("RAG Connector", connector_id)
        
        return success
