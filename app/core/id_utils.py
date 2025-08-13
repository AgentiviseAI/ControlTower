"""
ID utilities for handling UUIDs consistently across database environments
"""
import uuid
from typing import Union, Optional
import os


def generate_id() -> uuid.UUID:
    """Generate a new UUID"""
    return uuid.uuid4()


def parse_id(value: Union[str, uuid.UUID, None]) -> Optional[uuid.UUID]:
    """
    Parse an ID value into a UUID object.
    Handles both string and UUID inputs safely.
    
    Args:
        value: The ID value to parse (string or UUID)
        
    Returns:
        UUID object or None if value is None
        
    Raises:
        ValueError: If the string is not a valid UUID
    """
    if value is None:
        return None
    
    if isinstance(value, uuid.UUID):
        return value
    
    if isinstance(value, str):
        try:
            return uuid.UUID(value)
        except ValueError as e:
            raise ValueError(f"Invalid UUID string: {value}") from e
    
    raise TypeError(f"ID must be str or UUID, got {type(value)}")


def id_to_string(value: Union[str, uuid.UUID, None]) -> Optional[str]:
    """
    Convert an ID to string representation.
    Useful when you need to ensure string format for APIs or logging.
    
    Args:
        value: The ID value to convert
        
    Returns:
        String representation or None if value is None
    """
    if value is None:
        return None
    
    if isinstance(value, uuid.UUID):
        return str(value)
    
    if isinstance(value, str):
        # Validate it's a proper UUID string
        try:
            uuid.UUID(value)
            return value
        except ValueError as e:
            raise ValueError(f"Invalid UUID string: {value}") from e
    
    raise TypeError(f"ID must be str or UUID, got {type(value)}")


def is_sqlite_database() -> bool:
    """
    Check if we're using SQLite database.
    Useful for conditional logic based on database type.
    """
    database_url = os.getenv("DATABASE_URL", "sqlite:///./control_tower.db")
    return database_url.startswith("sqlite")


def is_postgresql_database() -> bool:
    """
    Check if we're using PostgreSQL database.
    Useful for conditional logic based on database type.
    """
    return not is_sqlite_database()
