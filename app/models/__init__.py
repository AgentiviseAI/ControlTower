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
    pipeline_id = Column(String(36), nullable=True)
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
    model_name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)
    enabled = Column(Boolean, default=True)
    endpoint_url = Column(String(500), nullable=False)
    status = Column(String(50), default="active")
    usage_stats = Column(JSON)
    config = Column(JSON)
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


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    nodes = Column(JSON)  # Store pipeline configuration
    edges = Column(JSON)  # Store pipeline edges/connections
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
