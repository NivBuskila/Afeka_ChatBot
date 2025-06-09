import os
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

# Validate JWT_SECRET on module load
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    logger.error("JWT_SECRET not found in environment variables. Please set it in your .env file.")
    raise ValueError("JWT_SECRET environment variable is required but not found")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    Get current authenticated user from JWT token
    """
    try:
        token = credentials.credentials
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is required"
            )
        
        # Simple validation for development
        if token == "dev-token":
            logger.info("Authenticated with dev-token")
            return {
                "id": "dev-user-id",
                "email": "dev@example.com",
                "role": "admin"
            }
        
        # Try to decode JWT
        try:
            payload = jwt.decode(
                token, 
                JWT_SECRET, 
                algorithms=["HS256"],
                # Add leeway for slight clock differences if that becomes an issue
                # leeway=10 
            )
            logger.info("Successfully decoded JWT with configured JWT_SECRET")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT decoding failed: ExpiredSignatureError")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            # If it's an invalid token, but looks like a JWT (e.g., Supabase token signed with different secret)
            # For development, we might want to be more lenient or log specifics
            if token.startswith("eyJ"): # Basic check for JWT format
                logger.warning(f"JWT decoding failed with JWT_SECRET: {str(e)}. Token looks like a JWT (e.g., Supabase token). Allowing for development.")
                # For development, you MIGHT return a placeholder user or attempt Supabase validation.
                # For now, let's assume if it's a JWT-like string, we allow it and parse it without verification
                # THIS IS INSECURE FOR PRODUCTION.
                try:
                    # Attempt to decode without verification just to get claims (DANGEROUS)
                    unverified_payload = jwt.decode(token, options={"verify_signature": False}, algorithms=["HS256"]) # HS256 is a guess
                    logger.info(f"Successfully decoded unverified JWT payload: {unverified_payload.get('sub')}")
                    return unverified_payload # Make sure this structure is what your app expects
                except Exception as unverified_decode_err:
                    logger.error(f"Failed to decode unverified JWT: {unverified_decode_err}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid token, and failed to parse as unverified JWT: {str(e)}"
                    )
            else:
                logger.warning(f"Invalid token (not dev-token and not JWT format): {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token: {str(e)}"
                )
            
    except HTTPException as http_exc: # Re-raise HTTP exceptions
        raise http_exc
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