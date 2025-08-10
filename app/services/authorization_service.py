"""
Authorization service for role-based access control
"""
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories import OrganizationRepository, SecurityRoleRepository
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


class AuthorizationService:
    """Service for handling authorization and permission checks"""
    
    def __init__(self, db: Session = None):
        # If no database session is provided, create one
        if db is not None:
            self.db = db
            self._should_close_db = False
        else:
            self.db = SessionLocal()
            self._should_close_db = True
            
        self.org_repo = OrganizationRepository(self.db)
        self.role_repo = SecurityRoleRepository(self.db)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._should_close_db and self.db:
            try:
                if exc_type is not None:
                    self.db.rollback()
                self.db.close()
            except Exception as e:
                print(f"Error closing database session: {e}")
    
    def close(self):
        """Manually close the database session if needed"""
        if self._should_close_db and self.db:
            try:
                self.db.close()
            except Exception as e:
                print(f"Error closing database session: {e}")
    
    # Removed validate_token_and_get_user method - token validation is now handled by the API dependency layer
    
    def get_user_role_in_organization(self, user_id: str, organization_id: str) -> Optional[str]:
        """Get user's role in the specified organization"""
        logger.debug(f"👥 Looking up role for user '{user_id}' in organization '{organization_id}'")
        
        try:
            # Use the organization repository to get user role
            role = self.org_repo.get_user_role_in_organization(organization_id, user_id)
            role_value = role.value if role else None
            
            logger.debug(f"📋 Role lookup result: {role_value}")
            return role_value
            
        except Exception as e:
            logger.error(f"❌ Error looking up user role: {e}")
            logger.exception("Full traceback:")
            return None
    
    def get_role_permissions(self, role_name: str) -> Dict[str, List[str]]:
        """Get permissions for a role"""
        logger.debug(f"🔑 Looking up permissions for role '{role_name}'")
        
        try:
            # First try exact match
            role = self.role_repo.get_by_name(role_name)
            
            # If no exact match, try case-insensitive search
            if not role:
                logger.debug(f"🔍 Exact match not found for '{role_name}', trying case-insensitive search...")
                # Try with capitalized first letter (e.g., "owner" -> "Owner")
                capitalized_name = role_name.capitalize()
                role = self.role_repo.get_by_name(capitalized_name)
                
                if role:
                    logger.debug(f"✅ Found role with capitalized name: '{capitalized_name}'")
                else:
                    # Try uppercase (e.g., "owner" -> "OWNER")
                    upper_name = role_name.upper()
                    role = self.role_repo.get_by_name(upper_name)
                    if role:
                        logger.debug(f"✅ Found role with uppercase name: '{upper_name}'")
            
            if role:
                permissions = role.permissions
                logger.debug(f"✅ Found permissions for role '{role_name}': {permissions}")
                return permissions
            else:
                logger.warning(f"❌ Role '{role_name}' not found in database (tried: '{role_name}', '{role_name.capitalize()}', '{role_name.upper()}')")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error looking up role permissions for '{role_name}': {e}")
            logger.exception("Full traceback:")
            return {}
    
    def check_permission(self, user_id: str, organization_id: str, 
                        resource: str, action: str) -> bool:
        """
        Check if user has permission to perform action on resource in organization
        
        Args:
            user_id: User ID from JWT token
            organization_id: Organization ID from request
            resource: Resource type (e.g., 'agents', 'llms', 'workflows')
            action: Action to perform (e.g., 'create', 'read', 'update', 'delete')
        
        Returns:
            True if user has permission, False otherwise
        """
        logger.debug(f"🔍 Checking permission for user_id='{user_id}', organization_id='{organization_id}', resource='{resource}', action='{action}'")
        
        # Get user's role in organization
        role_name = self.get_user_role_in_organization(user_id, organization_id)
        logger.debug(f"📋 User role in organization: {role_name}")
        
        if not role_name:
            logger.warning(f"❌ User '{user_id}' has no role in organization '{organization_id}'")
            return False
        
        # Get permissions for the role
        permissions = self.get_role_permissions(role_name)
        logger.debug(f"🔑 Role '{role_name}' permissions: {permissions}")
        
        if not permissions:
            logger.warning(f"❌ Role '{role_name}' has no permissions defined")
            return False
        
        # Check if role has permission for the resource and action
        resource_permissions = permissions.get(resource, [])
        logger.debug(f"📋 Permissions for resource '{resource}': {resource_permissions}")
        
        has_permission = action in resource_permissions
        logger.info(f"{'✅' if has_permission else '❌'} Permission check result: user='{user_id}', role='{role_name}', resource='{resource}', action='{action}' -> {has_permission}")
        
        return has_permission
    
    def authorize_request(self, user_id: str, organization_id: str,
                         resource: str, action: str) -> str:
        """
        Complete authorization check for a request
        
        Args:
            user_id: The user ID (already validated by the API dependency layer)
            organization_id: The organization context for the request
            resource: The resource being accessed
            action: The action being performed
        
        Returns:
            user_id if authorized
            
        Raises:
            ForbiddenError: If user doesn't have permission
        """
        logger.info(f"🔐 Starting authorization check for user='{user_id}', organization='{organization_id}', resource='{resource}', action='{action}'")
        
        # Check permissions - user is already authenticated by the API dependency layer
        logger.debug("🔍 Checking user permissions...")
        try:
            has_permission = self.check_permission(user_id, organization_id, resource, action)
            
            if not has_permission:
                logger.warning(f"🚫 Permission denied for user '{user_id}'")
                
                # Get more detailed information for error message
                user_role = self.get_user_role_in_organization(user_id, organization_id)
                logger.debug(f"📋 User role for error context: {user_role}")
                
                if not user_role:
                    error_msg = f"User is not a member of organization {organization_id}"
                    logger.error(f"❌ Authorization failed: {error_msg}")
                    raise ForbiddenError(error_msg)
                else:
                    # Get role permissions for debugging
                    role_permissions = self.get_role_permissions(user_role)
                    resource_permissions = role_permissions.get(resource, [])
                    
                    error_msg = f"User with role '{user_role}' does not have '{action}' permission for '{resource}'"
                    logger.error(f"❌ Authorization failed: {error_msg}")
                    logger.debug(f"📋 Available permissions for resource '{resource}': {resource_permissions}")
                    logger.debug(f"🔑 All role permissions: {role_permissions}")
                    
                    raise ForbiddenError(error_msg)
            
            logger.info(f"✅ Authorization successful for user '{user_id}' on resource '{resource}' with action '{action}'")
            return user_id
            
        except ForbiddenError:
            # Re-raise authorization errors
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during permission check: {e}")
            logger.exception("Full traceback:")
            raise ForbiddenError(f"Authorization check failed due to system error: {str(e)}")
