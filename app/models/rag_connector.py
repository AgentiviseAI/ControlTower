"""
RAG Connector model with organization support
"""
from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class RAGConnector(BaseModel):
    __tablename__ = "rag_connectors"

    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)  # wiki, confluence, database, etc.
    enabled = Column(Boolean, default=True)
    connection_details = Column(JSON)  # Store connection configuration
    
    # Relationships
    organization = relationship("Organization", back_populates="rag_connectors")
