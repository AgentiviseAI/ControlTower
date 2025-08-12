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
    RAGConnectorRepository, WorkflowRepository, SecurityRoleRepository,
    MetricsRepository, OrganizationRepository
)
from app.services import (
    AIAgentService, MCPToolService, LLMService,
    RAGConnectorService, WorkflowService, SecurityService, OrganizationService
)

# Security
security = HTTPBearer(auto_error=False)
auth_client = AuthServiceClient()
logger = logging.getLogger(__name__)

async def get_current_user_id(
    x_user_id: str = Header(None, alias="X-User-ID"),
    x_service: str = Header(None, alias="X-Service"),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UUID:
    """Validate JWT token or handle internal service calls and return user ID as UUID"""
    # Handle internal service calls (from AuthService, etc.)
    if x_user_id and x_service:
        logger.info(f"Internal service call from {x_service} for user {x_user_id}")
        try:
            return UUID(x_user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format in X-User-ID header"
            )
    
    # Handle regular JWT token validation
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_data = await auth_client.validate_token(credentials.credentials)
        # Use 'id' field for user ID, fallback to 'sub' for JWT standard compatibility
        user_id_str = user_data.get("id") or user_data.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        try:
            return UUID(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format in token"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_organization_id(
    request: Request,
    current_user_id: UUID = Depends(get_current_user_id)
) -> str:
    """Extract organization_id from x-organization-id header"""
    
    organization_id = request.headers.get('x-organization-id')
    
    if not organization_id:
        # Use default test organization for development/testing
        organization_id = "dev-org-001"
        logger.info(f"No x-organization-id header found, using default organization: {organization_id}")
    else:
        logger.info(f"Found organization_id in header: {organization_id}")
    
    return organization_id


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


def get_organization_service(
    repository: OrganizationRepository = Depends(get_organization_repository)
) -> OrganizationService:
    return OrganizationService(repository)
