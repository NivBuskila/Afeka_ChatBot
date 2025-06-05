# app/services/base.py
"""Base service class"""

from abc import ABC
import logging
from typing import Optional


class BaseService(ABC):
    """Base class for all services"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"{self.__class__.__name__} initialized")
    
    def _log_operation(self, operation: str, details: Optional[str] = None):
        """Log service operations"""
        message = f"{operation}"
        if details:
            message += f": {details}"
        self.logger.info(message)
    
    def _log_error(self, operation: str, error: Exception):
        """Log service errors"""
        self.logger.error(f"Error in {operation}: {error}", exc_info=True)
