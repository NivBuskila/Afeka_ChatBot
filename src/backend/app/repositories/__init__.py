# src/backend/app/repositories/__init__.py
"""Repository layer exports with RAG support"""

# Import base repository first
from .base import BaseRepository

# Import factory
try:
    from .factory import (
        RepositoryFactory, 
        get_repository_factory,
        init_repository_factory,
        reset_repository_factory,
        is_rag_available,
        get_rag_repositories
    )
    _HAS_FACTORY = True
except ImportError:
    _HAS_FACTORY = False

# Import existing repositories
try:
    from .user_repository import UserRepository
    _HAS_USER_REPO = True
except ImportError:
    _HAS_USER_REPO = False

try:
    from .chat_repository import ChatSessionRepository, ChatMessageRepository
    _HAS_CHAT_REPO = True
except ImportError:
    _HAS_CHAT_REPO = False

try:
    from .document_repository import DocumentRepository
    _HAS_DOCUMENT_REPO = True
except ImportError:
    _HAS_DOCUMENT_REPO = False

# Import new RAG repositories
try:
    from .rag_document_repository import RAGDocumentRepository
    from .chunk_repository import ChunkRepository
    _HAS_RAG_REPOS = True
except ImportError:
    _HAS_RAG_REPOS = False

# Build exports list dynamically
__all__ = ["BaseRepository"]

# Add factory exports
if _HAS_FACTORY:
    __all__.extend([
        "RepositoryFactory", 
        "get_repository_factory",
        "init_repository_factory",
        "reset_repository_factory",
        "is_rag_available",
        "get_rag_repositories"
    ])

# Add existing repository exports
if _HAS_USER_REPO:
    __all__.append("UserRepository")

if _HAS_CHAT_REPO:
    __all__.extend(["ChatSessionRepository", "ChatMessageRepository"])

if _HAS_DOCUMENT_REPO:
    __all__.append("DocumentRepository")

# Add RAG repository exports
if _HAS_RAG_REPOS:
    __all__.extend(["RAGDocumentRepository", "ChunkRepository"])

# Utility function to check repository availability
def get_available_repositories() -> dict:
    """Get information about available repositories"""
    return {
        "base": True,
        "factory": _HAS_FACTORY,
        "existing": {
            "user": _HAS_USER_REPO,
            "chat": _HAS_CHAT_REPO,
            "document": _HAS_DOCUMENT_REPO,
        },
        "rag": {
            "available": _HAS_RAG_REPOS,
            "rag_document": _HAS_RAG_REPOS,
            "chunk": _HAS_RAG_REPOS,
        },
        "total_repositories": len(__all__) - 1  # Exclude BaseRepository from count
    }

# Add utility function to exports
__all__.append("get_available_repositories")