"""
Database models for the AI Platform
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, Integer, Float
from app.core.database import Base
import uuid
from datetime import datetime
from typing import Optional, Dict, Any


class AIAgent(Base):
    __tablename__ = "ai_agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    preview_enabled = Column(Boolean, default=False)
    workflow_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MCPTool(Base):
    __tablename__ = "mcp_tools"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    endpoint_url = Column(String(500), nullable=False)
    status = Column(String(50), default="active")
    required_permissions = Column(JSON)
    auth_headers = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LLM(Base):
    __tablename__ = "llms"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Hosting Environment
    hosting_environment = Column(String(100), nullable=False)  # azure_ai_foundry, aws_bedrock, aws_sagemaker, gcp_vertex_ai, custom_deployment
    
    # Azure AI Foundry fields
    azure_endpoint_url = Column(String(500))
    azure_api_key = Column(Text)  # Encrypted
    azure_deployment_name = Column(String(255))
    
    # AWS fields (Bedrock & SageMaker)
    aws_region = Column(String(50))
    aws_access_key_id = Column(Text)  # Encrypted
    aws_secret_access_key = Column(Text)  # Encrypted
    aws_model_id = Column(String(255))  # For Bedrock
    aws_sagemaker_endpoint_name = Column(String(255))  # For SageMaker
    aws_content_handler_class = Column(String(255))  # For SageMaker
    
    # Google Cloud Vertex AI fields
    gcp_project_id = Column(String(255))
    gcp_region = Column(String(50))
    gcp_auth_method = Column(String(50))  # adc, service_account_key
    gcp_service_account_key = Column(Text)  # Encrypted JSON
    gcp_model_type = Column(String(50))  # foundation, custom_endpoint
    gcp_model_name = Column(String(255))  # For foundation models
    gcp_endpoint_id = Column(String(255))  # For custom endpoints
    gcp_model_id = Column(String(255))  # For custom endpoints
    
    # Custom Deployment fields
    custom_deployment_location = Column(String(100))  # on_premise, azure_compute, aws_compute, gcp_compute, other_cloud
    custom_llm_provider = Column(String(255))
    custom_api_endpoint_url = Column(String(500))
    custom_api_compatibility = Column(String(50))  # openai_compatible, huggingface_tgi, ollama, custom
    custom_auth_method = Column(String(50))  # none, api_key_header, bearer_token, other
    custom_auth_header_name = Column(String(100))
    custom_auth_key_prefix = Column(String(50))
    custom_auth_api_key = Column(Text)  # Encrypted
    
    # General LLM Configuration
    model_name = Column(String(255))  # Internal tracking name
    temperature = Column(Float)
    max_tokens = Column(Integer)
    top_p = Column(Float)
    stop_sequences = Column(Text)  # Comma-separated
    
    # System fields
    enabled = Column(Boolean, default=True)
    status = Column(String(50), default="active")
    usage_stats = Column(JSON)
    additional_config = Column(JSON)  # For any extra configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RAGConnector(Base):
    __tablename__ = "rag_connectors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)  # wiki, confluence, database, etc.
    enabled = Column(Boolean, default=True)
    connection_details = Column(JSON)  # Store connection configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    agent_id = Column(String(36), nullable=True)  # Link to agent
    nodes = Column(JSON)  # Store workflow configuration
    edges = Column(JSON)  # Store workflow edges/connections
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SecurityRole(Base):
    __tablename__ = "security_roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    status = Column(String(50), default="active")
    permissions = Column(JSON)  # Store role permissions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # Should be hashed
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(100), nullable=False)
    status = Column(String(50), default="active")
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Metrics(Base):
    __tablename__ = "metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(100), nullable=False)
    metric_type = Column(String(50), nullable=False)  # counter, gauge, histogram
    value = Column(Float, nullable=False)
    tags = Column(JSON)  # Additional metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
