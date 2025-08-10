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
async def list_security_roles(
    security_service: SecurityService = Depends(get_security_service)
):
    """List all security roles with full details"""
    try:
        roles = security_service.list_roles()
        return ListResponse(items=roles, total=len(roles))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
