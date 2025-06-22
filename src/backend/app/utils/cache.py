import time
from functools import wraps
from .common_types import Dict, Any, Optional, TypeVar, Generic
from .logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class CacheManager(Generic[T]):
    """Generic cache manager to prevent code duplication"""
    
    def __init__(self, ttl: int = 600):
        """Initialize cache with TTL in seconds"""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[T]:
        """Get cached value if still valid"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        age = time.time() - entry.get('timestamp', 0)
        
        if age > self.ttl:
            # Cache expired
            del self._cache[key]
            return None
        
        logger.info(f"[CACHE-HIT] Key: {key}, Age: {age:.1f}s")
        return entry.get('data')
    
    def set(self, key: str, data: T) -> None:
        """Set cache value"""
        self._cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        logger.info(f"[CACHE-SET] Key: {key}")
    
    def invalidate(self, key: str) -> None:
        """Invalidate specific cache entry"""
        if key in self._cache:
            del self._cache[key]
            logger.info(f"[CACHE-INVALIDATE] Key: {key}")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        logger.info("[CACHE-CLEAR] All entries cleared")

# Pre-configured cache instances for different use cases
api_keys_cache = CacheManager[Dict[str, Any]](ttl=600)  # 10 minutes
sessions_cache = CacheManager[list](ttl=60)  # 1 minute
fast_cache = CacheManager[Any](ttl=1800)  # 30 minutes

def cached(cache_manager: CacheManager, key_func=None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result)
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator 