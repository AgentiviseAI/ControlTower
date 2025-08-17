"""
Script to seed default security roles in the ControlTower database.
This script creates system-level security roles with predefined permissions.
"""

import logging
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories import SecurityRoleRepository
from app.models.security_role import RoleType

logger = logging.getLogger(__name__)


def seed_security_roles():
    """Seed default security roles into the database"""
    logger.info("Starting security roles seeding...")
    
    # Get database session
    db: Session = next(get_db())
    
    try:
        # Initialize repository
        role_repo = SecurityRoleRepository(db)
        
        # Check if security roles already exist
        existing_roles = role_repo.get_all()
        if existing_roles:
            logger.info("Security roles already exist, skipping security role initialization")
            return
            
        logger.info("Creating system security roles...")
        
        # Create OWNER role
        role_repo.create(
            name="OWNER",
            description="Organization owner with full administrative privileges",
            status="active",
            type=RoleType.SYSTEM,
            permissions={
                "agents": ["create", "read", "update", "delete", "execute"],
                "llms": ["create", "read", "update", "delete", "configure"],
                "mcp-tools": ["create", "read", "update", "delete", "configure"],
                "rag": ["create", "read", "update", "delete", "configure"],
                "workflows": ["create", "read", "update", "delete", "deploy"],
                "rest-apis": ["create", "read", "update", "delete"],
                "intent-data": ["read"],
                "metrics": ["read", "configure"],
                "roles": ["create", "read", "update", "delete"]
            }
        )
        
        # Create ADMIN role
        role_repo.create(
            name="ADMIN",
            description="Full system administrator with all permissions",
            status="active",
            type=RoleType.SYSTEM,
            permissions={
                "agents": ["create", "read", "update", "delete", "execute"],
                "llms": ["create", "read", "update", "delete", "configure"],
                "mcp-tools": ["create", "read", "update", "delete", "configure"],
                "rag": ["create", "read", "update", "delete", "configure"],
                "workflows": ["create", "read", "update", "delete", "deploy"],
                "rest-apis": ["create", "read", "update", "delete"],
                "intent-data": ["read"],
                "metrics": ["read", "configure"],
                "roles": ["create", "read", "update", "delete"]
            }
        )
        
        # Create USER role with limited permissions
        role_repo.create(
            name="USER",
            description="Standard user with basic permissions",
            status="active",
            type=RoleType.SYSTEM,
            permissions={
                "agents": ["read", "execute"],
                "llms": ["read"],
                "mcp-tools": ["read"],
                "rag": ["read"],
                "workflows": ["read", "execute"],
                "rest-apis": ["read"],
                "intent-data": ["read"],
                "metrics": ["read"]
            }
        )
        
        # Create VIEWER role with read-only permissions
        role_repo.create(
            name="VIEWER",
            description="Read-only access to system resources",
            status="active",
            type=RoleType.SYSTEM,
            permissions={
                "agents": ["read"],
                "llms": ["read"],
                "mcp-tools": ["read"],
                "rag": ["read"],
                "workflows": ["read"],
                "rest-apis": ["read"],
                "intent-data": ["read"],
                "metrics": ["read"]
            }
        )
        
        db.commit()
        logger.info("System security roles seeded successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding security roles: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    """Run the seeding script directly"""
    import sys
    import os
    
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        seed_security_roles()
        print("Security roles seeding completed successfully!")
    except Exception as e:
        print(f"Error during security roles seeding: {e}")
        sys.exit(1)
