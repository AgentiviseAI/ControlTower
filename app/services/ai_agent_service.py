"""
AI Agent Service implementation
"""
from typing import List, Optional, Dict, Any
from app.repositories import AIAgentRepository
from app.core.exceptions import NotFoundError, ConflictError
from .base import BaseService


class AIAgentService(BaseService):
    """Service for AI Agent business logic"""
    
    def __init__(self, repository: AIAgentRepository, pipeline_service=None):
        super().__init__(repository)
        self.pipeline_service = pipeline_service
    
    def create_agent(self, name: str, description: str = None, enabled: bool = True, 
                    preview_enabled: bool = False) -> Dict[str, Any]:
        """Create a new AI agent"""
        # Check if agent with same name exists
        existing = self.repository.get_by_name(name)
        if existing:
            raise ConflictError(f"AI Agent with name '{name}' already exists")
        
        self.logger.info(f"Creating AI agent: {name}")
        
        # Create default pipeline if pipeline_service is available
        pipeline_id = None
        if self.pipeline_service:
            try:
                # Use the pipeline service to create a default pipeline
                default_pipeline = self.pipeline_service.create_default_pipeline(name)
                pipeline_id = default_pipeline.get("id")
                self.logger.info(f"Created default pipeline {pipeline_id} for agent {name}")
            except Exception as e:
                self.logger.warning(f"Failed to create default pipeline for agent {name}: {e}")
        
        agent = self.repository.create(
            name=name,
            description=description,
            enabled=enabled,
            preview_enabled=preview_enabled,
            pipeline_id=pipeline_id
        )
        
        return self._to_dict(agent)
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get AI agent by ID"""
        agent = self.repository.get_by_id(agent_id)
        if not agent:
            raise NotFoundError("AI Agent", agent_id)
        return self._to_dict(agent)
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all AI agents"""
        agents = self.repository.get_all()
        return [self._to_dict(agent) for agent in agents]
    
    def update_agent(self, agent_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update AI agent"""
        # Check for name conflicts if name is being updated
        if 'name' in kwargs:
            existing = self.repository.get_by_name(kwargs['name'])
            if existing and existing.id != agent_id:
                raise ConflictError(f"AI Agent with name '{kwargs['name']}' already exists")
        
        self.logger.info(f"Updating AI agent: {agent_id}")
        
        agent = self.repository.update(agent_id, **kwargs)
        if not agent:
            raise NotFoundError("AI Agent", agent_id)
        
        return self._to_dict(agent)
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete AI agent"""
        self.logger.info(f"Deleting AI agent: {agent_id}")
        
        success = self.repository.delete(agent_id)
        if not success:
            raise NotFoundError("AI Agent", agent_id)
        
        return success
    
    def get_enabled_agents(self) -> List[Dict[str, Any]]:
        """Get all enabled AI agents"""
        agents = self.repository.get_enabled_agents()
        return [self._to_dict(agent) for agent in agents]
