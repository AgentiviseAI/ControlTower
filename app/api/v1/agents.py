"""
AI Agents API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import AIAgent, AIAgentCreate, AIAgentUpdate, ListResponse
from app.services import AIAgentService
from app.api.dependencies import get_ai_agent_service, verify_token
from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter(prefix="/agents", tags=["AI Agents"])


@router.get("", response_model=ListResponse)
async def list_agents(
    token: str = Depends(verify_token),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """List all AI agents"""
    agents = agent_service.get_all_agents()
    return ListResponse(items=agents, total=len(agents))


@router.post("", response_model=AIAgent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent: AIAgentCreate,
    token: str = Depends(verify_token),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Create a new AI agent"""
    try:
        new_agent = agent_service.create_agent(
            name=agent.name,
            description=agent.description,
            enabled=agent.enabled,
            preview_enabled=agent.preview_enabled
        )
        return new_agent
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{agent_id}", response_model=AIAgent)
async def get_agent(
    agent_id: str,
    token: str = Depends(verify_token),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Get a specific AI agent"""
    try:
        agent = agent_service.get_agent(agent_id)
        return agent
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{agent_id}", response_model=AIAgent)
async def update_agent(
    agent_id: str,
    agent: AIAgentUpdate,
    token: str = Depends(verify_token),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Update an AI agent"""
    try:
        update_data = agent.dict(exclude_unset=True)
        updated_agent = agent_service.update_agent(agent_id, **update_data)
        return updated_agent
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    token: str = Depends(verify_token),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Delete an AI agent"""
    try:
        agent_service.delete_agent(agent_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/enabled", response_model=ListResponse)
async def list_enabled_agents(
    token: str = Depends(verify_token),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """List all enabled AI agents"""
    agents = agent_service.get_enabled_agents()
    return ListResponse(items=agents, total=len(agents))
