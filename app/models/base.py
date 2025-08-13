"""
Base model configuration for the AI Platform
"""
from sqlalchemy import Column, DateTime
from app.core.database import Base
from app.core.database_types import UniversalID
import uuid
from datetime import datetime


class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(UniversalID(), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
