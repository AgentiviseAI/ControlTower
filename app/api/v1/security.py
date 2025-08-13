"""
Security and RBAC API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Tuple
from uuid import UUID

from app.schemas import SecurityRole, SecurityRoleCreate, ListResponse
from app.services import SecurityService
from app.api.dependencies import get_security_service
from app.core.exceptions import NotFoundError, ConflictError
from app.middleware.authorization import RequireRoleRead, RequireRoleCreate

router = APIRouter(prefix="/security", tags=["security"])


@router.get("/roles", response_model=ListResponse)
async def list_security_roles(
    auth: Tuple[UUID, UUID] = Depends(RequireRoleRead),
    security_service: SecurityService = Depends(get_security_service)
):
    """List all security roles with full details"""
    user_id, organization_id = auth
    try:
        # Pass organization_id UUID to get system roles + organization-specific roles
        roles = security_service.list_roles(organization_id)
        return ListResponse(items=roles, total=len(roles))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/roles/organization", response_model=SecurityRole, status_code=status.HTTP_201_CREATED)
async def create_organization_role(
    role: SecurityRoleCreate,
    auth: Tuple[UUID, UUID] = Depends(RequireRoleCreate),
    security_service: SecurityService = Depends(get_security_service)
):
    """Create a new organization-specific security role"""
    user_id, organization_id = auth
    try:
        role_data = role.dict()
        # Pass organization_id UUID to populate organization_id field
        created_role = security_service.create_organization_role(role_data, organization_id)
        return created_role
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
