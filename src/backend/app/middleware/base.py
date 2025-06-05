# app/middleware/base.py
"""Base middleware class"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

logger = logging.getLogger(__name__)


class BaseMiddleware(BaseHTTPMiddleware):
    """Base class for custom middleware"""
    
    def __init__(self, app: ASGIApp, **kwargs):
        super().__init__(app)
        self.logger = logger
        
        # Log middleware initialization
        middleware_name = self.__class__.__name__
        self.logger.info(f"{middleware_name} initialized with options: {kwargs}")
