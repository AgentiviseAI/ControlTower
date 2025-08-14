"""
AI Agents API endpoints with authorization
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import AIAgent, AIAgentCreate, AIAgentUpdate, Workflow, WorkflowCreate, ListResponse
from app.services import AIAgentService, WorkflowService, LLMService
from app.api.dependencies import get_ai_agent_service, get_workflow_service, get_llm_service
from app.core.exceptions import NotFoundError, ConflictError
from app.middleware.authorization import (
    RequireAgentCreate, RequireAgentRead, RequireAgentUpdate, RequireAgentDelete,
    RequireWorkflowRead, RequireWorkflowCreate
)
from app.middleware.transaction import get_transaction_manager, TransactionManager

router = APIRouter(prefix="/agents", tags=["AI Agents"])


@router.get("", response_model=ListResponse)
async def list_agents(
    auth: tuple = Depends(RequireAgentRead),
    agent_service: AIAgentService = Depends(get_ai_agent_service),
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """List all AI agents for the current user/organization with their default workflow IDs"""
    user_id, organization_id = auth
    agents = agent_service.list_agents(organization_id, workflow_service)
    return ListResponse(items=agents, total=len(agents))


@router.post("", response_model=AIAgent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent: AIAgentCreate,
    auth: tuple = Depends(RequireAgentCreate),
    agent_service: AIAgentService = Depends(get_ai_agent_service),
    workflow_service: WorkflowService = Depends(get_workflow_service),
    llm_service: LLMService = Depends(get_llm_service),
    transaction_manager: TransactionManager = Depends(get_transaction_manager)
):
    """Create a new AI agent with a default workflow atomically"""
    user_id, organization_id = auth
    
    try:
        # Convert Pydantic model to dict for service layer
        agent_data = {
            'name': agent.name,
            'description': agent.description,
            'enabled': agent.enabled,
            'preview_enabled': agent.preview_enabled
        }
        
        # Execute the orchestrated agent creation atomically
        def atomic_agent_creation():
            return agent_service.create_agent_with_default_workflow(
                agent_data=agent_data,
                organization_id=organization_id,
                workflow_service=workflow_service,
                llm_service=llm_service
            )
        
        result = transaction_manager.execute_atomic([atomic_agent_creation])
        return result
        
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{agent_id}", response_model=AIAgent)
async def get_agent(
    agent_id: str,
    auth: tuple = Depends(RequireAgentRead),
    agent_service: AIAgentService = Depends(get_ai_agent_service),
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Get a specific AI agent with its default workflow ID"""
    user_id, organization_id = auth
    try:
        agent = agent_service.get_agent(UUID(agent_id), organization_id, workflow_service)
        return agent
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid agent ID format")


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
        updated_agent = agent_service.update_agent(UUID(agent_id), organization_id, **update_data)
        return updated_agent
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid agent ID format")


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    auth: tuple = Depends(RequireAgentDelete),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Delete an AI agent"""
    user_id, organization_id = auth
    try:
        agent_service.delete_agent(UUID(agent_id), organization_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid agent ID format")


@router.get("/{agent_id}/workflows", response_model=ListResponse)
async def get_agent_workflows(
    agent_id: str,
    auth: tuple = Depends(RequireWorkflowRead),
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflows for an AI agent"""
    user_id, organization_id = auth
    try:
        workflows = workflow_service.get_workflows_for_agent(agent_id, organization_id)
        return ListResponse(items=workflows, total=len(workflows))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{agent_id}/workflows", response_model=Workflow, status_code=status.HTTP_201_CREATED)
async def create_agent_workflow(
    agent_id: str,
    workflow: WorkflowCreate,
    auth: tuple = Depends(RequireWorkflowCreate),
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Create a new workflow for an AI agent"""
    user_id, organization_id = auth
    try:
        # Convert the entire workflow to dict first, then extract nested objects
        workflow_dict = workflow.dict()
        
        # Ensure the agent_id is set to the one from the URL path
        workflow_dict['agent_id'] = agent_id
        
        new_workflow = workflow_service.create_workflow(
            organization_id=organization_id,
            name=workflow_dict['name'],
            description=workflow_dict.get('description'),
            agent_id=workflow_dict['agent_id'],
            nodes=workflow_dict.get('nodes', []),
            edges=workflow_dict.get('edges', []),
            status=workflow_dict.get('status', 'draft')
        )
        return new_workflow
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{agent_id}/status", response_model=dict)
async def get_agent_status(
    agent_id: str,
    auth: tuple = Depends(RequireAgentRead),
    agent_service: AIAgentService = Depends(get_ai_agent_service)
):
    """Get status of an AI agent"""
    user_id, organization_id = auth
    try:
        status_info = agent_service.get_agent_status(UUID(agent_id), UUID(organization_id))
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
        result = agent_service.execute_agent(UUID(agent_id), organization_id, request_data)
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
        result = agent_service.start_training(UUID(agent_id), organization_id, training_data)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
