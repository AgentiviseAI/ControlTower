"""
AI Agent Service implementation
"""
import uuid
from uuid import UUID
from typing import List, Optional, Dict, Any
from app.repositories import AIAgentRepository
from app.core.exceptions import NotFoundError, ConflictError
from .base import BaseService


class AIAgentService(BaseService):
    """Service for AI Agent business logic"""
    
    def __init__(self, repository: AIAgentRepository):
        super().__init__(repository)
    
    def create_agent(self, name: str, organization_id: UUID, description: str = None, 
                    enabled: bool = True, preview_enabled: bool = False) -> Dict[str, Any]:
        """Create a new AI agent (automatically detects transaction context)"""
        # Check if agent with same name exists in this organization
        existing = self.repository.get_by_name_and_organization(name, organization_id)
        if existing:
            raise ConflictError(f"AI Agent with name '{name}' already exists in this organization")
        
        self.logger.info(f"Creating AI agent: {name} for organization: {organization_id}")
        
        # Create the agent (auto-detects transaction context)
        # organization_id is already a UUID
        agent = self.repository.create(
            name=name,
            description=description,
            enabled=enabled,
            preview_enabled=preview_enabled,
            organization_id=organization_id
        )
        
        return self._to_dict(agent)
    
    def get_agent(self, agent_id: UUID, organization_id: UUID, workflow_service=None) -> Optional[Dict[str, Any]]:
        """Get AI agent by ID within organization with default workflow ID"""
        agent = self.repository.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("AI Agent", agent_id)
        
        # Verify the agent belongs to the organization
        if agent.organization_id != organization_id:
            raise NotFoundError("AI Agent", agent_id)
        
        agent_dict = self._to_dict(agent)
        
        # Add workflow_id if workflow_service is provided
        if workflow_service:
            try:
                default_workflow = workflow_service.get_default_workflow_for_agent(
                    str(agent_id), organization_id
                )
                agent_dict['workflow_id'] = default_workflow['id'] if default_workflow else None
            except Exception as e:
                self.logger.warning(f"Failed to get default workflow for agent {agent_id}: {e}")
                agent_dict['workflow_id'] = None
        else:
            agent_dict['workflow_id'] = None
        
        return agent_dict
    
    def get_all_agents(self, organization_id: UUID) -> List[Dict[str, Any]]:
        """Get all AI agents for organization"""
        agents = self.repository.get_by_organization(organization_id)
        return [self._to_dict(agent) for agent in agents]
    
    def list_agents(self, organization_id: UUID, workflow_service=None) -> List[Dict[str, Any]]:
        """Get all AI agents for organization with their default workflow IDs"""
        agents = self.repository.get_by_organization(organization_id)
        result = []
        
        for agent in agents:
            agent_dict = self._to_dict(agent)
            
            # Add workflow_id if workflow_service is provided
            if workflow_service:
                try:
                    default_workflow = workflow_service.get_default_workflow_for_agent(
                        str(agent.id), organization_id
                    )
                    agent_dict['workflow_id'] = default_workflow['id'] if default_workflow else None
                except Exception as e:
                    self.logger.warning(f"Failed to get default workflow for agent {agent.id}: {e}")
                    agent_dict['workflow_id'] = None
            else:
                agent_dict['workflow_id'] = None
            
            result.append(agent_dict)
        
        return result
    
    def update_agent(self, agent_id: UUID, organization_id: UUID, **kwargs) -> Optional[Dict[str, Any]]:
        """Update AI agent within organization (automatically detects transaction context)"""
        # Check for name conflicts if name is being updated
        if 'name' in kwargs:
            existing = self.repository.get_by_name_and_organization(kwargs['name'], organization_id)
            if existing and existing.id != agent_id:
                raise ConflictError(f"AI Agent with name '{kwargs['name']}' already exists in this organization")
        
        self.logger.info(f"Updating AI agent: {agent_id} in organization: {organization_id}")
        
        # First verify the agent exists and belongs to the organization
        agent = self.repository.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("AI Agent", agent_id)
        if agent.organization_id != organization_id:
            raise NotFoundError("AI Agent", agent_id)
        
        agent = self.repository.update(agent_id, **kwargs)
        return self._to_dict(agent)
    
    def delete_agent(self, agent_id: UUID, organization_id: UUID) -> bool:
        """Delete AI agent within organization"""
        self.logger.info(f"Deleting AI agent: {agent_id} in organization: {organization_id}")
        
        # First verify the agent exists and belongs to the organization
        agent = self.repository.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("AI Agent", agent_id)
        if agent.organization_id != organization_id:
            raise NotFoundError("AI Agent", agent_id)
        
        success = self.repository.delete(agent_id)
        return success
    
    def get_enabled_agents(self, organization_id: UUID) -> List[Dict[str, Any]]:
        """Get all enabled AI agents for organization"""
        agents = self.repository.get_enabled_agents_by_organization(organization_id)
        return [self._to_dict(agent) for agent in agents]
    
    def get_agent_status(self, agent_id: UUID, organization_id: UUID) -> Dict[str, Any]:
        """Get status of an AI agent within organization"""
        # First verify the agent exists and belongs to the organization
        agent = self.repository.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("AI Agent", agent_id)
        if agent.organization_id != organization_id:
            raise NotFoundError("AI Agent", agent_id)
        
        return {
            "agent_id": agent_id,
            "status": "active" if agent.enabled else "inactive",
            "last_execution": None,  # Placeholder
            "health": "healthy"
        }
    
    def get_default_workflow_for_agent(self, agent_id: UUID, organization_id: UUID, workflow_service) -> Optional[Dict[str, Any]]:
        """Get the default workflow for an agent"""
        # First verify the agent exists and belongs to the organization
        agent = self.repository.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("AI Agent", agent_id)
        if agent.organization_id != organization_id:
            raise NotFoundError("AI Agent", agent_id)
        
        # Get workflows for this agent, ordered by execution_order, default first
        return workflow_service.get_default_workflow_for_agent(agent_id, organization_id)

    def get_all_workflows_for_agent(self, agent_id: UUID, organization_id: UUID, workflow_service) -> List[Dict[str, Any]]:
        """Get all workflows for an agent, ordered by execution order"""
        # First verify the agent exists and belongs to the organization
        agent = self.repository.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("AI Agent", agent_id)
        if agent.organization_id != organization_id:
            raise NotFoundError("AI Agent", agent_id)
        
        # Get all workflows for this agent
        return workflow_service.get_workflows_for_agent(agent_id, organization_id)

    def execute_agent(self, agent_id: UUID, organization_id: UUID, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an AI agent within organization"""
        # First verify the agent exists and belongs to the organization
        agent = self.repository.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("AI Agent", agent_id)
        if agent.organization_id != organization_id:
            raise NotFoundError("AI Agent", agent_id)
        
        # Placeholder implementation
        self.logger.info(f"Executing AI agent: {agent_id} in organization: {organization_id}")
        return {
            "execution_id": f"exec_{agent_id}",
            "status": "completed",
            "result": "Agent execution placeholder"
        }
    
    def start_training(self, agent_id: UUID, organization_id: UUID, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start training for an AI agent within organization"""
        # First verify the agent exists and belongs to the organization
        agent = self.repository.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("AI Agent", agent_id)
        if agent.organization_id != organization_id:
            raise NotFoundError("AI Agent", agent_id)
        
        # Placeholder implementation
        self.logger.info(f"Starting training for AI agent: {agent_id} in organization: {organization_id}")
        return {
            "training_id": f"train_{agent_id}",
            "status": "started",
            "estimated_duration": "2 hours"
        }
    
    def create_agent_with_default_workflow(self, agent_data: Dict[str, Any], 
                                         organization_id: UUID, 
                                         workflow_service) -> Dict[str, Any]:
        """Create an AI agent with a default workflow atomically
        
        This simplified approach:
        1. Creates the agent
        2. Creates default workflow with is_default=True
        
        No circular dependency - workflow references agent, not vice versa.
        
        Args:
            agent_data: Dictionary containing agent creation data
            organization_id: Organization ID for the agent
            workflow_service: Workflow service instance for creating default workflow
            
        Returns:
            Dict containing the created agent
        """
        # Step 1: Create the agent (no workflow_id needed)
        self.logger.info(f"Creating agent with data: {agent_data}")
        created_agent = self.create_agent(
            name=agent_data['name'],
            description=agent_data.get('description'),
            enabled=agent_data.get('enabled', True),
            preview_enabled=agent_data.get('preview_enabled', False),
            organization_id=organization_id
        )
        self.logger.info(f"Created agent: {created_agent}")
        
        # Step 2: Create default workflow for the agent (workflow references agent)
        self.logger.info(f"Creating default workflow for agent {created_agent['id']}")
        default_workflow = self._create_default_workflow(
            created_agent, agent_data['name'], organization_id, workflow_service
        )
        self.logger.info(f"Created default workflow: {default_workflow}")
        
        # No need to update agent - workflow is marked as default and references agent
        # Return the created agent as-is
        return created_agent
    
    def _create_default_workflow(self, agent: Dict[str, Any], agent_name: str, 
                                organization_id: UUID, workflow_service) -> Dict[str, Any]:
        """Create a default workflow with LLM node for the agent"""
        # Generate unique node IDs
        llm_node_id = str(uuid.uuid4())
        start_node_id = str(uuid.uuid4())
        end_node_id = str(uuid.uuid4())
        
        # Define default workflow structure
        default_nodes = [
            {
                "id": start_node_id,
                "label": "Start",
                "type": "start",
                "link": None,
                "position": {"x": 100, "y": 100},
                "config": {"message": "Start here"}
            },
            {
                "id": llm_node_id,
                "label": "LLM Node",
                "type": "llm",
                "link": None,
                "position": {"x": 300, "y": 100},
                "config": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "system_prompt": "You are a helpful AI assistant."
                }
            },
            {
                "id": end_node_id,
                "label": "End",
                "type": "end",
                "link": None,
                "position": {"x": 500, "y": 100},
                "config": {"message": "End here"}
            }
        ]
        
        default_edges = [
            {"source": start_node_id, "target": llm_node_id},
            {"source": llm_node_id, "target": end_node_id}
        ]
        
        # Create the workflow through the workflow service
        # New design: workflow references agent and is marked as default
        return workflow_service.create_workflow(
            organization_id=organization_id,
            name=f"Default Workflow - {agent_name}",
            description="Default workflow with LLM node",
            agent_id=agent['id'],  # Workflow references agent
            nodes=default_nodes,
            edges=default_edges,
            status='draft',
            is_default=True,  # Mark as default workflow
            execution_order=0  # Highest priority
        )
