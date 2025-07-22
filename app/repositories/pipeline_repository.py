"""
Pipeline Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List

from app.models import Pipeline
from .base import BaseRepository


class PipelineRepository(BaseRepository):
    """Repository for Pipeline operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, Pipeline)
    
    def get_by_status(self, status: str) -> List[Pipeline]:
        """Get pipelines by status"""
        return self.filter_by(status=status)
