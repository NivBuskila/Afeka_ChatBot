from fastapi import HTTPException
from typing import Optional, Any, Callable
from functools import wraps
from .logger import get_logger

logger = get_logger(__name__)

def handle_api_errors(default_message: str = "Internal server error", status_code: int = 500):
    """
    Decorator for consistent API error handling.
    
    Args:
        default_message: Default error message
        status_code: Default HTTP status code
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTPExceptions as-is
                raise
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status_code,
                    detail=f"{default_message}: {str(e)}"
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTPExceptions as-is
                raise
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status_code,
                    detail=f"{default_message}: {str(e)}"
                )
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class ServiceError(Exception):
    """Base exception for service layer errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class ValidationError(ServiceError):
    """Validation error exception"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class NotFoundError(ServiceError):
    """Resource not found exception"""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)

class AuthenticationError(ServiceError):
    """Authentication error exception"""
    def __init__(self, message: str):
        super().__init__(message, status_code=401)

class AuthorizationError(ServiceError):
    """Authorization error exception"""
    def __init__(self, message: str):
        super().__init__(message, status_code=403) 