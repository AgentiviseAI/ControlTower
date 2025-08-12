"""
Organization API endpoints for ControlTower service
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user_id, get_organization_service
from app.services.organization_service import OrganizationService
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUserResponse,
    UserOrganizationResponse,
    AddUserToOrganizationRequest,
    OrganizationRole
)

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    organization_data: OrganizationCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    service: OrganizationService = Depends(get_organization_service)
):
    """Create a new organization"""
    try:
        organization = service.create_organization(
            organization_data.name,
            organization_data.description,
            current_user_id,  # Already UUID from dependency
            organization_data.type
        )
        return OrganizationResponse.from_orm(organization)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create organization: {str(e)}"
        )

@router.get("/", response_model=List[UserOrganizationResponse])
async def get_user_organizations(
    current_user_id: UUID = Depends(get_current_user_id),
    service: OrganizationService = Depends(get_organization_service)
):
    """Get all organizations for the current user"""
    try:
        organizations = service.get_user_organizations(current_user_id)
        return [UserOrganizationResponse.from_orm(org) for org in organizations]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user organizations: {str(e)}"
        )

@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: str,
    current_user_id: UUID = Depends(get_current_user_id),
    service: OrganizationService = Depends(get_organization_service)
):
    """Get a specific organization by ID"""
    try:
        organization = service.get_organization_by_id(UUID(organization_id))
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        return OrganizationResponse.from_orm(organization)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organization: {str(e)}"
        )

@router.get("/{organization_id}/users", response_model=List[OrganizationUserResponse])
async def get_organization_users(
    organization_id: str,
    current_user_id: UUID = Depends(get_current_user_id),
    service: OrganizationService = Depends(get_organization_service)
):
    """Get all users in an organization"""
    try:
        # Check if current user is an admin or owner of the organization
        user_role = service.get_user_role_in_organization(UUID(organization_id), current_user_id)
        if user_role not in [OrganizationRole.ADMIN, OrganizationRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Admin or Owner role required"
            )
        
        users = service.get_organization_users(UUID(organization_id))
        return [OrganizationUserResponse.from_orm(user) for user in users]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organization users: {str(e)}"
        )

@router.post("/{organization_id}/users", status_code=status.HTTP_201_CREATED)
async def add_user_to_organization(
    organization_id: str,
    request: AddUserToOrganizationRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    service: OrganizationService = Depends(get_organization_service)
):
    """Add a user to an organization"""
    try:
        # Check if current user is an admin or owner of the organization
        user_role = service.get_user_role_in_organization(UUID(organization_id), current_user_id)
        if user_role not in [OrganizationRole.ADMIN, OrganizationRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Admin or Owner role required"
            )
        
        service.add_user_to_organization(
            UUID(organization_id),
            request.user_id,
            request.role
        )
        
        return {"message": "User added to organization successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add user to organization: {str(e)}"
        )

@router.delete("/{organization_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_organization(
    organization_id: str,
    user_id: str,
    current_user_id: UUID = Depends(get_current_user_id),
    service: OrganizationService = Depends(get_organization_service)
):
    """Remove a user from an organization"""
    try:
        # Check if current user is an admin or owner of the organization
        user_role = service.get_user_role_in_organization(UUID(organization_id), current_user_id)
        if user_role not in [OrganizationRole.ADMIN, OrganizationRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Admin or Owner role required"
            )
        
        # Don't allow removing the owner
        target_user_role = service.get_user_role_in_organization(UUID(organization_id), UUID(user_id))
        if target_user_role == OrganizationRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove organization owner"
            )
        
        service.remove_user_from_organization(UUID(organization_id), UUID(user_id))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove user from organization: {str(e)}"
        )
