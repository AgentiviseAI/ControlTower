"""
Database-aware column types for cross-database compatibility
"""
from sqlalchemy import String, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import CHAR
import uuid
import os


class UniversalID(TypeDecorator):
    """
    A database-agnostic ID type that uses UUID for PostgreSQL and String for SQLite.
    This allows the same model to work across both development (SQLite) and production (PostgreSQL) environments.
    """
    
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load the appropriate type based on the database dialect"""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            # For SQLite and other databases, use String(36) to store UUID as string
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        """Process value when binding to database"""
        if value is None:
            return None
        
        if dialect.name == 'postgresql':
            # PostgreSQL can handle UUID objects directly
            if isinstance(value, uuid.UUID):
                return value
            elif isinstance(value, str):
                return uuid.UUID(value)
        else:
            # For SQLite, convert UUID to string
            if isinstance(value, uuid.UUID):
                return str(value)
            elif isinstance(value, str):
                # Validate it's a proper UUID string
                try:
                    uuid.UUID(value)
                    return value
                except ValueError:
                    raise ValueError(f"Invalid UUID string: {value}")
        
        return value

    def process_result_value(self, value, dialect):
        """Process value when loading from database"""
        if value is None:
            return None
            
        if dialect.name == 'postgresql':
            # PostgreSQL returns UUID objects
            return value if isinstance(value, uuid.UUID) else uuid.UUID(value)
        else:
            # For SQLite, convert string back to UUID object
            return uuid.UUID(value) if isinstance(value, str) else value


def get_id_column():
    """
    Factory function to create the appropriate ID column based on environment
    """
    return UniversalID
