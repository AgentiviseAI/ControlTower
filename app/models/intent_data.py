"""
IntentData model for storing extracted intent information from REST APIs and MCP tools
"""
from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.core.database_types import UniversalID


class IntentData(BaseModel):
    """Model for storing intent data extracted from REST APIs and MCP tools"""
    __tablename__ = "intent_data"
    
    # Basic fields
    organization_id = Column(UniversalID(), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Source information
    source_type = Column(String(50), nullable=False, index=True)  # 'rest_api' or 'mcp_tool'
    source_id = Column(UniversalID(), nullable=False, index=True)  # ID of the source REST API or MCP tool
    
    # Additional metadata
    category = Column(String(100), nullable=True, index=True)
    tags = Column(Text, nullable=True)  # Comma-separated tags
    enabled = Column(Boolean, nullable=False, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="intent_data")
    
    def __repr__(self):
        return f"<IntentData {self.name} ({self.source_type}:{self.source_id})>"
