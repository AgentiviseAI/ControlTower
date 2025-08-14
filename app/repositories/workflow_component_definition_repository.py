"""
Workflow Component Definition Repository
"""
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from uuid import UUID
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.workflow_component_definition import WorkflowComponentDefinition
from app.repositories.base import BaseRepository

if TYPE_CHECKING:
    from typing import Generic
    BaseRepositoryType = BaseRepository[WorkflowComponentDefinition]
else:
    BaseRepositoryType = BaseRepository


class WorkflowComponentDefinitionRepository(BaseRepositoryType):
    """Repository for workflow component definitions"""
    
    def __init__(self, db: Session):
        super().__init__(db, WorkflowComponentDefinition)
    
    def get_by_component_id(self, component_id: str) -> Optional[WorkflowComponentDefinition]:
        """Get component definition by component ID"""
        result = self.db.query(self.model).filter(
            self.model.component_id == component_id
        ).first()
        
        return result
    
    def list_by_category(self, category: str) -> List[WorkflowComponentDefinition]:
        """Get all component definitions in a specific category"""
        results = self.db.query(self.model).filter(
            and_(
                self.model.category == category,
                self.model.enabled == True
            )
        ).order_by(self.model.sort_order, self.model.name).all()
        
        return results
    
    def list_enabled(self) -> List[WorkflowComponentDefinition]:
        """Get all enabled component definitions"""
        results = self.db.query(self.model).filter(
            self.model.enabled == True
        ).order_by(self.model.category, self.model.sort_order, self.model.name).all()
        
        return results
    
    def search_by_name_or_description(self, search_term: str) -> List[WorkflowComponentDefinition]:
        """Search component definitions by name or description"""
        results = self.db.query(self.model).filter(
            and_(
                self.model.enabled == True,
                or_(
                    self.model.name.ilike(f"%{search_term}%"),
                    self.model.description.ilike(f"%{search_term}%")
                )
            )
        ).order_by(self.model.category, self.model.sort_order, self.model.name).all()
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        results = self.db.query(self.model.category).filter(
            self.model.enabled == True
        ).distinct().all()
        
        return [result[0] for result in results]
    
    def component_id_exists(self, component_id: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if component ID already exists"""
        query = self.db.query(self.model).filter(self.model.component_id == component_id)
        
        if exclude_id:
            query = query.filter(self.model.id != exclude_id)
        
        return query.first() is not None
    
    def update_sort_orders(self, category: str, component_orders: List[Dict[str, Any]]) -> None:
        """Update sort orders for components in a category"""
        for order_info in component_orders:
            component_id = order_info.get('component_id')
            sort_order = order_info.get('sort_order', 0)
            
            self.db.query(self.model).filter(
                and_(
                    self.model.component_id == component_id,
                    self.model.category == category
                )
            ).update({'sort_order': sort_order})
        
        self.db.commit()
    
    def get_by_tags(self, tags: List[str]) -> List[WorkflowComponentDefinition]:
        """Get component definitions that have any of the specified tags"""
        # Since tags is stored as JSON, we need to check if any of the provided tags exist
        results = []
        all_components = self.list_enabled()
        
        for component in all_components:
            component_tags = getattr(component, 'tags', []) or []
            if any(tag in component_tags for tag in tags):
                results.append(component)
        
        return results
