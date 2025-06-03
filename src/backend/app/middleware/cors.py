# app/middleware/cors.py
"""CORS middleware configuration"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware for the application"""
    
    logger.info(f"Configuring CORS with allowed origins: {settings.allowed_origins_list}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=600  # 10 minutes cache for preflight requests
    )
    
    logger.info("CORS middleware configured successfully")