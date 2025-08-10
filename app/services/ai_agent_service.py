"""
AI Agent Service implementation
"""
from typing import List, Optional, Dict, Any
from app.repositories import AIAgentRepository
from app.core.exceptions import NotFoundError, ConflictError
from .base import BaseService


class AIAgentService(BaseService):
    """Service for AI Agent business logic"""
    
    def __init__(self, repository: AIAgentRepository):
        super().__init__(repository)
    
    def create_agent(self, name: str, organization_id: str, description: str = None, 
                    enabled: bool = True, preview_enabled: bool = False, 
                    workflow_id: str = None) -> Dict[str, Any]:
        """Create a new AI agent"""
        # Check if agent with same name exists in this organization
        existing = self.repository.get_by_name_and_organization(name, organization_id)
        if existing:
            raise ConflictError(f"AI Agent with name '{name}' already exists in this organization")
        
        self.logger.info(f"Creating AI agent: {name} for organization: {organization_id}")
        
        # Create the agent
        agent = self.repository.create(
            name=name,
            description=description,
            enabled=enabled,
            preview_enabled=preview_enabled,
            workflow_id=workflow_id,
            organization_id=organization_id  # ✅ Always include organization_id
        )
        
        return self._to_dict(agent)
    
    def get_agent(self, agent_id: str, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get AI agent by ID within organization"""
        agent = self.repository.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("AI Agent", agent_id)
        
        # Verify the agent belongs to the organization
        if agent.organization_id != organization_id:
            raise NotFoundError("AI Agent", agent_id)
        
        return self._to_dict(agent)
    
    def get_all_agents(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all AI agents for organization"""
        agents = self.repository.get_by_organization(organization_id)
        return [self._to_dict(agent) for agent in agents]
    
    def list_agents(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all AI agents for organization (alias for get_all_agents)"""
        return self.get_all_agents(organization_id)
    
    def update_agent(self, agent_id: str, organization_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update AI agent within organization"""
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
    
    def delete_agent(self, agent_id: str, organization_id: str) -> bool:
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
    
    def get_enabled_agents(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all enabled AI agents for organization"""
        agents = self.repository.get_enabled_agents_by_organization(organization_id)
        return [self._to_dict(agent) for agent in agents]
    
    def get_agent_status(self, agent_id: str, organization_id: str) -> Dict[str, Any]:
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
    
    def execute_agent(self, agent_id: str, organization_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
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
    
    def start_training(self, agent_id: str, organization_id: str, training_data: Dict[str, Any]) -> Dict[str, Any]:
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
