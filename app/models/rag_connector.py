"""
RAG Connector model with organization support
"""
from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
from app.core.database_types import UniversalID


class RAGConnector(BaseModel):
    __tablename__ = "rag_connectors"

    organization_id = Column(UniversalID(), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)  # wiki, confluence, database, etc.
    enabled = Column(Boolean, default=True)
    connection_details = Column(JSON)  # Store connection configuration
    
    # Relationships
    organization = relationship("Organization", back_populates="rag_connectors")
