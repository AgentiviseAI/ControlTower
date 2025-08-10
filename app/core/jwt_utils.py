"""
JWT utilities for token validation and user extraction
"""
import jwt
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import os
from .config import settings

logger = logging.getLogger(__name__)

class JWTManager:
    """JWT token validation and user extraction"""
    
    def __init__(self):
        # In production, this should come from environment variables
        # and be the same secret used by AuthService
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-in-production")
        self.algorithm = "HS256"
        logger.info(f"🔑 JWT Manager initialized with secret key: {self.secret_key[:10]}...")
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate JWT token
        Returns user payload if valid, None if invalid
        """
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            logger.debug(f"🔑 Decoding token with secret_key: {self.secret_key[:10]}...")
            logger.debug(f"🔑 Using algorithm: {self.algorithm}")
            logger.debug(f"🎫 Token (first 20 chars): {token[:20]}...")
            
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                audience=settings.resource_app_id
            )
            
            logger.debug(f"✅ Token decoded successfully, payload keys: {list(payload.keys())}")
            
            # Check if token is expired
            if 'exp' in payload:
                exp_timestamp = payload['exp']
                current_timestamp = datetime.utcnow().timestamp()
                logger.debug(f"⏰ Token expiry check: exp={exp_timestamp}, now={current_timestamp}")
                
                if current_timestamp > exp_timestamp:
                    logger.warning(f"❌ Token expired: exp={exp_timestamp}, now={current_timestamp}")
                    return None
            
            return payload
            
        except jwt.ExpiredSignatureError as e:
            logger.error(f"❌ Token expired: {e}")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"❌ Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected token decoding error: {e}")
            logger.exception("Full traceback:")
            return None
    
    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """Extract user ID from JWT token"""
        logger.debug(f"🎫 Extracting user ID from token")
        
        payload = self.decode_token(token)
        if payload:
            logger.debug(f"🔍 Token payload keys: {list(payload.keys())}")
            
            # Log the key claims for debugging
            preferred_username = payload.get('preferred_username')
            user_id = payload.get('user_id')
            sub = payload.get('sub')
            email = payload.get('email')
            
            logger.debug(f"👤 Token claims:")
            logger.debug(f"  - preferred_username: {preferred_username}")
            logger.debug(f"  - user_id: {user_id}")
            logger.debug(f"  - sub: {sub}")
            logger.debug(f"  - email: {email}")
            
            # EntraID typically stores email in 'preferred_username' claim
            result = preferred_username or user_id
            logger.info(f"✅ Extracted user ID: {result}")
            return result
        else:
            logger.warning("❌ Failed to decode token payload")
            
        return None


# Global instance
jwt_manager = JWTManager()
