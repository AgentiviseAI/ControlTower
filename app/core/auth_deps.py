"""
Authorization dependencies for ControlTower
Uses AuthService for token validation
"""
from fastapi import HTTPException, Header, Depends
from typing import Dict, Any
from app.core.auth_client import auth_client


async def get_current_user(authorization: str = Header(...)) -> Dict[str, Any]:
    """
    Extract and validate user from Authorization header
    Returns user information from AuthService
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    user_info = await auth_client.validate_token(token)
    
    return user_info


async def get_optional_user(authorization: str = Header(None)) -> Dict[str, Any]:
    """
    Optional user extraction - returns None if no auth header
    """
    if not authorization:
        return None
    
    return await get_current_user(authorization)
