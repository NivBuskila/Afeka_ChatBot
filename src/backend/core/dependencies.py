import logging
from typing import Optional, Dict, Any

from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from supabase import Client, create_client

from ..app.config.settings import settings
from ..app.core.auth import get_current_user

logger = logging.getLogger(__name__)

# --- Supabase Client Dependency ---
supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """FastAPI dependency that provides a Supabase client instance."""
    global supabase_client
    if supabase_client is None:
        if not settings.SUPABASE_KEY or not settings.SUPABASE_URL:
            logger.error("Supabase URL or Key not configured.")
            raise HTTPException(status_code=503, detail="Database connection not configured")
        try:
            supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Supabase client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise HTTPException(status_code=503, detail="Failed to connect to database")
    
    if supabase_client is None: # Should not happen if initialization is correct
         raise HTTPException(status_code=503, detail="Database client unavailable")
         
    return supabase_client

def get_supabase_client_sync() -> Optional[Client]:
    """Synchronous version of get_supabase_client for use in non-FastAPI contexts."""
    global supabase_client
    if supabase_client is None:
        if not settings.SUPABASE_KEY or not settings.SUPABASE_URL:
            logger.warning("Supabase URL or Key not configured for sync client.")
            return None
        try:
            supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Supabase sync client initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase sync client: {e}")
            return None
    
    return supabase_client

# --- API Key Dependency ---
api_key_header_scheme = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header_scheme)):
    """FastAPI dependency that verifies the internal API key."""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API Key",
            headers={"WWW-Authenticate": "APIKey"}
        )
    if api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "APIKey"}
        )
    return api_key # Or return True, or the key itself if needed

# --- Admin Authentication Dependency ---
def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)):
    """FastAPI dependency that requires the user to be an admin."""
    if not current_user:
        raise HTTPException(
            status_code=403,
            detail="Authentication required"
        )
    
    # Get user ID from JWT payload (Supabase uses 'sub' field)
    user_id = current_user.get("id") or current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=403,
            detail="Invalid user data"
        )
    
    # Check if user is admin in the admins table
    try:
        supabase = get_supabase_client()
        result = supabase.table("admins").select("id, permissions").eq("user_id", user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=403,
                detail="Admin access required"
            )
        
        # Add admin info to current_user
        current_user["admin_id"] = result.data[0]["id"]
        current_user["permissions"] = result.data[0]["permissions"]
        
        return current_user
        
    except Exception as e:
        logger.error(f"Error checking admin status for user {user_id}: {e}")
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        ) 