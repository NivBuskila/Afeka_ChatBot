# app/dependencies.py
"""FastAPI dependency injection helpers"""

from fastapi import Depends
from app.repositories.factory import get_repository_factory, RepositoryFactory
from app.repositories.user_repository import UserRepository
from app.repositories.chat_repository import ChatSessionRepository, ChatMessageRepository
from app.repositories.document_repository import DocumentRepository
from app.services.factory import get_service_factory, ServiceFactory
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.user_service import UserService
from app.services.ai_service import AIServiceClient, AIService

# Repository dependencies
def get_user_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
) -> UserRepository:
    """Dependency to get UserRepository instance"""
    return factory.user_repository

def get_chat_session_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
) -> ChatSessionRepository:
    """Dependency to get ChatSessionRepository instance"""
    return factory.chat_session_repository

def get_chat_message_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
) -> ChatMessageRepository:
    """Dependency to get ChatMessageRepository instance"""
    return factory.chat_message_repository

def get_document_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
) -> DocumentRepository:
    """Dependency to get DocumentRepository instance"""
    return factory.document_repository

# Service dependencies
def get_chat_service(
    factory: ServiceFactory = Depends(get_service_factory)
) -> ChatService:
    """Dependency to get ChatService instance"""
    return factory.chat_service

def get_document_service(
    factory: ServiceFactory = Depends(get_service_factory)
) -> DocumentService:
    """Dependency to get DocumentService instance"""
    return factory.document_service

def get_user_service(
    factory: ServiceFactory = Depends(get_service_factory)
) -> UserService:
    """Dependency to get UserService instance"""
    return factory.create_user_service()

def get_ai_service(
    factory: ServiceFactory = Depends(get_service_factory)
) -> AIServiceClient:
    """Dependency to get AI service client instance"""
    return factory.ai_service

# Legacy alias for backward compatibility
def get_ai_service_legacy(
    factory: ServiceFactory = Depends(get_service_factory)
) -> AIService:
    """Legacy dependency - use get_ai_service instead"""
    return factory.get_ai_service()

# Additional AI-specific dependencies for direct injection
def get_ai_service_client() -> AIServiceClient:
    """Direct AI service client dependency (singleton)"""
    return _get_ai_service_singleton()

# Health check dependency
async def get_ai_service_health() -> dict:
    """Get AI service health status"""
    ai_service = _get_ai_service_singleton()
    return await ai_service.health_check()

# Private singleton management
_ai_service_instance: AIServiceClient = None

def _get_ai_service_singleton() -> AIServiceClient:
    """Get or create AI service singleton instance"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIServiceClient()
    return _ai_service_instance

def reset_ai_service_singleton():
    """Reset the AI service singleton (for testing)"""
    global _ai_service_instance
    _ai_service_instance = None

# ✅ ADD: Combined dependencies for complex operations
def get_services_bundle(factory: ServiceFactory = Depends(get_service_factory)):
    """Get multiple services for complex operations"""
    return {
        'chat_service': factory.chat_service,
        'ai_service': factory.ai_service,
        'document_service': factory.document_service
    }