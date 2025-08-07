"""
API Dependencies and utilities
"""
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.repositories import (
    AIAgentRepository, MCPToolRepository, LLMRepository,
    RAGConnectorRepository, WorkflowRepository, SecurityRoleRepository,
    MetricsRepository
)
from app.services import (
    AIAgentService, MCPToolService, LLMService,
    RAGConnectorService, WorkflowService, SecurityService
)


# Repository Dependencies
def get_ai_agent_repository(db: Session = Depends(get_db)) -> AIAgentRepository:
    return AIAgentRepository(db)


def get_mcp_tool_repository(db: Session = Depends(get_db)) -> MCPToolRepository:
    return MCPToolRepository(db)


def get_llm_repository(db: Session = Depends(get_db)) -> LLMRepository:
    return LLMRepository(db)


def get_rag_connector_repository(db: Session = Depends(get_db)) -> RAGConnectorRepository:
    return RAGConnectorRepository(db)


def get_workflow_repository(db: Session = Depends(get_db)) -> WorkflowRepository:
    return WorkflowRepository(db)


def get_security_role_repository(db: Session = Depends(get_db)) -> SecurityRoleRepository:
    return SecurityRoleRepository(db)


def get_metrics_repository(db: Session = Depends(get_db)) -> MetricsRepository:
    return MetricsRepository(db)


# Service Dependencies
def get_workflow_service(
    repository: WorkflowRepository = Depends(get_workflow_repository),
    llm_repository: LLMRepository = Depends(get_llm_repository),
    mcp_repository: MCPToolRepository = Depends(get_mcp_tool_repository),
    rag_repository: RAGConnectorRepository = Depends(get_rag_connector_repository)
) -> WorkflowService:
    return WorkflowService(repository, llm_repository, mcp_repository, rag_repository)


def get_llm_service(
    repository: LLMRepository = Depends(get_llm_repository)
) -> LLMService:
    return LLMService(repository)


def get_ai_agent_service(
    repository: AIAgentRepository = Depends(get_ai_agent_repository)
) -> AIAgentService:
    return AIAgentService(repository)


def get_mcp_tool_service(
    repository: MCPToolRepository = Depends(get_mcp_tool_repository)
) -> MCPToolService:
    return MCPToolService(repository)


def get_rag_connector_service(
    repository: RAGConnectorRepository = Depends(get_rag_connector_repository)
) -> RAGConnectorService:
    return RAGConnectorService(repository)


def get_security_service(
    role_repository: SecurityRoleRepository = Depends(get_security_role_repository)
) -> SecurityService:
    return SecurityService(role_repository)
