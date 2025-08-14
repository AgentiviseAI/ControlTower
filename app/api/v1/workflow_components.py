"""
Workflow Component Definition API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.dependencies import get_workflow_component_definition_service
from app.services.workflow_component_definition_service import WorkflowComponentDefinitionService
from app.middleware.authorization import RequireWorkflowRead
from app.schemas.workflow_component_definition import (
    WorkflowComponentDefinitionResponse, WorkflowComponentDefinitionListResponse
)
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/workflow-components", tags=["Workflow Components"])


@router.get("/", response_model=WorkflowComponentDefinitionListResponse)
async def list_workflow_components(
    auth: tuple = Depends(RequireWorkflowRead),
    service: WorkflowComponentDefinitionService = Depends(get_workflow_component_definition_service),
    category: Optional[str] = Query(None, description="Filter by category"),
    enabled_only: bool = Query(True, description="Only return enabled components"),
    search: Optional[str] = Query(None, description="Search term for name/description"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags to filter by")
):
    """List all workflow component definitions with optional filters"""
    user_id, organization_id = auth
    
    try:
        if search:
            components = service.search_components(search)
        elif tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            components = service.get_components_by_tags(tag_list)
        elif category:
            components = service.list_components_by_category(category)
        else:
            components = service.list_components(enabled_only=enabled_only)
        
        return WorkflowComponentDefinitionListResponse(
            items=[WorkflowComponentDefinitionResponse(**comp) for comp in components],
            total=len(components)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/categories")
async def get_categories(
    auth: tuple = Depends(RequireWorkflowRead),
    service: WorkflowComponentDefinitionService = Depends(get_workflow_component_definition_service)
):
    """Get all unique component categories"""
    user_id, organization_id = auth
    
    try:
        categories = service.get_categories()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{component_id}", response_model=WorkflowComponentDefinitionResponse)
async def get_workflow_component(
    component_id: str,
    auth: tuple = Depends(RequireWorkflowRead),
    service: WorkflowComponentDefinitionService = Depends(get_workflow_component_definition_service)
):
    """Get a specific workflow component definition by component_id"""
    user_id, organization_id = auth
    
    try:
        component = service.get_component(component_id)
        return WorkflowComponentDefinitionResponse(**component)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
