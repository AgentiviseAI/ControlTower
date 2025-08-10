"""
RAG Connector schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class RAGConnectorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=100)
    enabled: bool = True
    connection_details: Optional[Dict[str, Any]] = {}


class RAGConnectorCreate(RAGConnectorBase):
    """Create RAG Connector schema - organization_id is injected via dependency"""
    pass


class RAGConnectorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, min_length=1, max_length=100)
    enabled: Optional[bool] = None
    connection_details: Optional[Dict[str, Any]] = None
    # organization_id cannot be changed after creation


class RAGConnector(RAGConnectorBase):
    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
