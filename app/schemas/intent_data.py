"""
IntentData schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class IntentDataBase(BaseModel):
    """Base schema for IntentData"""
    name: str = Field(..., min_length=1, max_length=255, description="Intent name")
    description: Optional[str] = Field(None, description="Intent description")
    source_type: str = Field(..., description="Source type: 'rest_api' or 'mcp_tool'")
    source_id: str = Field(..., description="ID of the source REST API or MCP tool")
    category: Optional[str] = Field(None, max_length=100, description="Intent category")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    enabled: bool = Field(True, description="Whether the intent is enabled")


class IntentDataCreate(IntentDataBase):
    """Schema for creating IntentData"""
    pass


class IntentDataUpdate(BaseModel):
    """Schema for updating IntentData"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Intent name")
    description: Optional[str] = Field(None, description="Intent description")
    category: Optional[str] = Field(None, max_length=100, description="Intent category")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    enabled: Optional[bool] = Field(None, description="Whether the intent is enabled")
    # source_type and source_id cannot be updated


class IntentDataResponse(IntentDataBase):
    """Schema for IntentData responses"""
    id: str = Field(..., description="Intent data UUID")
    organization_id: str = Field(..., description="Organization UUID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class IntentDataListResponse(BaseModel):
    """Schema for listing IntentData"""
    items: List[IntentDataResponse] = Field(..., description="List of intent data")
    total: int = Field(..., description="Total number of intent data records")


class IntentDataBulkCreate(BaseModel):
    """Schema for bulk creating IntentData"""
    intent_data: List[IntentDataCreate] = Field(..., description="List of intent data to create")


class IntentDataSync(BaseModel):
    """Schema for syncing IntentData from a source"""
    source_type: str = Field(..., description="Source type (rest_api, mcp_tool)")
    source_id: str = Field(..., description="Source ID")
    intents: List[Dict[str, Any]] = Field(..., description="List of intent data to sync")


class IntentDataBulkCreateRequest(BaseModel):
    """Schema for bulk creating IntentData"""
    intent_data: List[IntentDataCreate] = Field(..., description="List of intent data to create")


class IntentDataBulkCreateResponse(BaseModel):
    """Schema for bulk create IntentData response"""
    created: List[IntentDataResponse] = Field(..., description="Successfully created intent data")
    failed: List[dict] = Field(..., description="Failed intent data with error messages")
    total_requested: int = Field(..., description="Total number of intent data requested")
    total_created: int = Field(..., description="Total number of intent data created")
