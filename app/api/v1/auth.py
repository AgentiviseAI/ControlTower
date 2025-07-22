"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas import UserLogin, Token, User
from app.services import AuthService
from app.api.dependencies import get_auth_service
from app.core.exceptions import NotFoundError
import uuid

router = APIRouter(tags=["Authentication"])
security = HTTPBearer()


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user and return access token"""
    try:
        user = auth_service.authenticate_user(credentials.username, credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # In a real app, you'd generate a proper JWT token
        # For now, we'll create a mock token
        access_token = f"mock_token_{credentials.username}_{uuid.uuid4()}"
        
        return Token(
            access_token=access_token,
            token_type="bearer"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.get("/me", response_model=User)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current authenticated user"""
    # In a real app, you'd decode the JWT token to get user info
    # For now, we'll extract username from the mock token
    token = credentials.credentials
    if not token.startswith("mock_token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Extract username from mock token
        parts = token.split("_")
        if len(parts) >= 3:
            username = parts[2]
            user = auth_service.get_user_by_username(username)
            if user:
                return user
    except Exception:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token and return username"""
    token = credentials.credentials
    if not token.startswith("mock_token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract username from mock token
    try:
        parts = token.split("_")
        if len(parts) >= 3:
            return parts[2]  # Return username
    except Exception:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
