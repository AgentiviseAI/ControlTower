"""
LLM schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime


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
