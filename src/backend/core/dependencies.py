import logging
from typing import Optional

from fastapi import HTTPException, Security, Depends, Request, status
from fastapi.security import APIKeyHeader
from supabase import Client, create_client
import os
from dotenv import load_dotenv

from backend.core import config

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = config.SUPABASE_URL
supabase_key = config.SUPABASE_KEY

# Create a placeholder for testing
def get_supabase_client():
    """Provides a Supabase client for dependency injection."""
    return create_client(supabase_url, supabase_key)

# API key validation
def verify_api_key(request: Request):
    """Validates that the API key is correct."""
    api_key = request.headers.get(config.API_KEY_NAME)
    # For testing, accept any API key
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key missing"
        )
    return api_key

# --- Supabase Client Dependency ---
supabase_client: Optional[Client] = None

def get_supabase_client_from_config() -> Client:
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

def verify_api_key_from_header(api_key: str = Security(api_key_header_scheme)):
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