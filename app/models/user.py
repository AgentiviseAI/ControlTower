"""
User model
"""
from sqlalchemy import Column, String, DateTime
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # Should be hashed
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(100), nullable=False)
    status = Column(String(50), default="active")
    last_login = Column(DateTime)
