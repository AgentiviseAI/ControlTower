"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


# Base response schemas
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None


class ListResponse(BaseModel):
    """Generic list response"""
    items: List[Any]
    total: int
    page: Optional[int] = None
    page_size: Optional[int] = None


# AI Agent schemas
class AIAgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: bool = True
    preview_enabled: bool = False
    workflow_id: Optional[str] = None


class AIAgentCreate(AIAgentBase):
    pass


class AIAgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: Optional[bool] = None
    preview_enabled: Optional[bool] = None
    workflow_id: Optional[str] = None


class AIAgent(AIAgentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# MCP Tool schemas
class MCPToolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: bool = True
    endpoint_url: str = Field(..., min_length=1, max_length=500)
    status: str = "active"
    required_permissions: Optional[List[str]] = []
    auth_headers: Optional[Dict[str, str]] = {}


class MCPToolCreate(MCPToolBase):
    pass


class MCPToolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: Optional[bool] = None
    endpoint_url: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[str] = None
    required_permissions: Optional[List[str]] = None
    auth_headers: Optional[Dict[str, str]] = None


class MCPTool(MCPToolBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# LLM schemas
class LLMBase(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    
    # Hosting Environment
    hosting_environment: str = Field(..., description="Where the LLM is hosted")
    
    # Azure AI Foundry fields
    azure_endpoint_url: Optional[str] = Field(None, max_length=500)
    azure_api_key: Optional[str] = None
    azure_deployment_name: Optional[str] = Field(None, max_length=255)
    
    # AWS fields (Bedrock & SageMaker)
    aws_region: Optional[str] = Field(None, max_length=50)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_model_id: Optional[str] = Field(None, max_length=255)
    aws_sagemaker_endpoint_name: Optional[str] = Field(None, max_length=255)
    aws_content_handler_class: Optional[str] = Field(None, max_length=255)
    
    # Google Cloud Vertex AI fields
    gcp_project_id: Optional[str] = Field(None, max_length=255)
    gcp_region: Optional[str] = Field(None, max_length=50)
    gcp_auth_method: Optional[str] = Field(None, max_length=50)
    gcp_service_account_key: Optional[str] = None
    gcp_model_type: Optional[str] = Field(None, max_length=50)
    gcp_model_name: Optional[str] = Field(None, max_length=255)
    gcp_endpoint_id: Optional[str] = Field(None, max_length=255)
    gcp_model_id: Optional[str] = Field(None, max_length=255)
    
    # Custom Deployment fields
    custom_deployment_location: Optional[str] = Field(None, max_length=100)
    custom_llm_provider: Optional[str] = Field(None, max_length=255)
    custom_api_endpoint_url: Optional[str] = Field(None, max_length=500)
    custom_api_compatibility: Optional[str] = Field(None, max_length=50)
    custom_auth_method: Optional[str] = Field(None, max_length=50)
    custom_auth_header_name: Optional[str] = Field(None, max_length=100)
    custom_auth_key_prefix: Optional[str] = Field(None, max_length=50)
    custom_auth_api_key: Optional[str] = None
    
    # General LLM Configuration
    model_name: Optional[str] = Field(None, max_length=255)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    stop_sequences: Optional[str] = None
    
    # System fields
    enabled: bool = True
    status: str = "active"
    usage_stats: Optional[Dict[str, Any]] = {}
    additional_config: Optional[Dict[str, Any]] = {}
    
    @validator('custom_api_compatibility')
    def validate_custom_api_compatibility(cls, v):
        if v == 'custom':
            raise ValueError("Custom API compatibility is not supported yet. Please choose 'openai_compatible', 'anthropic_compatible', 'hf_tgi_compatible', or 'ollama_compatible'.")
        return v


class LLMCreate(LLMBase):
    pass


class LLMUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    hosting_environment: Optional[str] = None
    
    # Azure AI Foundry fields
    azure_endpoint_url: Optional[str] = Field(None, max_length=500)
    azure_api_key: Optional[str] = None
    azure_deployment_name: Optional[str] = Field(None, max_length=255)
    
    # AWS fields
    aws_region: Optional[str] = Field(None, max_length=50)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_model_id: Optional[str] = Field(None, max_length=255)
    aws_sagemaker_endpoint_name: Optional[str] = Field(None, max_length=255)
    aws_content_handler_class: Optional[str] = Field(None, max_length=255)
    
    # Google Cloud fields
    gcp_project_id: Optional[str] = Field(None, max_length=255)
    gcp_region: Optional[str] = Field(None, max_length=50)
    gcp_auth_method: Optional[str] = Field(None, max_length=50)
    gcp_service_account_key: Optional[str] = None
    gcp_model_type: Optional[str] = Field(None, max_length=50)
    gcp_model_name: Optional[str] = Field(None, max_length=255)
    gcp_endpoint_id: Optional[str] = Field(None, max_length=255)
    gcp_model_id: Optional[str] = Field(None, max_length=255)
    
    # Custom Deployment fields
    custom_deployment_location: Optional[str] = Field(None, max_length=100)
    custom_llm_provider: Optional[str] = Field(None, max_length=255)
    custom_api_endpoint_url: Optional[str] = Field(None, max_length=500)
    custom_api_compatibility: Optional[str] = Field(None, max_length=50)
    custom_auth_method: Optional[str] = Field(None, max_length=50)
    custom_auth_header_name: Optional[str] = Field(None, max_length=100)
    custom_auth_key_prefix: Optional[str] = Field(None, max_length=50)
    custom_auth_api_key: Optional[str] = None
    
    # General Configuration
    model_name: Optional[str] = Field(None, max_length=255)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    stop_sequences: Optional[str] = None
    
    enabled: Optional[bool] = None
    status: Optional[str] = None
    usage_stats: Optional[Dict[str, Any]] = None
    additional_config: Optional[Dict[str, Any]] = None
    
    @validator('custom_api_compatibility')
    def validate_custom_api_compatibility(cls, v):
        if v == 'custom':
            raise ValueError("Custom API compatibility is not supported yet. Please choose 'openai_compatible', 'anthropic_compatible', 'hf_tgi_compatible', or 'ollama_compatible'.")
        return v


class LLM(LLMBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# RAG Connector schemas
class RAGConnectorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=100)
    enabled: bool = True
    connection_details: Optional[Dict[str, Any]] = {}


class RAGConnectorCreate(RAGConnectorBase):
    pass


class RAGConnectorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, min_length=1, max_length=100)
    enabled: Optional[bool] = None
    connection_details: Optional[Dict[str, Any]] = None


class RAGConnector(RAGConnectorBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Workflow schemas
class WorkflowNodeBase(BaseModel):
    id: str = Field(..., description="UUID for the node")
    label: str = Field(..., description="Human-readable label for the node")
    type: str = Field(..., description="Type of the node (llm, rag, mcp_tools, etc.)")
    link: Optional[str] = Field(None, description="UUID linking to the actual resource (LLM ID, MCP Tool ID, etc.)")
    position: Dict[str, float] = Field(..., description="Position of the node in the UI")
    config: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration for the node")


class WorkflowNode(WorkflowNodeBase):
    pass


class WorkflowEdgeBase(BaseModel):
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")


class WorkflowEdge(WorkflowEdgeBase):
    pass


class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    agent_id: Optional[str] = None
    nodes: List[WorkflowNode] = []
    edges: List[WorkflowEdge] = []
    status: str = "draft"


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    agent_id: Optional[str] = None
    nodes: Optional[List[WorkflowNode]] = None
    edges: Optional[List[WorkflowEdge]] = None
    status: Optional[str] = None


class Workflow(WorkflowBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Security schemas
class SecurityRoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    status: str = "active"
    permissions: Dict[str, List[str]] = {}


class SecurityRoleCreate(SecurityRoleBase):
    pass


class SecurityRoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[str] = None
    permissions: Optional[Dict[str, List[str]]] = None


class SecurityRole(SecurityRoleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    role: str = Field(..., min_length=1, max_length=100)
    status: str = "active"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=6)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    role: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = None


class User(UserBase):
    id: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Metrics schemas
class MetricCreate(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_type: str = Field(..., pattern=r'^(counter|gauge|histogram)$')
    value: float
    tags: Optional[Dict[str, str]] = {}


class Metric(BaseModel):
    id: str
    metric_name: str
    metric_type: str
    value: float
    tags: Dict[str, str]
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True
