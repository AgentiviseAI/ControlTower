"""
Authorization middleware for role-based access control
"""
from fastapi import Request, HTTPException, status, Depends
from typing import Tuple
from app.services.authorization_service import AuthorizationService
from app.api.dependencies import get_current_user_id
from app.core.exceptions import ForbiddenError


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
            FastAPI dependency function that returns (user_id, organization_id)
        """
        def check_permission(
            request: Request,
            current_user_id: str = Depends(get_current_user_id)
        ) -> Tuple[str, str]:
            try:
                # Get organization_id from x-organization-id header (consistent with frontend)
                # Using lowercase as it's the HTTP standard and what FastAPI normalizes to
                organization_id = request.headers.get('x-organization-id')
                
                if not organization_id:
                    # Use default test organization for development/testing
                    organization_id = "dev-org-001"
                    print(f"[AUTH] No x-organization-id header found, using default organization: {organization_id}")
                else:
                    print(f"[AUTH] Found organization_id in header: {organization_id}")
                
                print(f"[AUTH] Checking permissions for user: {current_user_id}, org: {organization_id}, resource: {resource}, action: {action}")
                
                # Create authorization service with proper resource management
                with AuthorizationService() as auth_service:
                    # Authorize the request using the already-validated user_id
                    user_id = auth_service.authorize_request(
                        user_id=current_user_id,
                        organization_id=organization_id,
                        resource=resource,
                        action=action
                    )
                    
                    print(f"[AUTH] Authorization successful for user: {user_id}")
                    return user_id, organization_id
                
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
