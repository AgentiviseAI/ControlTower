"""
REST API Repository implementation
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.rest_api import RestAPI
from .base import BaseRepository


class RestAPIRepository(BaseRepository):
    """Repository for REST API data access"""
    
    def __init__(self, session: Session):
        super().__init__(session, RestAPI)
    
    def get_by_name_and_organization(self, name: str, organization_id: str) -> Optional[RestAPI]:
        """Get REST API by name within an organization"""
        return self.db.query(RestAPI).filter(
            RestAPI.name == name,
            RestAPI.organization_id == organization_id
        ).first()
    
    def get_by_organization(self, organization_id: str) -> List[RestAPI]:
        """Get all REST APIs for a specific organization"""
        return self.db.query(RestAPI).filter(
            RestAPI.organization_id == organization_id
        ).all()
    
    def get_by_tags(self, organization_id: str, tags: List[str]) -> List[RestAPI]:
        """Get REST APIs by tags within an organization"""
        query = self.db.query(RestAPI).filter(
            RestAPI.organization_id == organization_id
        )
        
        # Filter by tags (using JSON containment)
        for tag in tags:
            query = query.filter(RestAPI.tags.contains([tag]))
        
        return query.all()
    
    def get_by_method(self, organization_id: str, method: str) -> List[RestAPI]:
        """Get REST APIs by HTTP method within an organization"""
        return self.db.query(RestAPI).filter(
            RestAPI.organization_id == organization_id,
            RestAPI.method == method.upper()
        ).all()
    
    def get_by_base_url(self, organization_id: str, base_url: str) -> List[RestAPI]:
        """Get REST APIs by base URL within an organization"""
        return self.db.query(RestAPI).filter(
            RestAPI.organization_id == organization_id,
            RestAPI.base_url == base_url
        ).all()
    
    def get_enabled(self, organization_id: str) -> List[RestAPI]:
        """Get all enabled REST APIs for an organization"""
        return self.db.query(RestAPI).filter(
            RestAPI.organization_id == organization_id,
            RestAPI.enabled == True,
            RestAPI.status == "active"
        ).all()
    
    def get_by_status(self, organization_id: str, status: str) -> List[RestAPI]:
        """Get REST APIs by status within an organization"""
        return self.db.query(RestAPI).filter(
            RestAPI.organization_id == organization_id,
            RestAPI.status == status
        ).all()
    
    def search_by_name(self, organization_id: str, search_term: str) -> List[RestAPI]:
        """Search REST APIs by name within an organization"""
        return self.db.query(RestAPI).filter(
            RestAPI.organization_id == organization_id,
            RestAPI.name.ilike(f"%{search_term}%")
        ).all()
    
    def get_by_openapi_spec_url(self, organization_id: str, spec_url: str) -> List[RestAPI]:
        """Get REST APIs by OpenAPI spec URL within an organization"""
        return self.db.query(RestAPI).filter(
            RestAPI.organization_id == organization_id,
            RestAPI.openapi_spec_url == spec_url
        ).all()
