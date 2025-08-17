"""
Authorization middleware for role-based access control
"""
from fastapi import Request, HTTPException, status, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.services.authorization_service import AuthorizationService
from app.core.exceptions import ForbiddenError
from app.core.database import get_db
from app.core.auth_client import AuthServiceClient
import logging

# Security dependencies
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


class AuthorizationMiddleware:
    """Middleware for handling authorization checks"""
    
    @staticmethod
    def create_permission_dependency(resource: str, action: str):
        """
        Create a FastAPI dependency for checking specific permissions
        
        Args:
            resource: Resource type (e.g., 'agents', 'llms', 'workflows')
            action: Action to perform (e.g., 'create', 'read', 'update', 'delete')
        
        Returns:
            FastAPI dependency function that returns (user_id, organization_id) where both are UUIDs
        """
        def check_permission(
            request: Request,
            db: Session = Depends(get_db),
            current_user_id: UUID = Depends(get_current_user_id)
        ) -> Tuple[UUID, UUID]:
            try:
                # Get organization_id from x-organization-id header (consistent with frontend)
                # Using lowercase as it's the HTTP standard and what FastAPI normalizes to
                organization_id_str = request.headers.get('x-organization-id')
                
                if not organization_id_str:
                    # Use default test organization for development/testing
                    organization_id_str = "bb5a9afd-336a-445e-99ce-e81b9d444b76"  # Default UUID format
                    print(f"[AUTH] No x-organization-id header found, using default organization: {organization_id_str}")
                else:
                    print(f"[AUTH] Found organization_id in header: {organization_id_str}")
                
                # Convert string to UUID
                try:
                    organization_id = UUID(organization_id_str)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid organization ID format: {organization_id_str}"
                    )
                
                # Convert user_id to UUID as well (it's already a UUID from get_current_user_id)
                user_id_uuid = current_user_id
                
                print(f"[AUTH] Checking permissions for user: {user_id_uuid}, org: {organization_id}, resource: {resource}, action: {action}")
                
                # Create authorization service using the shared database session
                auth_service = AuthorizationService(db)
                
                # Authorize the request using the already-validated user_id
                user_id = auth_service.authorize_request(
                    user_id=str(current_user_id),  # AuthorizationService expects string
                    organization_id=str(organization_id),  # AuthorizationService expects string
                    resource=resource,
                    action=action
                )
                
                print(f"[AUTH] Authorization successful for user: {user_id}")
                return user_id_uuid, organization_id  # Return both as UUIDs
                
            except ForbiddenError as e:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=str(e)
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Authorization error: {str(e)}"
                )
        
        return check_permission


# Pre-defined permission dependencies for common operations
RequireAgentCreate = AuthorizationMiddleware.create_permission_dependency("agents", "create")
RequireAgentRead = AuthorizationMiddleware.create_permission_dependency("agents", "read")
RequireAgentUpdate = AuthorizationMiddleware.create_permission_dependency("agents", "update")
RequireAgentDelete = AuthorizationMiddleware.create_permission_dependency("agents", "delete")

RequireLLMCreate = AuthorizationMiddleware.create_permission_dependency("llms", "create")
RequireLLMRead = AuthorizationMiddleware.create_permission_dependency("llms", "read")
RequireLLMUpdate = AuthorizationMiddleware.create_permission_dependency("llms", "update")
RequireLLMDelete = AuthorizationMiddleware.create_permission_dependency("llms", "delete")

RequireWorkflowCreate = AuthorizationMiddleware.create_permission_dependency("workflows", "create")
RequireWorkflowRead = AuthorizationMiddleware.create_permission_dependency("workflows", "read")
RequireWorkflowUpdate = AuthorizationMiddleware.create_permission_dependency("workflows", "update")
RequireWorkflowDelete = AuthorizationMiddleware.create_permission_dependency("workflows", "delete")

# MCP Tools permissions
RequireMCPCreate = AuthorizationMiddleware.create_permission_dependency("mcp-tools", "create")
RequireMCPRead = AuthorizationMiddleware.create_permission_dependency("mcp-tools", "read")
RequireMCPUpdate = AuthorizationMiddleware.create_permission_dependency("mcp-tools", "update")
RequireMCPDelete = AuthorizationMiddleware.create_permission_dependency("mcp-tools", "delete")

# RAG Connectors permissions
RequireRAGCreate = AuthorizationMiddleware.create_permission_dependency("rag", "create")
RequireRAGRead = AuthorizationMiddleware.create_permission_dependency("rag", "read")
RequireRAGUpdate = AuthorizationMiddleware.create_permission_dependency("rag", "update")
RequireRAGDelete = AuthorizationMiddleware.create_permission_dependency("rag", "delete")

# Security Roles permissions
RequireRoleCreate = AuthorizationMiddleware.create_permission_dependency("roles", "create")
RequireRoleRead = AuthorizationMiddleware.create_permission_dependency("roles", "read")
RequireRoleUpdate = AuthorizationMiddleware.create_permission_dependency("roles", "update")
RequireRoleDelete = AuthorizationMiddleware.create_permission_dependency("roles", "delete")

# REST API permissions
RequireRestAPICreate = AuthorizationMiddleware.create_permission_dependency("rest-apis", "create")
RequireRestAPIRead = AuthorizationMiddleware.create_permission_dependency("rest-apis", "read")
RequireRestAPIUpdate = AuthorizationMiddleware.create_permission_dependency("rest-apis", "update")
RequireRestAPIDelete = AuthorizationMiddleware.create_permission_dependency("rest-apis", "delete")

# Intent Data permissions
RequireIntentDataRead = AuthorizationMiddleware.create_permission_dependency("intent-data", "read")
