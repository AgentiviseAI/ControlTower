"""
AI Agent Repository implementation
"""
from sqlalchemy.orm import Session
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
