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
from app.services.ai_service import AIService

# Repository dependencies
def get_user_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
) -> UserRepository:
    """Dependency to get UserRepository instance"""
    return factory.create_user_repository()

def get_chat_session_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
) -> ChatSessionRepository:
    """Dependency to get ChatSessionRepository instance"""
    return factory.create_chat_session_repository()

def get_chat_message_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
) -> ChatMessageRepository:
    """Dependency to get ChatMessageRepository instance"""
    return factory.create_chat_message_repository()

def get_document_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
) -> DocumentRepository:
    """Dependency to get DocumentRepository instance"""
    return factory.create_document_repository()

# Service dependencies
def get_chat_service(
    factory: ServiceFactory = Depends(get_service_factory)
) -> ChatService:
    """Dependency to get ChatService instance"""
    return factory.create_chat_service()

def get_document_service(
    factory: ServiceFactory = Depends(get_service_factory)
) -> DocumentService:
    """Dependency to get DocumentService instance"""
    return factory.create_document_service()

def get_user_service(
    factory: ServiceFactory = Depends(get_service_factory)
) -> UserService:
    """Dependency to get UserService instance"""
    return factory.create_user_service()

def get_ai_service(
    factory: ServiceFactory = Depends(get_service_factory)
) -> AIService:
    """Dependency to get AI service instance"""
    return factory.get_ai_service()