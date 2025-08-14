"""
Organization service for managing organizations and memberships
"""
from typing import List, Optional
from uuid import UUID

from app.models.organization import Organization, OrganizationUser, OrganizationRole
from app.repositories.organization_repository import OrganizationRepository
from app.services.base import BaseService


class OrganizationService(BaseService):
    """Service for organization business logic"""
    
    def __init__(self, repository: OrganizationRepository):
        super().__init__(repository)
        self.repository = repository
    
    def create_organization(
        self, 
        name: str, 
        description: Optional[str], 
        owner_user_id: UUID,
        org_type: str = "personal"
    ) -> Organization:
        """Create a new organization with the creator as owner"""
        # Check if organization with same name exists
        existing_org = self.repository.get_organization_by_name(name)
        if existing_org:
            raise ValueError(f"Organization with name '{name}' already exists")
        
        # Convert type to boolean for the model
        is_personal = org_type.lower() == "personal"
        
        # Create the organization
        organization = self.repository.create_organization(name, description, is_personal)
        
        # Add the creator as owner
        self.repository.add_user_to_organization(
            organization.id, 
            owner_user_id,
            OrganizationRole.OWNER
        )
        
        return organization
    
    def create_organization_with_sample_agent(
        self,
        name: str,
        description: Optional[str],
        owner_user_id: UUID,
        org_type: str = "personal",
        agent_service=None,
        workflow_service=None,
        llm_service=None
    ) -> Organization:
        """Create a new organization with a sample agent for the user"""
        # First create the organization
        organization = self.create_organization(name, description, owner_user_id, org_type)
        
        # Only create sample agent for personal organizations
        if org_type.lower() == "personal" and agent_service and workflow_service and llm_service:
            try:
                self.logger.info(f"Creating sample agent for new personal organization: {organization.id}")
                
                # Sample agent data
                sample_agent_data = {
                    'name': 'Welcome Assistant',
                    'description': 'Your personal AI assistant to help you get started with the platform. Ask me anything!',
                    'enabled': True,
                    'preview_enabled': False
                }
                
                # Use the same method that the API uses to create agent with workflow
                sample_agent = agent_service.create_agent_with_default_workflow(
                    agent_data=sample_agent_data,
                    organization_id=organization.id,
                    workflow_service=workflow_service,
                    llm_service=llm_service
                )
                
                self.logger.info(f"Sample agent created successfully: {sample_agent['id']} for organization: {organization.id}")
                
            except Exception as e:
                # Log error but don't fail organization creation
                self.logger.error(f"Failed to create sample agent for organization {organization.id}: {e}")
                # Sample agent creation failure shouldn't prevent organization creation
        
        return organization
    
    def get_organization_by_id(self, organization_id: UUID) -> Optional[Organization]:
        """Get organization by ID"""
        return self.repository.get_organization_by_id(organization_id)
    
    def get_user_organizations(self, user_id: UUID) -> List[dict]:
        """Get all organizations for a user with their roles"""
        org_roles = self.repository.get_user_organizations(user_id)
        
        organizations = []
        for org, role in org_roles:
            org_dict = {
                'id': org.id,
                'name': org.name,
                'type': 'personal' if org.is_personal else 'organization',
                'description': org.description,
                'status': org.status,
                'role': role,
                'created_at': org.created_at,
                'updated_at': org.updated_at
            }
            organizations.append(org_dict)
        
        return organizations
    
    def get_organization_users(self, organization_id: UUID) -> List[OrganizationUser]:
        """Get all users in an organization"""
        return self.repository.get_organization_users(organization_id)
    
    def add_user_to_organization(
        self, 
        organization_id: UUID, 
        user_id: UUID, 
        role: OrganizationRole
    ) -> OrganizationUser:
        """Add a user to an organization"""
        # Check if organization exists
        organization = self.repository.get_organization_by_id(organization_id)
        if not organization:
            raise ValueError("Organization not found")
        
        # Check if user is already in organization
        existing_role = self.repository.get_user_role_in_organization(organization_id, user_id)
        if existing_role:
            raise ValueError("User is already a member of this organization")
        
        return self.repository.add_user_to_organization(organization_id, user_id, role)
    
    def get_user_role_in_organization(
        self, 
        organization_id: UUID, 
        user_id: UUID
    ) -> Optional[OrganizationRole]:
        """Get user's role in an organization"""
        return self.repository.get_user_role_in_organization(organization_id, user_id)
    
    def remove_user_from_organization(self, organization_id: UUID, user_id: UUID):
        """Remove a user from an organization"""
        # Check if user is in organization
        role = self.repository.get_user_role_in_organization(organization_id, user_id)
        if not role:
            raise ValueError("User is not a member of this organization")
        
        # Don't allow removing the owner (should transfer ownership first)
        if role == OrganizationRole.OWNER:
            raise ValueError("Cannot remove organization owner")
        
        self.repository.remove_user_from_organization(organization_id, user_id)
    
    def user_has_access_to_organization(
        self, 
        organization_id: UUID, 
        user_id: UUID
    ) -> bool:
        """Check if user has access to an organization"""
        role = self.repository.get_user_role_in_organization(organization_id, user_id)
        return role is not None
    
    def user_is_admin_or_owner(
        self, 
        organization_id: UUID, 
        user_id: UUID
    ) -> bool:
        """Check if user is admin or owner of an organization"""
        role = self.repository.get_user_role_in_organization(organization_id, user_id)
        return role in [OrganizationRole.ADMIN, OrganizationRole.OWNER]