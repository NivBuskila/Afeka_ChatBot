import os
from supabase import create_client, Client
from typing import Optional
import logging

logger = logging.getLogger(__name__)

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Get Supabase client instance (singleton pattern)
    """
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
    
    return _supabase_client

def reset_supabase_client():
    """
    Reset the Supabase client (useful for testing)
    """
    global _supabase_client
    _supabase_client = None 