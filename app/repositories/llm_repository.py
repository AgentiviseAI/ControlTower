"""
LLM Repository implementation
"""
from sqlalchemy.orm import Session
from typing import List

from app.models import LLM
from .base import BaseRepository


class LLMRepository(BaseRepository):
    """Repository for LLM operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, LLM)
    
    def get_enabled_llms(self) -> List[LLM]:
        """Get all enabled LLMs"""
        return self.filter_by(enabled=True)
    
    def get_by_provider(self, provider: str) -> List[LLM]:
        """Get LLMs by provider"""
        return self.filter_by(provider=provider)
