"""
API Dependencies and utilities
"""
import logging
from typing import Generator
from uuid import UUID
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db, SessionLocal
from app.core.auth_client import AuthServiceClient
from app.repositories import (
    AIAgentRepository, MCPToolRepository, LLMRepository,
    RAGConnectorRepository, WorkflowRepository, WorkflowComponentDefinitionRepository,
    SecurityRoleRepository, MetricsRepository, OrganizationRepository, RestAPIRepository
)
from app.services import (
    AIAgentService, MCPToolService, LLMService,
    RAGConnectorService, WorkflowService, WorkflowComponentDefinitionService,
    SecurityService, OrganizationService, RestAPIService
)

# Security
security = HTTPBearer(auto_error=False)
auth_client = AuthServiceClient()
logger = logging.getLogger(__name__)

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


def get_organization_repository(db: Session = Depends(get_db)) -> OrganizationRepository:
    return OrganizationRepository(db)


def get_rest_api_repository(db: Session = Depends(get_db)) -> RestAPIRepository:
    return RestAPIRepository(db)


def get_workflow_component_definition_repository(db: Session = Depends(get_db)) -> WorkflowComponentDefinitionRepository:
    return WorkflowComponentDefinitionRepository(db)


# Service Dependencies
def get_llm_service(
    repository: LLMRepository = Depends(get_llm_repository)
) -> LLMService:
    return LLMService(repository)


def get_mcp_tool_service(
    repository: MCPToolRepository = Depends(get_mcp_tool_repository)
) -> MCPToolService:
    return MCPToolService(repository)


def get_rag_connector_service(
    repository: RAGConnectorRepository = Depends(get_rag_connector_repository)
) -> RAGConnectorService:
    return RAGConnectorService(repository)


def get_rest_api_service(
    repository: RestAPIRepository = Depends(get_rest_api_repository)
) -> RestAPIService:
    return RestAPIService(repository)


def get_workflow_service(
    repository: WorkflowRepository = Depends(get_workflow_repository),
    llm_service: LLMService = Depends(get_llm_service),
    mcp_service: MCPToolService = Depends(get_mcp_tool_service),
    rag_service: RAGConnectorService = Depends(get_rag_connector_service),
    rest_api_service: RestAPIService = Depends(get_rest_api_service)
) -> WorkflowService:
    return WorkflowService(repository, llm_service, mcp_service, rag_service, rest_api_service)


def get_ai_agent_service(
    repository: AIAgentRepository = Depends(get_ai_agent_repository)
) -> AIAgentService:
    return AIAgentService(repository)


def get_security_service(
    role_repository: SecurityRoleRepository = Depends(get_security_role_repository)
) -> SecurityService:
    return SecurityService(role_repository)


def get_organization_service(
    repository: OrganizationRepository = Depends(get_organization_repository)
) -> OrganizationService:
    return OrganizationService(repository)


def get_workflow_component_definition_service(
    repository: WorkflowComponentDefinitionRepository = Depends(get_workflow_component_definition_repository)
) -> WorkflowComponentDefinitionService:
    return WorkflowComponentDefinitionService(repository)
