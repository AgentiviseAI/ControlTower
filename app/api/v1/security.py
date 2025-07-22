"""
Security API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import User, UserCreate, UserUpdate, SecurityRole, SecurityRoleCreate, ListResponse
from app.services import SecurityService
from app.api.dependencies import get_security_service, verify_token
from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter(prefix="/security", tags=["Security"])


@router.get("/users", response_model=ListResponse)
async def list_users(
    token: str = Depends(verify_token),
    security_service: SecurityService = Depends(get_security_service)
):
    """List all users"""
    users = security_service.get_all_users()
    return ListResponse(items=users, total=len(users))


@router.post("/users", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    token: str = Depends(verify_token),
    security_service: SecurityService = Depends(get_security_service)
):
    """Create a new user"""
    try:
        user_data = user.dict()
        created_user = security_service.create_user(user_data)
        return {"user": created_user, "message": "User created successfully"}
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    token: str = Depends(verify_token),
    security_service: SecurityService = Depends(get_security_service)
):
    """Get a specific user"""
    try:
        user = security_service.get_user(user_id)
        return user
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/users/{user_id}", response_model=dict)
async def update_user(
    user_id: str,
    user: UserUpdate,
    token: str = Depends(verify_token),
    security_service: SecurityService = Depends(get_security_service)
):
    """Update user details"""
    try:
        user_data = user.dict(exclude_unset=True)
        updated_user = security_service.update_user(user_id, user_data)
        return {"user": updated_user, "message": "User updated successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    token: str = Depends(verify_token),
    security_service: SecurityService = Depends(get_security_service)
):
    """Delete a user"""
    try:
        security_service.delete_user(user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/roles", response_model=ListResponse)
async def list_security_roles(
    token: str = Depends(verify_token)
):
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
                "pipelines": ["read", "write", "delete"],
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
                "pipelines": ["read", "write"], 
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
                "pipelines": ["read"],
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
    token: str = Depends(verify_token),
    security_service: SecurityService = Depends(get_security_service)
):
    """Create a new security role"""
    try:
        role_data = role.dict()
        created_role = security_service.create_role(role_data)
        return created_role
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
