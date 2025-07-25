"""
Metrics schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class MetricsBase(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=255)
    metric_value: float
    entity_type: str = Field(..., min_length=1, max_length=100)
    entity_id: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = {}


class MetricsCreate(MetricsBase):
    pass


class MetricsUpdate(BaseModel):
    metric_name: Optional[str] = Field(None, min_length=1, max_length=255)
    metric_value: Optional[float] = None
    entity_type: Optional[str] = Field(None, min_length=1, max_length=100)
    entity_id: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class Metrics(MetricsBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
