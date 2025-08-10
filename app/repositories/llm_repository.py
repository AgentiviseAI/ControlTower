"""
LLM Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import LLM
from .base import BaseRepository


class LLMRepository(BaseRepository):
    """Repository for LLM operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, LLM)
    
    def get_enabled_llms(self) -> List[LLM]:
        """Get all enabled LLMs"""
        return self.filter_by(enabled=True)
    
    def get_by_hosting_environment(self, hosting_environment: str) -> List[LLM]:
        """Get LLMs by hosting environment"""
        return self.filter_by(hosting_environment=hosting_environment)
    
    def get_by_organization(self, organization_id: str) -> List[LLM]:
        """Get all LLMs for a specific organization"""
        return self.db.query(LLM).filter(LLM.organization_id == organization_id).all()
    
    def get_by_name_and_organization(self, name: str, organization_id: str) -> Optional[LLM]:
        """Get LLM by name within a specific organization"""
        return self.db.query(LLM).filter(
            LLM.name == name,
            LLM.organization_id == organization_id
        ).first()
    
    def get_enabled_llms_by_organization(self, organization_id: str) -> List[LLM]:
        """Get all enabled LLMs for a specific organization"""
        return self.db.query(LLM).filter(
            LLM.organization_id == organization_id,
            LLM.enabled == True
        ).all()
