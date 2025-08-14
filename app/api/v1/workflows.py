"""
Workflow API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import Workflow, WorkflowCreate, WorkflowUpdate, ListResponse
from app.services import WorkflowService
from app.api.dependencies import get_workflow_service
from app.core.exceptions import NotFoundError, ConflictError
from app.middleware.authorization import (
    RequireWorkflowCreate, RequireWorkflowRead, RequireWorkflowUpdate, RequireWorkflowDelete
)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("", response_model=ListResponse)
async def list_workflows(
    auth: tuple = Depends(RequireWorkflowRead),
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """List all workflows for the current organization"""
    user_id, organization_id = auth
    workflows = workflow_service.list_workflows(organization_id)
    return ListResponse(items=workflows, total=len(workflows))


@router.post("", response_model=Workflow, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow: WorkflowCreate,
    auth: tuple = Depends(RequireWorkflowCreate),
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Create a new workflow"""
    user_id, organization_id = auth
    try:
        # Convert the entire workflow to dict first, then extract nested objects
        workflow_dict = workflow.dict()
        
        new_workflow = workflow_service.create_workflow(
            organization_id=organization_id,
            name=workflow_dict['name'],
            description=workflow_dict.get('description'),
            agent_id=workflow_dict.get('agent_id'),
            nodes=workflow_dict.get('nodes', []),
            edges=workflow_dict.get('edges', []),
            status=workflow_dict.get('status', 'draft')
        )
        return new_workflow
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/node-options", response_model=dict)
async def get_workflow_node_options(
    auth: tuple = Depends(RequireWorkflowRead),
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Get available options for workflow nodes (LLMs, RAG connectors, MCP tools) from the organization"""
    user_id, organization_id = auth
    try:
        options = workflow_service.get_node_options(organization_id)
        return options
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(
    workflow_id: str,
    auth: tuple = Depends(RequireWorkflowRead),
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Get a specific workflow"""
    user_id, organization_id = auth
    try:
        workflow = workflow_service.get_workflow(workflow_id)
        return workflow
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow(
    workflow_id: str,
    workflow: WorkflowUpdate,
    auth: tuple = Depends(RequireWorkflowUpdate),
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Update a workflow"""
    user_id, organization_id = auth
    try:
        # Convert Pydantic model to plain dict to avoid serialization issues
        update_data = workflow.dict(exclude_unset=True)
        
        updated_workflow = workflow_service.update_workflow(workflow_id, **update_data)
        return updated_workflow
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: str,
    auth: tuple = Depends(RequireWorkflowDelete),
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Delete a workflow"""
    user_id, organization_id = auth
    try:
        workflow_service.delete_workflow(workflow_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
