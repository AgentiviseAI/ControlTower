"""
AI Agents API endpoints with authorization
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import AIAgent, AIAgentCreate, AIAgentUpdate, Workflow, ListResponse
from app.services import AIAgentService, WorkflowService
from app.api.dependencies import get_ai_agent_service, get_workflow_service, get_current_user_id, get_current_organization_id
from app.core.exceptions import NotFoundError, ConflictError
from app.middleware.authorization import (
    RequireAgentCreate, RequireAgentRead, RequireAgentUpdate, RequireAgentDelete,
    RequireWorkflowRead
)

router = APIRouter(prefix="/agents", tags=["AI Agents"])


@router.get("", response_model=ListResponse)
async def list_agents(
    auth: tuple = Depends(RequireAgentRead),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """List all AI agents for the current user/organization"""
    user_id, organization_id = auth
    agents = agent_service.list_agents(organization_id)
    return ListResponse(items=agents, total=len(agents))


@router.post("", response_model=AIAgent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent: AIAgentCreate,
    user_id: str = Depends(get_current_user_id),
    organization_id: str = Depends(get_current_organization_id),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Create a new AI agent"""
    try:
        created_agent = agent_service.create_agent(
            name=agent.name,
            description=agent.description,
            enabled=agent.enabled,
            preview_enabled=agent.preview_enabled,
            workflow_id=agent.workflow_id,
            organization_id=organization_id  # Injected from header
        )
        return created_agent
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{agent_id}", response_model=AIAgent)
async def get_agent(
    agent_id: str,
    auth: tuple = Depends(RequireAgentRead),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Get a specific AI agent"""
    user_id, organization_id = auth
    try:
        agent = agent_service.get_agent(agent_id, organization_id)
        return agent
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{agent_id}", response_model=AIAgent)
async def update_agent(
    agent_id: str,
    agent: AIAgentUpdate,
    auth: tuple = Depends(RequireAgentUpdate),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Update an AI agent"""
    user_id, organization_id = auth
    try:
        update_data = agent.dict(exclude_unset=True)
        updated_agent = agent_service.update_agent(agent_id, organization_id, **update_data)
        return updated_agent
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    auth: tuple = Depends(RequireAgentDelete),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Delete an AI agent"""
    user_id, organization_id = auth
    try:
        agent_service.delete_agent(agent_id, organization_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{agent_id}/workflows", response_model=ListResponse)
async def get_agent_workflows(
    agent_id: str,
    auth: tuple = Depends(RequireWorkflowRead),
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflows for an AI agent"""
    user_id, organization_id = auth
    try:
        workflows = workflow_service.get_workflows_by_agent(agent_id, organization_id)
        return ListResponse(items=workflows, total=len(workflows))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{agent_id}/status", response_model=dict)
async def get_agent_status(
    agent_id: str,
    auth: tuple = Depends(RequireAgentRead),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Get status of an AI agent"""
    user_id, organization_id = auth
    try:
        status_info = agent_service.get_agent_status(agent_id, organization_id)
        return status_info
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{agent_id}/execute", response_model=dict)
async def execute_agent(
    agent_id: str,
    request_data: dict,
    auth: tuple = Depends(RequireAgentRead),  # Execute requires read permissions
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Execute an AI agent"""
    user_id, organization_id = auth
    try:
        result = agent_service.execute_agent(agent_id, organization_id, request_data)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{agent_id}/training/start", response_model=dict)
async def start_agent_training(
    agent_id: str,
    training_data: dict,
    auth: tuple = Depends(RequireAgentUpdate),  # Training requires update permissions
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Start training for an AI agent"""
    user_id, organization_id = auth
    try:
        result = agent_service.start_training(agent_id, organization_id, training_data)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
