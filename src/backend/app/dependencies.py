# app/dependencies.py
"""FastAPI dependency injection helpers"""

from fastapi import Depends
from app.repositories.factory import get_repository_factory, RepositoryFactory
from app.repositories.user_repository import UserRepository
from app.repositories.chat_repository import ChatSessionRepository, ChatMessageRepository
from app.repositories.document_repository import DocumentRepository

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