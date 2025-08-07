"""
Security and RBAC API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.schemas import SecurityRole, SecurityRoleCreate, ListResponse
from app.services import SecurityService
from app.api.dependencies import get_security_service
from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter(prefix="/security", tags=["security"])


@router.get("/roles", response_model=ListResponse)
async def list_security_roles():
    """List all security roles with full details"""
    # Return default roles for now
    default_roles = [
        {
            "id": "admin",
            "name": "Administrator", 
            "description": "Full system access with all permissions",
            "permissions": {
                "agents": ["read", "write", "delete"],
                "llms": ["read", "write", "delete"],
                "workflows": ["read", "write", "delete"],
                "mcp_tools": ["read", "write", "delete"],
                "rag": ["read", "write", "delete"],
                "security": ["read", "write", "delete"],
                "metrics": ["read"]
            },
            "status": "active",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        },
        {
            "id": "user",
            "name": "Standard User",
            "description": "Basic access to view and manage own resources",
            "permissions": {
                "agents": ["read", "write"],
                "llms": ["read"],
                "workflows": ["read", "write"], 
                "mcp_tools": ["read"],
                "rag": ["read"],
                "security": ["read"],
                "metrics": ["read"]
            },
            "status": "active",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        },
        {
            "id": "viewer",
            "name": "Viewer",
            "description": "Read-only access to system resources",
            "permissions": {
                "agents": ["read"],
                "llms": ["read"],
                "workflows": ["read"],
                "mcp_tools": ["read"],
                "rag": ["read"],
                "security": ["read"],
                "metrics": ["read"]
            },
            "status": "active",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }
    ]
    return ListResponse(items=default_roles, total=len(default_roles))


@router.post("/roles", response_model=SecurityRole, status_code=status.HTTP_201_CREATED)
async def create_security_role(
    role: SecurityRoleCreate,
    security_service: SecurityService = Depends(get_security_service)
):
    """Create a new security role"""
    try:
        role_data = role.dict()
        created_role = security_service.create_role(role_data)
        return created_role
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
