# app/services/__init__.py
"""Service layer exports"""

from .base import BaseService
from .chat_service import ChatService
from .document_service import DocumentService
from .user_service import UserService
from .ai_service import AIServiceClient, AIService  # AIService is alias for backward compatibility
from .auth_service import AuthService
from .factory import ServiceFactory, get_service_factory, init_service_factory

__all__ = [
    "BaseService",
    "ChatService", 
    "DocumentService",
    "UserService",
    "AIServiceClient",
    "AIService",  # Legacy alias
    "AuthService",
    "ServiceFactory",
    "get_service_factory",
    "init_service_factory"
]
