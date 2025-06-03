# app/repositories/factory.py
"""Repository factory for dependency injection"""

from typing import Optional
from supabase import Client
from .user_repository import UserRepository
from .chat_repository import ChatSessionRepository, ChatMessageRepository
from .document_repository import DocumentRepository

class RepositoryFactory:
    """Factory class for creating repository instances"""
    
    def __init__(self, supabase_client: Optional[Client] = None):
        self.supabase_client = supabase_client
    
    def create_user_repository(self) -> UserRepository:
        """Create UserRepository instance"""
        return UserRepository(self.supabase_client)
    
    def create_chat_session_repository(self) -> ChatSessionRepository:
        """Create ChatSessionRepository instance"""
        return ChatSessionRepository(self.supabase_client)
    
    def create_chat_message_repository(self) -> ChatMessageRepository:
        """Create ChatMessageRepository instance"""
        return ChatMessageRepository(self.supabase_client)
    
    def create_document_repository(self) -> DocumentRepository:
        """Create DocumentRepository instance"""
        return DocumentRepository(self.supabase_client)

# Global factory instance (will be initialized in main.py)
repository_factory: Optional[RepositoryFactory] = None

def get_repository_factory() -> RepositoryFactory:
    """Get the global repository factory instance"""
    if repository_factory is None:
        raise RuntimeError("Repository factory not initialized")
    return repository_factory

def init_repository_factory(supabase_client: Optional[Client] = None) -> RepositoryFactory:
    """Initialize the global repository factory"""
    global repository_factory
    repository_factory = RepositoryFactory(supabase_client)
    return repository_factory