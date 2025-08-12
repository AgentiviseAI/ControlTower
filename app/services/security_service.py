"""
Security Service implementation
"""
from typing import List, Optional, Dict, Any
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

    def create_organization_role(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new organization-specific security role"""
        self._validate_data(role_data, ['name'])
        
        # Set the role type to organization
        role_data['type'] = RoleType.ORGANIZATION
        
        # Check if role name already exists
        existing_role = self.role_repo.get_by_name(role_data['name'])
        if existing_role:
            raise ConflictError(f"Role with name '{role_data['name']}' already exists")
        
        self.logger.info(f"Creating organization role: {role_data['name']}")
        
        role = self.role_repo.create(**role_data)
        return self._to_dict(role)

    def list_roles(self) -> List[Dict[str, Any]]:
        """List all active security roles (both system and organization roles)"""
        self.logger.info("Fetching all active security roles (system and organization)")
        
        roles = self.role_repo.get_active_roles()
        return [self._to_dict(role) for role in roles]
