# app/api/v1/__init__.py
"""API v1 routers"""

from fastapi import APIRouter
from .health import router as health_router
from .chat import router as chat_router
from .documents import router as documents_router
from .proxy import router as proxy_router  # Add proxy router

# # Create main v1 router
# api_router = APIRouter(prefix="/api/v1")
api_router = APIRouter(prefix="/api")

# Include all routers
api_router.include_router(health_router)
api_router.include_router(chat_router)
api_router.include_router(documents_router)
api_router.include_router(proxy_router)  # Include proxy router

__all__ = ["api_router"]