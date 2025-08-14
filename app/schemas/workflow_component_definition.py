"""
Workflow Component Definition Schemas
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator


class PortDefinition(BaseModel):
    """Schema for input/output port definitions"""
    name: str = Field(..., description="Port name")
    type: str = Field(..., description="Data type expected/provided")
    description: Optional[str] = Field(None, description="Port description")
    required: bool = Field(True, description="Whether this port is required")
    multiple: bool = Field(False, description="Whether multiple connections are allowed")


class WorkflowComponentDefinitionBase(BaseModel):
    """Base schema for workflow component definitions"""
    name: str = Field(..., min_length=1, max_length=255, description="Component display name")
    component_id: str = Field(..., min_length=1, max_length=100, description="Unique component identifier")
    category: str = Field(..., min_length=1, max_length=100, description="Component category")
    description: Optional[str] = Field(None, description="Component description")
    icon_name: Optional[str] = Field(None, max_length=100, description="Ant Design icon name")
    color: Optional[str] = Field(None, max_length=20, description="Hex color code")
    config_schema: Optional[Dict[str, Any]] = Field(default_factory=dict, description="JSON schema for configuration")
    default_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Default configuration values")
    input_ports: Optional[List[PortDefinition]] = Field(default_factory=list, description="Input port definitions")
    output_ports: Optional[List[PortDefinition]] = Field(default_factory=list, description="Output port definitions")
    version: Optional[str] = Field("1.0.0", max_length=20, description="Component version")
    tags: Optional[List[str]] = Field(default_factory=list, description="Component tags")
    enabled: bool = Field(True, description="Whether component is enabled")
    sort_order: int = Field(0, description="Sort order within category")
    implementation_class: Optional[str] = Field(None, max_length=255, description="Python implementation class")
    requirements: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Component requirements")
    
    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError('Color must be a valid hex code starting with #')
        return v
    
    @validator('component_id')
    def validate_component_id(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Component ID must contain only alphanumeric characters, underscores, and hyphens')
        return v


class WorkflowComponentDefinitionCreateRequest(WorkflowComponentDefinitionBase):
    """Schema for creating workflow component definitions"""
    pass


class WorkflowComponentDefinitionUpdateRequest(BaseModel):
    """Schema for updating workflow component definitions"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Component display name")
    component_id: Optional[str] = Field(None, min_length=1, max_length=100, description="Unique component identifier")
    category: Optional[str] = Field(None, min_length=1, max_length=100, description="Component category")
    description: Optional[str] = Field(None, description="Component description")
    icon_name: Optional[str] = Field(None, max_length=100, description="Ant Design icon name")
    color: Optional[str] = Field(None, max_length=20, description="Hex color code")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for configuration")
    default_config: Optional[Dict[str, Any]] = Field(None, description="Default configuration values")
    input_ports: Optional[List[PortDefinition]] = Field(None, description="Input port definitions")
    output_ports: Optional[List[PortDefinition]] = Field(None, description="Output port definitions")
    version: Optional[str] = Field(None, max_length=20, description="Component version")
    tags: Optional[List[str]] = Field(None, description="Component tags")
    enabled: Optional[bool] = Field(None, description="Whether component is enabled")
    sort_order: Optional[int] = Field(None, description="Sort order within category")
    implementation_class: Optional[str] = Field(None, max_length=255, description="Python implementation class")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Component requirements")
    
    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError('Color must be a valid hex code starting with #')
        return v
    
    @validator('component_id')
    def validate_component_id(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Component ID must contain only alphanumeric characters, underscores, and hyphens')
        return v


class WorkflowComponentDefinitionResponse(WorkflowComponentDefinitionBase):
    """Schema for workflow component definition responses"""
    id: str = Field(..., description="Component UUID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class WorkflowComponentDefinitionListResponse(BaseModel):
    """Schema for listing workflow component definitions"""
    items: List[WorkflowComponentDefinitionResponse] = Field(..., description="List of components")
    total: int = Field(..., description="Total number of components")


class WorkflowComponentBulkCreateRequest(BaseModel):
    """Schema for bulk creating workflow component definitions"""
    components: List[WorkflowComponentDefinitionCreateRequest] = Field(..., description="List of components to create")


class WorkflowComponentBulkCreateResponse(BaseModel):
    """Schema for bulk create response"""
    created: List[WorkflowComponentDefinitionResponse] = Field(..., description="Successfully created components")
    failed: List[Dict[str, str]] = Field(..., description="Failed component creations with errors")
    total_requested: int = Field(..., description="Total number of components requested")
    total_created: int = Field(..., description="Total number of components successfully created")


class CategorySortOrderUpdateRequest(BaseModel):
    """Schema for updating sort orders within a category"""
    category: str = Field(..., description="Category name")
    component_orders: List[Dict[str, Union[str, int]]] = Field(
        ..., 
        description="List of component_id and sort_order pairs"
    )


class ComponentSearchRequest(BaseModel):
    """Schema for component search requests"""
    search_term: Optional[str] = Field(None, description="Search term for name/description")
    category: Optional[str] = Field(None, description="Filter by category")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    enabled_only: bool = Field(True, description="Only return enabled components")
