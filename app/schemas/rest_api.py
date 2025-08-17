"""
REST API Pydantic schemas for request/response validation
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum


class HTTPMethod(str, Enum):
    """HTTP methods enumeration"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthMethod(str, Enum):
    """Authentication methods enumeration"""
    OBO = "OBO"
    APP_KEY = "AppKey"
    MSI = "MSI"
    APP_ID_SECRET = "AppId+AppSecret"


class RestAPIStatus(str, Enum):
    """REST API status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class TimeoutSettings(BaseModel):
    """Timeout configuration"""
    connect: int = Field(30, ge=1, le=300, description="Connection timeout in seconds")
    read: int = Field(60, ge=1, le=600, description="Read timeout in seconds")


class RateLimitSettings(BaseModel):
    """Rate limiting configuration"""
    requests_per_minute: Optional[int] = Field(None, ge=1, description="Max requests per minute")
    requests_per_hour: Optional[int] = Field(None, ge=1, description="Max requests per hour")
    burst_limit: Optional[int] = Field(None, ge=1, description="Burst request limit")


class ParameterDefinition(BaseModel):
    """Parameter definition for path/query parameters"""
    type: str = Field("string", description="Parameter type")
    description: Optional[str] = Field(None, description="Parameter description")
    required: bool = Field(False, description="Whether parameter is required")
    default: Optional[Union[str, int, float, bool]] = Field(None, description="Default value")


# Request Schemas
class RestAPICreateRequest(BaseModel):
    """Schema for creating a single REST API"""
    name: str = Field(..., min_length=1, max_length=255, description="API name")
    description: Optional[str] = Field(None, description="API description")
    base_url: HttpUrl = Field(..., description="Base URL of the API")
    version: Optional[str] = Field("v1", max_length=50, description="API version")
    method: HTTPMethod = Field(HTTPMethod.GET, description="HTTP method")
    resource_path: Optional[str] = Field(None, max_length=500, description="Resource endpoint path")
    
    # Schemas
    request_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for request payload")
    response_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for response")
    
    # Headers and Authentication
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="Default headers")
    auth_headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="Authentication headers")
    cookies: Optional[Dict[str, str]] = Field(default_factory=dict, description="Required cookies")
    
    # Parameters
    query_params: Optional[Dict[str, ParameterDefinition]] = Field(default_factory=dict, description="Query parameters")
    path_params: Optional[Dict[str, ParameterDefinition]] = Field(default_factory=dict, description="Path parameters")
    
    # OpenAPI Configuration
    openapi_spec_url: Optional[HttpUrl] = Field(None, description="URL to OpenAPI/Swagger spec")
    operation_id: Optional[str] = Field(None, max_length=255, description="OpenAPI operation ID")
    
    # Metadata
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")
    auth_method: Optional[AuthMethod] = Field(None, description="Authentication method")
    enabled: bool = Field(True, description="Whether API is enabled")
    
    # Performance and Documentation
    rate_limit: Optional[RateLimitSettings] = Field(None, description="Rate limiting configuration")
    timeout: Optional[TimeoutSettings] = Field(default_factory=TimeoutSettings, description="Timeout settings")
    documentation_url: Optional[HttpUrl] = Field(None, description="Link to API documentation")
    examples: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Request/response examples")


class RestAPIBulkCreateRequest(BaseModel):
    """Schema for creating multiple REST APIs"""
    apis: List[RestAPICreateRequest] = Field(..., min_items=1, description="List of APIs to create")


class RestAPIFromOpenAPIRequest(BaseModel):
    """Schema for creating REST APIs from OpenAPI specification"""
    spec_url: HttpUrl = Field(..., description="URL to OpenAPI/Swagger specification")
    tags_filter: Optional[List[str]] = Field(None, description="Attach a tag to the APIs to manage them better")


class RestAPIUpdateRequest(BaseModel):
    """Schema for updating a REST API"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="API name")
    description: Optional[str] = Field(None, description="API description")
    base_url: Optional[HttpUrl] = Field(None, description="Base URL of the API")
    version: Optional[str] = Field(None, max_length=50, description="API version")
    method: Optional[HTTPMethod] = Field(None, description="HTTP method")
    resource_path: Optional[str] = Field(None, max_length=500, description="Resource endpoint path")
    
    # Schemas
    request_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for request payload")
    response_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for response")
    
    # Headers and Authentication
    headers: Optional[Dict[str, str]] = Field(None, description="Default headers")
    auth_headers: Optional[Dict[str, str]] = Field(None, description="Authentication headers")
    cookies: Optional[Dict[str, str]] = Field(None, description="Required cookies")
    
    # Parameters
    query_params: Optional[Dict[str, ParameterDefinition]] = Field(None, description="Query parameters")
    path_params: Optional[Dict[str, ParameterDefinition]] = Field(None, description="Path parameters")
    
    # OpenAPI Configuration
    openapi_spec_url: Optional[HttpUrl] = Field(None, description="URL to OpenAPI/Swagger spec")
    operation_id: Optional[str] = Field(None, max_length=255, description="OpenAPI operation ID")
    
    # Metadata
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    auth_method: Optional[AuthMethod] = Field(None, description="Authentication method")
    enabled: Optional[bool] = Field(None, description="Whether API is enabled")
    status: Optional[RestAPIStatus] = Field(None, description="API status")
    
    # Performance and Documentation
    rate_limit: Optional[RateLimitSettings] = Field(None, description="Rate limiting configuration")
    timeout: Optional[TimeoutSettings] = Field(None, description="Timeout settings")
    documentation_url: Optional[HttpUrl] = Field(None, description="Link to API documentation")
    examples: Optional[Dict[str, Any]] = Field(None, description="Request/response examples")


class RestAPIBulkDeleteRequest(BaseModel):
    """Schema for deleting multiple REST APIs"""
    api_ids: List[str] = Field(..., min_items=1, description="List of API IDs to delete")


# Response Schemas
class RestAPIResponse(BaseModel):
    """Schema for REST API response"""
    id: str = Field(..., description="API ID")
    name: str = Field(..., description="API name")
    description: Optional[str] = Field(None, description="API description")
    base_url: str = Field(..., description="Base URL of the API")
    version: str = Field(..., description="API version")
    method: str = Field(..., description="HTTP method")
    resource_path: Optional[str] = Field(None, description="Resource endpoint path")
    
    # Schemas
    request_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for request payload")
    response_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for response")
    
    # Headers and Authentication
    headers: Dict[str, str] = Field(..., description="Default headers")
    auth_headers: Dict[str, str] = Field(..., description="Authentication headers")
    cookies: Dict[str, str] = Field(..., description="Required cookies")
    
    # Parameters
    query_params: Dict[str, Any] = Field(..., description="Query parameters")
    path_params: Dict[str, Any] = Field(..., description="Path parameters")
    
    # OpenAPI Configuration
    openapi_spec_url: Optional[str] = Field(None, description="URL to OpenAPI/Swagger spec")
    openapi_spec: Optional[Dict[str, Any]] = Field(None, description="Cached OpenAPI specification")
    operation_id: Optional[str] = Field(None, description="OpenAPI operation ID")
    
    # Metadata
    tags: List[str] = Field(..., description="Tags for categorization")
    organization_id: str = Field(..., description="Organization ID")
    auth_method: Optional[AuthMethod] = Field(None, description="Authentication method")
    enabled: bool = Field(..., description="Whether API is enabled")
    status: str = Field(..., description="API status")
    
    # Performance and Documentation
    rate_limit: Optional[Dict[str, Any]] = Field(None, description="Rate limiting configuration")
    timeout: Dict[str, Any] = Field(..., description="Timeout settings")
    documentation_url: Optional[str] = Field(None, description="Link to API documentation")
    examples: Dict[str, Any] = Field(..., description="Request/response examples")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RestAPIListResponse(BaseModel):
    """Schema for list of REST APIs"""
    items: List[RestAPIResponse] = Field(..., description="List of REST APIs")
    total: int = Field(..., description="Total number of APIs")


class RestAPIBulkCreateResponse(BaseModel):
    """Schema for bulk create response"""
    created: List[RestAPIResponse] = Field(..., description="Successfully created APIs")
    failed: List[Dict[str, str]] = Field(..., description="Failed API creations with errors")
    total_requested: int = Field(..., description="Total number of APIs requested to create")
    total_created: int = Field(..., description="Total number of APIs successfully created")


class RestAPIBulkDeleteResponse(BaseModel):
    """Schema for bulk delete response"""
    deleted: List[str] = Field(..., description="Successfully deleted API IDs")
    failed: List[str] = Field(..., description="Failed to delete API IDs")
    not_found: List[str] = Field(..., description="API IDs that were not found")
    total_requested: int = Field(..., description="Total number of APIs requested to delete")
    total_deleted: int = Field(..., description="Total number of APIs successfully deleted")


# Query Parameter Schemas
class RestAPIQueryParams(BaseModel):
    """Query parameters for REST API listing"""
    tags: Optional[str] = Field(None, description="Comma-separated list of tags to filter by")
    method: Optional[HTTPMethod] = Field(None, description="Filter by HTTP method")
    status: Optional[RestAPIStatus] = Field(None, description="Filter by status")
    enabled: Optional[bool] = Field(None, description="Filter by enabled status")
    search: Optional[str] = Field(None, description="Search term for API names")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Maximum number of results")
    offset: Optional[int] = Field(0, ge=0, description="Number of results to skip")
    
    @validator('tags', pre=True)
    def parse_tags(cls, v):
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v
