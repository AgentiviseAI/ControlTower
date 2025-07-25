"""
Workflow Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List

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
