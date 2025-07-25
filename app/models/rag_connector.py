"""
RAG Connector model
"""
from sqlalchemy import Column, String, Boolean, JSON
from .base import BaseModel


class RAGConnector(BaseModel):
    __tablename__ = "rag_connectors"

    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)  # wiki, confluence, database, etc.
    enabled = Column(Boolean, default=True)
    connection_details = Column(JSON)  # Store connection configuration
