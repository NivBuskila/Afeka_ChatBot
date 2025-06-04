# app/services/factory.py
"""Service factory for dependency injection"""

from typing import Optional
from app.repositories.factory import RepositoryFactory
from .chat_service import ChatService
from .document_service import DocumentService
from .user_service import UserService
from .ai_service import AIService


class ServiceFactory:
    """Factory class for creating service instances"""
    
    def __init__(self, repository_factory: RepositoryFactory):
        self.repo_factory = repository_factory
        self._ai_service = None
    
    def create_chat_service(self) -> ChatService:
        """Create ChatService instance"""
        return ChatService(
            session_repository=self.repo_factory.create_chat_session_repository(),
            message_repository=self.repo_factory.create_chat_message_repository(),
            user_repository=self.repo_factory.create_user_repository(),
            ai_service=self.get_ai_service()
        )
    
    def create_document_service(self) -> DocumentService:
        """Create DocumentService instance"""
        return DocumentService(
            document_repository=self.repo_factory.create_document_repository()
        )
    
    def create_user_service(self) -> UserService:
        """Create UserService instance"""
        return UserService(
            user_repository=self.repo_factory.create_user_repository()
        )
    
    def get_ai_service(self) -> AIService:
        """Get AI service instance (singleton)"""
        if not self._ai_service:
            self._ai_service = AIService()
        return self._ai_service


# Global factory instance
service_factory: Optional[ServiceFactory] = None


def get_service_factory() -> ServiceFactory:
    """Get the global service factory instance"""
    if service_factory is None:
        raise RuntimeError("Service factory not initialized")
    return service_factory


def init_service_factory(repository_factory: RepositoryFactory) -> ServiceFactory:
    """Initialize the global service factory"""
    global service_factory
    service_factory = ServiceFactory(repository_factory)
    return service_factory
