"""
Base schemas for API request/response models
"""
from pydantic import BaseModel
from typing import Optional, List, Any


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None


class ListResponse(BaseModel):
    """Generic list response"""
    items: List[Any]
    total: int
    page: Optional[int] = None
    page_size: Optional[int] = None
