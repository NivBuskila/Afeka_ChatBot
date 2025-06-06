"""
AI Service Database Integration
Independent database module for AI service to avoid cross-service imports
"""
import os
import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

# Global client instance
_supabase_client: Optional[Client] = None

def async_to_sync(func):
    """Decorator to run async functions in sync context"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If loop is already running, create a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, func(*args, **kwargs))
                return future.result()
        else:
            return loop.run_until_complete(func(*args, **kwargs))
    return wrapper

def get_supabase_client() -> Client:
    """
    Get Supabase client for AI service (independent instance)
    """
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("SUPABASE_URL and SUPABASE_KEY must be set")
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        try:
            _supabase_client = create_client(supabase_url, supabase_key)
            logger.info("✅ AI Service Supabase client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    return _supabase_client

def test_connection() -> bool:
    """
    Test database connection
    """
    try:
        client = get_supabase_client()
        # Simple query to test connection
        response = client.table('documents').select('id').limit(1).execute()
        logger.info("✅ Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

class AIDocumentStore:
    """
    AI Service document operations (independent of backend service)
    """
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def search_documents_by_embedding(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        threshold: float = 0.78
    ) -> List[Dict[Any, Any]]:
        """
        Search documents by embedding similarity
        """
        try:
            # Use Supabase's vector similarity search
            response = await self.client.rpc('match_documents', {
                'query_embedding': query_embedding,
                'match_threshold': threshold,
                'match_count': limit
            }).execute()
            
            if response.data:
                logger.info(f"✅ Found {len(response.data)} matching documents")
                return response.data
            else:
                logger.warning("No matching documents found")
                return []
                
        except Exception as e:
            logger.error(f"❌ Document search failed: {e}")
            return []
    
    async def get_document_chunks(self, document_id: str) -> List[Dict[Any, Any]]:
        """
        Get all chunks for a specific document
        """
        try:
            response = await self.client.table('document_chunks')\
                .select('*')\
                .eq('document_id', document_id)\
                .execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"❌ Failed to get document chunks: {e}")
            return []
    
    async def store_document_chunk(
        self, 
        document_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict[Any, Any] = None
    ) -> bool:
        """
        Store a document chunk with embedding
        """
        try:
            chunk_data = {
                'document_id': document_id,
                'content': content,
                'embedding': embedding,
                'metadata': metadata or {}
            }
            
            response = await self.client.table('document_chunks')\
                .insert(chunk_data)\
                .execute()
            
            if response.data:
                logger.info(f"✅ Stored chunk for document {document_id}")
                return True
            else:
                logger.error(f"❌ Failed to store chunk for document {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error storing document chunk: {e}")
            return False

# Convenience functions for sync usage
@async_to_sync
async def search_documents_sync(query_embedding: List[float], limit: int = 10, threshold: float = 0.78):
    """Synchronous wrapper for document search"""
    store = AIDocumentStore()
    return await store.search_documents_by_embedding(query_embedding, limit, threshold)

@async_to_sync
async def get_document_chunks_sync(document_id: str):
    """Synchronous wrapper for getting document chunks"""
    store = AIDocumentStore()
    return await store.get_document_chunks(document_id)

# Initialize module
def initialize_ai_database():
    """
    Initialize AI database module
    """
    try:
        connection_ok = test_connection()
        if connection_ok:
            logger.info("🚀 AI Database module initialized successfully")
            return True
        else:
            logger.error("❌ AI Database module initialization failed")
            return False
    except Exception as e:
        logger.error(f"❌ AI Database module initialization error: {e}")
        return False

# Auto-initialize when module is imported
if __name__ != "__main__":
    try:
        initialize_ai_database()
    except Exception as e:
        logger.warning(f"⚠️ AI Database auto-initialization failed: {e}") 