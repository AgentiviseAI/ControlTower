"""
IntentData repository for database operations
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.intent_data import IntentData
from app.repositories.base import BaseRepository


class IntentDataRepository(BaseRepository):
    """Repository for IntentData operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, IntentData)
    
    def get_by_source(self, organization_id: str, source_type: str, source_id: str) -> List[IntentData]:
        """Get intent data by source type and ID"""
        return (
            self.db.query(self.model)
            .filter(
                and_(
                    self.model.organization_id == organization_id,
                    self.model.source_type == source_type,
                    self.model.source_id == source_id
                )
            )
            .all()
        )
    
    def list_by_source_type(self, organization_id: str, source_type: str) -> List[IntentData]:
        """List intent data by source type"""
        return (
            self.db.query(self.model)
            .filter(
                and_(
                    self.model.organization_id == organization_id,
                    self.model.source_type == source_type
                )
            )
            .order_by(self.model.name.asc())
            .all()
        )
    
    def list_enabled(self, organization_id: str) -> List[IntentData]:
        """List enabled intent data"""
        return (
            self.db.query(self.model)
            .filter(
                and_(
                    self.model.organization_id == organization_id,
                    self.model.enabled == True
                )
            )
            .order_by(self.model.name.asc())
            .all()
        )
    
    def search_by_name_or_description(self, organization_id: str, search_term: str) -> List[IntentData]:
        """Search intent data by name or description"""
        search_pattern = f"%{search_term}%"
        return (
            self.db.query(self.model)
            .filter(
                and_(
                    self.model.organization_id == organization_id,
                    or_(
                        self.model.name.ilike(search_pattern),
                        self.model.description.ilike(search_pattern)
                    )
                )
            )
            .order_by(self.model.name.asc())
            .all()
        )
    
    def get_by_category(self, organization_id: str, category: str) -> List[IntentData]:
        """Get intent data by category"""
        return (
            self.db.query(self.model)
            .filter(
                and_(
                    self.model.organization_id == organization_id,
                    self.model.category == category
                )
            )
            .order_by(self.model.name.asc())
            .all()
        )
    
    def delete_by_source(self, organization_id: str, source_type: str, source_id: str) -> int:
        """Delete intent data by source type and ID, returns count of deleted records"""
        deleted_count = (
            self.db.query(self.model)
            .filter(
                and_(
                    self.model.organization_id == organization_id,
                    self.model.source_type == source_type,
                    self.model.source_id == source_id
                )
            )
            .delete()
        )
        return deleted_count
    
    def bulk_create(self, intent_data_list: List[IntentData]) -> List[IntentData]:
        """Bulk create intent data"""
        self.db.add_all(intent_data_list)
        self.db.flush()
        return intent_data_list
