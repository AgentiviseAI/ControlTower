"""
REST API Entity Model
"""
from sqlalchemy import Column, String, Text, Boolean, JSON
from .base import BaseModel
from app.core.database_types import UniversalID


class RestAPI(BaseModel):
    """REST API entity for managing external REST API configurations"""
    __tablename__ = "rest_apis"
    
    # Organization relationship
    organization_id = Column(UniversalID(), nullable=False)
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # API Configuration
    base_url = Column(String(500), nullable=False)  # Base URL of the API
    version = Column(String(50), nullable=True, default="v1")  # API version
    method = Column(String(10), nullable=False, default="GET")  # HTTP method
    resource_path = Column(String(500), nullable=True)  # Resource endpoint path
    
    # Request/Response Configuration
    request_schema = Column(JSON, nullable=True)  # JSON schema for request payload
    response_schema = Column(JSON, nullable=True)  # JSON schema for response
    headers = Column(JSON, nullable=True, default={})  # Default headers
    auth_headers = Column(JSON, nullable=True, default={})  # Authentication headers
    cookies = Column(JSON, nullable=True, default={})  # Required cookies
    query_params = Column(JSON, nullable=True, default={})  # Default query parameters
    path_params = Column(JSON, nullable=True, default={})  # Path parameter definitions
    
    # OpenAPI/Swagger Configuration
    openapi_spec_url = Column(String(500), nullable=True)  # URL to OpenAPI/Swagger spec
    openapi_spec = Column(JSON, nullable=True)  # Cached OpenAPI specification
    operation_id = Column(String(255), nullable=True)  # OpenAPI operation ID
    
    # Metadata and Organization
    tags = Column(JSON, nullable=True, default=[])  # Tags for categorization
    
    # Permissions and Status
    required_permissions = Column(JSON, nullable=True, default=[])  # Required permissions
    enabled = Column(Boolean, default=True, nullable=False)
    status = Column(String(50), default="active", nullable=False)  # active, inactive, error
    
    # Rate Limiting and Timeout
    rate_limit = Column(JSON, nullable=True)  # Rate limiting configuration
    timeout = Column(JSON, nullable=True, default={"connect": 30, "read": 60})  # Timeout settings
    
    # Documentation and Examples
    documentation_url = Column(String(500), nullable=True)  # Link to API documentation
    examples = Column(JSON, nullable=True, default={})  # Request/response examples
    
    def __repr__(self):
        return f"<RestAPI(id='{self.id}', name='{self.name}', method='{self.method}', base_url='{self.base_url}')>"
