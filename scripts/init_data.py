"""
Initialize database with sample data
"""
from app.core.database import get_db, create_tables
from app.repositories import SecurityRoleRepository
from app.models.security_role import RoleType
from datetime import datetime


def initialize_sample_data():
    """Initialize the database with sample data"""
    
    # Create all tables
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Initialize repositories
        role_repo = SecurityRoleRepository(db)
        
        # Check if security roles already exist
        existing_roles = role_repo.get_all()
        if existing_roles:
            print("Security roles already exist, skipping initialization")
            return
        
        print("Initializing system security roles...")
        
        # Create sample security roles as SYSTEM roles
        role_repo.create(
            name="OWNER",
            description="Organization owner with full administrative privileges",
            status="active",
            type=RoleType.SYSTEM,
            permissions={
                "agents": ["create", "read", "update", "delete", "execute"],
                "llms": ["create", "read", "update", "delete", "configure"],
                "tools": ["create", "read", "update", "delete", "configure"],
                "rag": ["create", "read", "update", "delete", "configure"],
                "workflows": ["create", "read", "update", "delete", "deploy"],
                "metrics": ["read", "configure"],
                "roles": ["create", "read", "update", "delete"]
            }
        )
        
        role_repo.create(
            name="ADMIN",
            description="Full system administrator with all permissions",
            status="active",
            type=RoleType.SYSTEM,
            permissions={
                "agents": ["create", "read", "update", "delete", "execute"],
                "llms": ["create", "read", "update", "delete", "configure"],
                "tools": ["create", "read", "update", "delete", "configure"],
                "rag": ["create", "read", "update", "delete", "configure"],
                "workflows": ["create", "read", "update", "delete", "deploy"],
                "metrics": ["read", "configure"],
                "roles": ["create", "read", "update", "delete"]
            }
        )        
                
        print("System security roles initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing security roles: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    initialize_sample_data()
