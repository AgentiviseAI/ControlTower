"""
Security Service implementation
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.repositories import SecurityRoleRepository
from app.core.exceptions import NotFoundError, ConflictError
from app.models.security_role import RoleType
from .base import BaseService


class SecurityService(BaseService):
    """Service for Security and RBAC operations"""
    
    def __init__(self, role_repository: SecurityRoleRepository):
        super().__init__(role_repository)
        self.role_repo = role_repository

    def create_role(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new security role"""
        self._validate_data(role_data, ['name'])
        
        # Check if role name already exists
        existing_role = self.role_repo.get_by_name(role_data['name'])
        if existing_role:
            raise ConflictError(f"Role with name '{role_data['name']}' already exists")
        
        self.logger.info(f"Creating role: {role_data['name']}")
        
        role = self.role_repo.create(**role_data)
        return self._to_dict(role)

    def create_organization_role(self, role_data: Dict[str, Any], organization_id: UUID) -> Dict[str, Any]:
        """Create a new organization-specific security role"""
        self._validate_data(role_data, ['name'])
        
        # Set the role type to organization and populate organization_id
        role_data['type'] = RoleType.ORGANIZATION
        role_data['organization_id'] = organization_id
        
        # Check if role name already exists
        existing_role = self.role_repo.get_by_name(role_data['name'])
        if existing_role:
            raise ConflictError(f"Role with name '{role_data['name']}' already exists")
        
        self.logger.info(f"Creating organization role: {role_data['name']} for organization: {organization_id}")
        
        role = self.role_repo.create(**role_data)
        return self._to_dict(role)

    def list_roles(self, organization_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """List security roles filtered by organization context"""
        if organization_id:
            self.logger.info(f"Fetching active security roles for organization: {organization_id}")
            # Get system roles (no organization_id) and organization roles for this organization
            system_roles = self.role_repo.get_active_system_roles()
            org_roles = self.role_repo.get_active_organization_roles(organization_id)
            roles = system_roles + org_roles
        else:
            self.logger.info("Fetching all active security roles (system and organization)")
            roles = self.role_repo.get_active_roles()
        
        return [self._to_dict(role) for role in roles]
