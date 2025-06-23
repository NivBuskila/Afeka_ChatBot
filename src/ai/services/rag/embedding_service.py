"""
Embedding Service - Handles vector generation and caching
"""

import os
import logging
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import OrderedDict
import google.generativeai as genai

try:
    from ...core.database_key_manager import DatabaseKeyManager
    from ...utils.vector_utils import ensure_768_dimensions, log_vector_info
except ImportError:
    from src.ai.core.database_key_manager import DatabaseKeyManager
    from src.ai.utils.vector_utils import ensure_768_dimensions, log_vector_info

logger = logging.getLogger(__name__)

class LRUCache:
    """Simple LRU cache implementation with size limit"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: Dict[str, Any]) -> None:
        if key in self.cache:
            # Update existing key
            self.cache.move_to_end(key)
        else:
            # Add new key
            if len(self.cache) >= self.max_size:
                # Remove least recently used item
                self.cache.popitem(last=False)
        self.cache[key] = value
    
    def clear(self) -> None:
        self.cache.clear()
    
    def size(self) -> int:
        return len(self.cache)

class EmbeddingService:
    """Service for handling embedding generation and caching"""
    
    # Class-level cache with size limit
    _embedding_cache = None
    _cache_stats = {"hits": 0, "misses": 0, "total_requests": 0}
    
    def __init__(self, key_manager: Optional[DatabaseKeyManager] = None):
        self.key_manager = key_manager
        
        # Import here to avoid circular imports
        try:
            from ...config.rag_config import get_embedding_config, get_performance_config
        except ImportError:
            from src.ai.config.rag_config import get_embedding_config, get_performance_config
        
        self.embedding_config = get_embedding_config()
        self.performance_config = get_performance_config()
        
        # Initialize LRU cache if not already done
        if EmbeddingService._embedding_cache is None:
            cache_size = getattr(self.performance_config, 'EMBEDDING_CACHE_SIZE', 1000)
            EmbeddingService._embedding_cache = LRUCache(max_size=cache_size)
        
        # Initialize Gemini
        self._init_gemini()
        logger.info("EmbeddingService initialized with LRU cache")
    
    def _init_gemini(self):
        """Initialize Gemini API"""
        fallback_key = os.getenv("GEMINI_API_KEY")
        if fallback_key:
            genai.configure(api_key=fallback_key)
            logger.info("Using GEMINI_API_KEY from environment")
    
    def _generate_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        if 'timestamp' not in cache_entry:
            return False
        
        cache_duration_seconds = getattr(self.performance_config, 'EMBEDDING_CACHE_TTL_SECONDS', 3600)
        expiry_time = cache_entry['timestamp'] + timedelta(seconds=cache_duration_seconds)
        return datetime.now() < expiry_time
    
    async def _track_embedding_usage(self, text: str, key_id: Optional[int] = None):
        """Track embedding usage"""
        if self.key_manager and key_id:
            try:
                estimated_tokens = len(text) // 4  # Rough estimation
                await self.key_manager.record_usage(key_id, estimated_tokens, 1)
                logger.debug(f"Tracked {estimated_tokens} tokens for embedding")
            except Exception as e:
                logger.warning(f"Failed to track embedding usage: {e}")
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query with caching"""
        # Update cache stats
        self._cache_stats["total_requests"] += 1
        
        # Check cache
        cache_key = self._generate_cache_key(query)
        cache_entry = self._embedding_cache.get(cache_key)
        if cache_entry and self._is_cache_valid(cache_entry):
            self._cache_stats["hits"] += 1
            logger.debug(f"Cache hit for query: {query[:50]}...")
            return cache_entry['embedding']
        
        # Cache miss - generate new embedding
        self._cache_stats["misses"] += 1
        logger.debug(f"Generating embedding for query: {query[:50]}...")
        
        try:
            # Get API key if available
            key_id = None
            if self.key_manager:
                try:
                    api_key_data = await self.key_manager.get_available_key()
                    if api_key_data and 'key' in api_key_data:
                        genai.configure(api_key=api_key_data['key'])
                        key_id = api_key_data.get('id')
                except Exception as e:
                    logger.warning(f"Key manager error: {e}")
            
            # Generate embedding
            model_name = getattr(self.embedding_config, 'MODEL_NAME', 'models/embedding-001')
            response = genai.embed_content(
                model=model_name,
                content=query,
                task_type="retrieval_query"
            )
            
            if response and 'embedding' in response:
                embedding = response['embedding']
                
                # Ensure correct dimensions
                embedding = ensure_768_dimensions(embedding)
                log_vector_info(embedding, f"Query embedding for: {query[:30]}...")
                
                # Cache the result
                self._embedding_cache.put(cache_key, {
                    'embedding': embedding,
                    'timestamp': datetime.now(),
                    'query': query[:100]  # Store first 100 chars for debugging
                })
                
                # Track usage
                if key_id:
                    await self._track_embedding_usage(query, key_id)
                
                logger.debug(f"Generated embedding for query: {query[:50]}...")
                return embedding
            else:
                raise ValueError("No embedding in response")
                
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return a zero vector as fallback
            return [0.0] * 768
    
    async def generate_text_embedding(self, text: str) -> List[float]:
        """Generate embedding for text content"""
        return await self.generate_query_embedding(text)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self._cache_stats["total_requests"]
        hits = self._cache_stats["hits"]
        misses = self._cache_stats["misses"]
        
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        return {
            "total_requests": total,
            "cache_hits": hits,
            "cache_misses": misses,
            "hit_rate_percent": round(hit_rate, 2),
            "cache_size": self._embedding_cache.size()
        }
    
    def clear_cache(self):
        """Clear embedding cache"""
        self._embedding_cache.clear()
        logger.info("Embedding cache cleared")
    
    def clear_expired_cache(self):
        """Clear expired cache entries"""
        expired_keys = []
        for key, entry in self._embedding_cache.cache.items():
            if not self._is_cache_valid(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            self._embedding_cache.cache.pop(key)
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information"""
        return {
            "cache_size": self._embedding_cache.size(),
            "stats": self.get_cache_stats(),
            "config": {
                "cache_duration_seconds": getattr(self.performance_config, 'EMBEDDING_CACHE_TTL_SECONDS', 3600),
                "model_name": getattr(self.embedding_config, 'MODEL_NAME', 'models/embedding-001')
            }
        } 