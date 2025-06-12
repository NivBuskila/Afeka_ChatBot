import logging
from typing import Optional

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from supabase import Client, create_client

from src.backend.core import config

logger = logging.getLogger(__name__)

# --- Supabase Client Dependency ---
supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """FastAPI dependency that provides a Supabase client instance."""
    global supabase_client
    if supabase_client is None:
        if not config.SUPABASE_KEY or not config.SUPABASE_URL:
            logger.error("Supabase URL or Key not configured.")
            raise HTTPException(status_code=503, detail="Database connection not configured")
        try:
            supabase_client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            logger.info("Supabase client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise HTTPException(status_code=503, detail="Failed to connect to database")
    
    if supabase_client is None: # Should not happen if initialization is correct
         raise HTTPException(status_code=503, detail="Database client unavailable")
         
    return supabase_client

# --- API Key Dependency ---
api_key_header_scheme = APIKeyHeader(name=config.API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header_scheme)):
    """FastAPI dependency that verifies the internal API key."""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API Key",
            headers={"WWW-Authenticate": "APIKey"}
        )
    if api_key != config.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "APIKey"}
        )
    return api_key # Or return True, or the key itself if needed 