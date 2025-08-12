"""
AI Agent Repository implementation
"""
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from app.models import AIAgent
from .base import BaseRepository


class AIAgentRepository(BaseRepository):
    """Repository for AI Agent operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, AIAgent)
    
    def get_enabled_agents(self) -> List[AIAgent]:
        """Get all enabled AI agents"""
        return self.filter_by(enabled=True)
    
    def get_by_name(self, name: str) -> Optional[AIAgent]:
        """Get AI agent by name"""
        return self.get_by_field("name", name)
    
    def get_by_name_and_organization(self, name: str, organization_id: UUID) -> Optional[AIAgent]:
        """Get AI agent by name within a specific organization"""
        # Convert organization_id string to UUID for database query
        org_uuid = UUID(organization_id) if isinstance(organization_id, str) else organization_id
        return self.db.query(AIAgent).filter(
            AIAgent.name == name,
            AIAgent.organization_id == org_uuid
        ).first()
    
    def get_by_organization(self, organization_id: UUID) -> List[AIAgent]:
        """Get all AI agents for a specific organization"""
        # Convert organization_id string to UUID for database query
        org_uuid = UUID(organization_id) if isinstance(organization_id, str) else organization_id
        return self.db.query(AIAgent).filter(AIAgent.organization_id == org_uuid).all()
    
    def get_enabled_agents_by_organization(self, organization_id: UUID) -> List[AIAgent]:
        """Get all enabled AI agents for a specific organization"""
        # Convert organization_id string to UUID for database query
        org_uuid = UUID(organization_id) if isinstance(organization_id, str) else organization_id
        return self.db.query(AIAgent).filter(
            AIAgent.organization_id == org_uuid,
            AIAgent.enabled == True
        ).all()
