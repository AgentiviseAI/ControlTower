"""
Workflow Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models import Workflow
from .base import BaseRepository


class WorkflowRepository(BaseRepository):
    """Repository for Workflow operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, Workflow)
    
    def get_by_status(self, status: str) -> List[Workflow]:
        """Get workflows by status"""
        return self.filter_by(status=status)
    
    def get_by_agent_id(self, agent_id: str) -> List[Workflow]:
        """Get workflows by agent ID"""
        return self.filter_by(agent_id=agent_id)
    
    def get_by_organization(self, organization_id: UUID) -> List[Workflow]:
        """Get all workflows for a specific organization"""
        return self.db.query(Workflow).filter(Workflow.organization_id == organization_id).all()
    
    def get_by_name_and_organization(self, name: str, organization_id: UUID) -> Optional[Workflow]:
        """Get workflow by name within a specific organization"""
        return self.db.query(Workflow).filter(
            Workflow.name == name,
            Workflow.organization_id == organization_id
        ).first()
    
    def get_active_workflows_by_organization(self, organization_id: UUID) -> List[Workflow]:
        """Get all active workflows for a specific organization"""
        return self.db.query(Workflow).filter(
            Workflow.organization_id == organization_id,
            Workflow.status == "active"
        ).all()
