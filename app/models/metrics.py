"""
Metrics model
"""
from sqlalchemy import Column, String, Float, JSON, DateTime
from datetime import datetime
from .base import BaseModel


class Metrics(BaseModel):
    __tablename__ = "metrics"

    metric_name = Column(String(100), nullable=False)
    metric_type = Column(String(50), nullable=False)  # counter, gauge, histogram
    value = Column(Float, nullable=False)
    tags = Column(JSON)  # Additional metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
