import os
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    Get current authenticated user from JWT token
    """
    try:
        token = credentials.credentials
        
        # For development, we'll use a simple approach
        # In production, you should validate JWT properly
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is required"
            )
        
        # Simple validation for development
        # Replace with proper JWT validation in production
        if token == "dev-token":
            return {
                "id": "dev-user-id",
                "email": "dev@example.com",
                "role": "admin"
            }
        
        # Try to decode JWT (if using real JWT)
        try:
            payload = jwt.decode(
                token, 
                os.getenv("JWT_SECRET", "dev-secret"), 
                algorithms=["HS256"]
            )
            return payload
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict]:
    """
    Get current user if authenticated, otherwise return None
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None 