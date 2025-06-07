# src/backend/app/repositories/factory.py
"""Repository factory for dependency injection with RAG support"""

from typing import Optional
from supabase import Client
from .user_repository import UserRepository
from .chat_repository import ChatSessionRepository, ChatMessageRepository
from .document_repository import DocumentRepository

# Import new RAG repositories
try:
    from .rag_document_repository import RAGDocumentRepository
    from .chunk_repository import ChunkRepository
    _HAS_RAG_REPOS = True
except ImportError:
    _HAS_RAG_REPOS = False


class RepositoryFactory:
    """Factory class for creating repository instances with RAG support"""
    
    def __init__(self, supabase_client: Optional[Client] = None):
        self.supabase_client = supabase_client
        
        # Cache repository instances
        self._user_repo: Optional[UserRepository] = None
        self._chat_session_repo: Optional[ChatSessionRepository] = None
        self._chat_message_repo: Optional[ChatMessageRepository] = None
        self._document_repo: Optional[DocumentRepository] = None
        
        # RAG repository caches
        if _HAS_RAG_REPOS:
            self._rag_document_repo: Optional[RAGDocumentRepository] = None
            self._chunk_repo: Optional[ChunkRepository] = None
    
    # === Existing Repository Methods ===
    
    def create_user_repository(self) -> UserRepository:
        """Create UserRepository instance"""
        if not self._user_repo:
            self._user_repo = UserRepository(self.supabase_client)
        return self._user_repo
    
    def create_chat_session_repository(self) -> ChatSessionRepository:
        """Create ChatSessionRepository instance"""
        if not self._chat_session_repo:
            self._chat_session_repo = ChatSessionRepository(self.supabase_client)
        return self._chat_session_repo
    
    def create_chat_message_repository(self) -> ChatMessageRepository:
        """Create ChatMessageRepository instance"""
        if not self._chat_message_repo:
            self._chat_message_repo = ChatMessageRepository(self.supabase_client)
        return self._chat_message_repo
    
    def create_document_repository(self) -> DocumentRepository:
        """Create DocumentRepository instance"""
        if not self._document_repo:
            self._document_repo = DocumentRepository(self.supabase_client)
        return self._document_repo
    
    # === New RAG Repository Methods ===
    
    def create_rag_document_repository(self) -> 'RAGDocumentRepository':
        """Create RAG DocumentRepository instance"""
        if not _HAS_RAG_REPOS:
            raise ImportError("RAG repositories not available. Ensure RAG domain models are properly installed.")
        
        if not self._rag_document_repo:
            self._rag_document_repo = RAGDocumentRepository(self.supabase_client)
        return self._rag_document_repo
    
    def create_chunk_repository(self) -> 'ChunkRepository':
        """Create ChunkRepository instance"""
        if not _HAS_RAG_REPOS:
            raise ImportError("RAG repositories not available. Ensure RAG domain models are properly installed.")
        
        if not self._chunk_repo:
            self._chunk_repo = ChunkRepository(self.supabase_client)
        return self._chunk_repo
    
    # === Property-based Access (for backward compatibility) ===
    
    @property
    def user_repository(self) -> UserRepository:
        """Get UserRepository instance (property access)"""
        return self.create_user_repository()
    
    @property
    def chat_session_repository(self) -> ChatSessionRepository:
        """Get ChatSessionRepository instance (property access)"""
        return self.create_chat_session_repository()
    
    @property
    def chat_message_repository(self) -> ChatMessageRepository:
        """Get ChatMessageRepository instance (property access)"""
        return self.create_chat_message_repository()
    
    @property
    def document_repository(self) -> DocumentRepository:
        """Get DocumentRepository instance (property access)"""
        return self.create_document_repository()
    
    # === New RAG Repository Properties ===
    
    if _HAS_RAG_REPOS:
        @property
        def rag_document_repository(self) -> 'RAGDocumentRepository':
            """Get RAG DocumentRepository instance (property access)"""
            return self.create_rag_document_repository()
        
        @property
        def chunk_repository(self) -> 'ChunkRepository':
            """Get ChunkRepository instance (property access)"""
            return self.create_chunk_repository()
    
    # === Utility Methods ===
    
    def get_all_repositories(self) -> dict:
        """Get all available repositories as a dictionary"""
        repos = {
            'user': self.create_user_repository(),
            'chat_session': self.create_chat_session_repository(),
            'chat_message': self.create_chat_message_repository(),
            'document': self.create_document_repository(),
        }
        
        if _HAS_RAG_REPOS:
            repos.update({
                'rag_document': self.create_rag_document_repository(),
                'chunk': self.create_chunk_repository(),
            })
        
        return repos
    
    def health_check(self) -> dict:
        """Perform health check on all repositories"""
        health_status = {
            'database_connection': bool(self.supabase_client),
            'repositories_available': {
                'user': True,
                'chat_session': True,
                'chat_message': True,
                'document': True,
                'rag_document': _HAS_RAG_REPOS,
                'chunk': _HAS_RAG_REPOS,
            },
            'rag_support': _HAS_RAG_REPOS
        }
        
        return health_status
    
    def clear_cache(self):
        """Clear all cached repository instances"""
        self._user_repo = None
        self._chat_session_repo = None
        self._chat_message_repo = None
        self._document_repo = None
        
        if _HAS_RAG_REPOS:
            self._rag_document_repo = None
            self._chunk_repo = None


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


def reset_repository_factory():
    """Reset the global repository factory (for testing)"""
    global repository_factory
    repository_factory = None


# Utility functions for RAG availability
def is_rag_available() -> bool:
    """Check if RAG repositories are available"""
    return _HAS_RAG_REPOS


def get_rag_repositories(factory: Optional[RepositoryFactory] = None) -> dict:
    """Get RAG repositories if available"""
    if not _HAS_RAG_REPOS:
        return {}
    
    if factory is None:
        factory = get_repository_factory()
    
    return {
        'rag_document': factory.create_rag_document_repository(),
        'chunk': factory.create_chunk_repository(),
    }