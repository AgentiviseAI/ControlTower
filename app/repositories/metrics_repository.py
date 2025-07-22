"""
Metrics Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List

from app.models import Metrics
from .base import BaseRepository


class MetricsRepository(BaseRepository):
    """Repository for Metrics operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, Metrics)
    
    def get_by_metric_name(self, metric_name: str) -> List[Metrics]:
        """Get metrics by name"""
        return self.filter_by(metric_name=metric_name)
    
    def get_by_metric_type(self, metric_type: str) -> List[Metrics]:
        """Get metrics by type"""
        return self.filter_by(metric_type=metric_type)
