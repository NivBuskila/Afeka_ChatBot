# src/backend/app/repositories/__init__.py
"""Repository layer exports"""

# Import base repository first
from .base import BaseRepository

# Import factory - but be careful about circular imports
try:
    from .factory import RepositoryFactory, get_repository_factory
    _HAS_FACTORY = True
except ImportError:
    _HAS_FACTORY = False

# Import specific repositories if they exist
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

# Build exports list
__all__ = ["BaseRepository"]

if _HAS_FACTORY:
    __all__.extend(["RepositoryFactory", "get_repository_factory"])

if _HAS_USER_REPO:
    __all__.append("UserRepository")

if _HAS_CHAT_REPO:
    __all__.extend(["ChatSessionRepository", "ChatMessageRepository"])

if _HAS_DOCUMENT_REPO:
    __all__.append("DocumentRepository")