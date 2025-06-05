# # app/api/lifecycle.py
# """Application lifecycle handlers"""

# from fastapi import FastAPI
# import logging
# from typing import Optional
# from app.config import settings

# logger = logging.getLogger(__name__)


# async def startup_handler(app: FastAPI) -> None:
#     """Handle application startup"""
#     logger.info("=" * 50)
#     logger.info(f"Starting {settings.app_name} v{settings.app_version}")
#     logger.info(f"Environment: {settings.environment}")
#     logger.info(f"API URL: http://{settings.host}:{settings.port}")
#     if settings.is_development:
#         logger.info(f"API Docs: http://{settings.host}:{settings.port}/docs")
#     logger.info("=" * 50)
    
#     # Verify critical services
#     if hasattr(app.state, 'supabase_client') and app.state.supabase_client:
#         logger.info("✓ Database connection available")
#     else:
#         logger.warning("✗ Database connection not available - running in degraded mode")
    
#     # Initialize background tasks if needed
#     # app.state.background_tasks = BackgroundTasks()
    
#     logger.info("Application startup complete")


# async def shutdown_handler(app: FastAPI) -> None:
#     """Handle application shutdown"""
#     logger.info("Shutting down application...")
    
#     # Close database connections
#     if hasattr(app.state, 'supabase_client') and app.state.supabase_client:
#         # Supabase client doesn't need explicit closing
#         logger.info("Database connections closed")
    
#     # Cancel background tasks
#     # if hasattr(app.state, 'background_tasks'):
#     #     await app.state.background_tasks.cancel_all()
    
#     logger.info("Application shutdown complete")


# def register_lifecycle_handlers(app: FastAPI) -> None:
#     """Register startup and shutdown handlers"""
#     app.add_event_handler("startup", lambda: startup_handler(app))
#     app.add_event_handler("shutdown", lambda: shutdown_handler(app))

# app/api/lifecycle.py
"""Application lifecycle handlers"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from app.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 50)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"API URL: http://{settings.host}:{settings.port}")
    if settings.is_development:
        logger.info(f"API Docs: http://{settings.host}:{settings.port}/docs")
    logger.info("=" * 50)
    
    # Verify critical services
    if hasattr(app.state, 'supabase_client') and app.state.supabase_client:
        logger.info("✓ Database connection available")
    else:
        logger.warning("✗ Database connection not available - running in degraded mode")
    
    logger.info("Application startup complete")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down application...")
    
    if hasattr(app.state, 'supabase_client') and app.state.supabase_client:
        logger.info("Database connections closed")
    
    logger.info("Application shutdown complete")