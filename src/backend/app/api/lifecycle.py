# # app/api/lifecycle.py
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