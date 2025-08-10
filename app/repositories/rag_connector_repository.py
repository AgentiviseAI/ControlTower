"""
RAG Connector Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import RAGConnector
from .base import BaseRepository


class RAGConnectorRepository(BaseRepository):
    """Repository for RAG Connector operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, RAGConnector)
    
    def get_enabled_connectors(self) -> List[RAGConnector]:
        """Get all enabled RAG connectors"""
        return self.filter_by(enabled=True)
    
    def get_by_type(self, connector_type: str) -> List[RAGConnector]:
        """Get RAG connectors by type"""
        return self.filter_by(type=connector_type)
    
    def get_by_organization(self, organization_id: str) -> List[RAGConnector]:
        """Get all RAG connectors for a specific organization"""
        return self.db.query(RAGConnector).filter(RAGConnector.organization_id == organization_id).all()
    
    def get_by_name_and_organization(self, name: str, organization_id: str) -> Optional[RAGConnector]:
        """Get RAG connector by name within a specific organization"""
        return self.db.query(RAGConnector).filter(
            RAGConnector.name == name,
            RAGConnector.organization_id == organization_id
        ).first()
    
    def get_enabled_connectors_by_organization(self, organization_id: str) -> List[RAGConnector]:
        """Get all enabled RAG connectors for a specific organization"""
        return self.db.query(RAGConnector).filter(
            RAGConnector.organization_id == organization_id,
            RAGConnector.enabled == True
        ).all()
