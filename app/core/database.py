"""
Database configuration and session management with improved architecture
"""
from sqlalchemy import create_engine, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator, Optional
import logging
import os

from .config import settings, get_database_url

logger = logging.getLogger(__name__)

# Create the SQLAlchemy engine
database_url = get_database_url()

# Handle PostgreSQL URL format conversion for Azure Cosmos DB compatibility
if not database_url.startswith("sqlite"):
    # Handle different PostgreSQL URL formats
    if database_url.startswith('postgres://'):
        if 'cosmos.azure.com' in database_url:
            # Azure Cosmos DB for PostgreSQL - use psycopg2 explicitly
            database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
            logger.info("Detected Azure Cosmos DB for PostgreSQL - using psycopg2 driver")
        else:
            # Regular PostgreSQL - convert to postgresql://
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Validate PostgreSQL URL format
    if not database_url.startswith(('postgresql://', 'postgresql+psycopg2://')):
        raise ValueError(f"Invalid PostgreSQL URL format: {database_url[:30]}...")

if database_url.startswith("sqlite"):
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.debug,
    )
else:
    # PostgreSQL configuration with Azure Cosmos DB optimizations
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.debug,
        # Azure Cosmos DB specific settings
        connect_args={
            "sslmode": "require",
            "connect_timeout": 30,
        } if 'cosmos.azure.com' in database_url else {}
    )
    
    # Test database connection for PostgreSQL
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()


class DatabaseManager:
    """Database manager for handling connections and operations"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all database tables (use with caution)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in dependency: {e}")
        raise
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    db_manager.create_tables()


def init_db():
    """Initialize database with default data"""
    from app.repositories import SecurityRoleRepository
    from app.models.security_role import RoleType
    
    logger.info("Initializing database with default data...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Initialize repositories
        role_repo = SecurityRoleRepository(db)
        
        # Check if security roles already exist
        existing_roles = role_repo.get_all()
        if existing_roles:
            logger.info("Security roles already exist, skipping initialization")
            return
        
        logger.info("Creating system security roles...")
        
        # Create sample security roles as SYSTEM roles
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
                "mcp-tools": ["create", "read", "update", "delete", "configure"],
                "rag": ["create", "read", "update", "delete", "configure"],
                "workflows": ["create", "read", "update", "delete", "deploy"],
                "rest-apis": ["create", "read", "update", "delete"],
                "metrics": ["read", "configure"],
                "roles": ["create", "read", "update", "delete"]
            }
        )        
                
        logger.info("System security roles initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


# Event listeners for connection management
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragma for better performance and foreign key support"""
    if "sqlite" in str(engine.url):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=1000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()


@event.listens_for(SessionLocal, "after_transaction_end")
def restart_savepoint(session, transaction):
    """Restart savepoint after transaction end for better error handling"""
    if transaction.nested and not transaction._parent.nested:
        session.expire_all()
