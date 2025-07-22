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
    pipeline_id: Optional[str] = None


class AIAgentCreate(AIAgentBase):
    pass


class AIAgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: Optional[bool] = None
    preview_enabled: Optional[bool] = None
    pipeline_id: Optional[str] = None


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
    model_name: str = Field(..., min_length=1, max_length=255)
    provider: str = Field(..., min_length=1, max_length=100)
    enabled: bool = True
    endpoint_url: str = Field(..., min_length=1, max_length=500)
    status: str = "active"
    usage_stats: Optional[Dict[str, Any]] = {}
    config: Optional[Dict[str, Any]] = {}


class LLMCreate(LLMBase):
    pass


class LLMUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    model_name: Optional[str] = Field(None, min_length=1, max_length=255)
    provider: Optional[str] = Field(None, min_length=1, max_length=100)
    enabled: Optional[bool] = None
    endpoint_url: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[str] = None
    usage_stats: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None


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


# Pipeline schemas
class PipelineComponentBase(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    config: Dict[str, Any] = {}


class PipelineComponent(PipelineComponentBase):
    pass


class PipelineEdgeBase(BaseModel):
    source_component_id: str
    target_component_id: str


class PipelineEdge(PipelineEdgeBase):
    pass


class PipelineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    nodes: List[PipelineComponent] = []
    edges: List[PipelineEdge] = []
    status: str = "draft"


class PipelineCreate(PipelineBase):
    pass


class PipelineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    nodes: Optional[List[PipelineComponent]] = None
    edges: Optional[List[PipelineEdge]] = None
    status: Optional[str] = None


class Pipeline(PipelineBase):
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
