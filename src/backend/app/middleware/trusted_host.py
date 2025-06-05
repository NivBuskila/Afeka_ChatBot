# app/middleware/trusted_host.py
"""Trusted Host middleware configuration"""

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def setup_trusted_host(app: FastAPI) -> None:
    """Configure Trusted Host middleware for production environments"""
    
    if settings.is_production:
        logger.info(f"Adding TrustedHostMiddleware with hosts: {settings.allowed_hosts_list}")
        
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts_list
        )
        
        logger.info("TrustedHost middleware configured successfully")
    else:
        logger.info("Skipping TrustedHost middleware (not in production)")