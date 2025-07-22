"""
RAG Connector Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List

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
