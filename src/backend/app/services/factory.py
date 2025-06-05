# app/services/factory.py
"""Service factory for dependency injection"""

from typing import Optional
from app.repositories.factory import RepositoryFactory
from .chat_service import ChatService
from .document_service import DocumentService
from .user_service import UserService
from .ai_service import AIServiceClient


class ServiceFactory:
    """Factory class for creating service instances"""
    
    def __init__(self, repository_factory: RepositoryFactory):
        self.repo_factory = repository_factory
        self._ai_service: Optional[AIServiceClient] = None
        self._chat_service: Optional[ChatService] = None
        self._document_service: Optional[DocumentService] = None
        self._user_service: Optional[UserService] = None
    
    @property
    def ai_service(self) -> AIServiceClient:
        """AI service property for dependency injection"""
        return self.get_ai_service()
    
    @property
    def chat_service(self) -> ChatService:
        """Chat service property for dependency injection"""
        if not self._chat_service:
            self._chat_service = self.create_chat_service()
        return self._chat_service
    
    @property
    def document_service(self) -> DocumentService:
        """Document service property for dependency injection"""
        if not self._document_service:
            self._document_service = self.create_document_service()
        return self._document_service
    
    @property
    def user_service(self) -> UserService:
        """User service property for dependency injection"""
        if not self._user_service:
            self._user_service = self.create_user_service()
        return self._user_service
    
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
    
    def get_ai_service(self) -> AIServiceClient:
        """Get AI service client instance (singleton)"""
        if not self._ai_service:
            self._ai_service = AIServiceClient()
        return self._ai_service
    
    def reset_ai_service(self):
        """Reset AI service instance (useful for testing)"""
        self._ai_service = None
    
    def reset_all_services(self):
        """Reset all service instances (useful for testing)"""
        self._ai_service = None
        self._chat_service = None
        self._document_service = None
        self._user_service = None


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


def reset_service_factory():
    """Reset the global service factory (for testing)"""
    global service_factory
    if service_factory:
        service_factory.reset_all_services()
    service_factory = None
