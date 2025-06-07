# src/backend/app/domain/__init__.py
"""Domain models for the Afeka ChatBot API"""

# Import existing base classes first (your original models)
from .base import (
    DomainEntity, 
    TimestampedEntity,
    # New RAG foundation classes
    BaseEntity,
    BaseValueObject,
    FileMetadata,
    EmbeddingVector,
    TextChunk,
    DomainEvent,
    DocumentProcessedEvent,
    # Utility functions
    create_file_metadata_from_upload,
    create_text_chunks_from_content
)

# Import existing domain models (conditional to prevent errors)
try:
    from .chat import ChatSession, ChatMessage
    _HAS_CHAT = True
except ImportError:
    _HAS_CHAT = False

try:
    from .document import Document
    _HAS_DOCUMENT = True
except ImportError:
    _HAS_DOCUMENT = False

try:
    from .user import User, Admin
    _HAS_USER = True
except ImportError:
    _HAS_USER = False

# Import RAG domain models (conditional for Phase 1)
try:
    from .rag import (
        ProcessingStatus,
        SearchType,
        Document as RAGDocument,  # Alias to avoid conflict with existing Document
        DocumentChunk,
        SearchResult,
        ProcessingResult,
        RAGResponse,
        EmbeddingResult,
        ContextWindow,
        DocumentDomainService,
        ChunkDomainService,
        SearchDomainService
    )
    _HAS_RAG = True
except ImportError:
    _HAS_RAG = False
    # Define minimal ProcessingStatus for compatibility
    class ProcessingStatus:
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

# Build dynamic exports list
__all__ = [
    # Original base classes (always available)
    'DomainEntity',
    'TimestampedEntity',
    
    # New RAG base classes (always available)
    'BaseEntity',
    'BaseValueObject',
    'FileMetadata',
    'EmbeddingVector',
    'TextChunk',
    'DomainEvent',
    'DocumentProcessedEvent',
    
    # Utility functions
    'create_file_metadata_from_upload',
    'create_text_chunks_from_content',
    
    # Always include ProcessingStatus (either real or placeholder)
    'ProcessingStatus'
]

# Add existing domain models if available
if _HAS_CHAT:
    __all__.extend(['ChatSession', 'ChatMessage'])

if _HAS_DOCUMENT:
    __all__.extend(['Document'])

if _HAS_USER:
    __all__.extend(['User', 'Admin'])

# Add RAG domain models if available
if _HAS_RAG:
    __all__.extend([
        'SearchType',
        'RAGDocument',
        'DocumentChunk',
        'SearchResult', 
        'ProcessingResult',
        'RAGResponse',
        'EmbeddingResult',
        'ContextWindow',
        'DocumentDomainService',
        'ChunkDomainService',
        'SearchDomainService'
    ])

# For backward compatibility, make Document refer to the original if available
if _HAS_DOCUMENT and not _HAS_RAG:
    # Only original Document available
    pass
elif _HAS_DOCUMENT and _HAS_RAG:
    # Both available - keep original Document as default, RAGDocument as alias
    pass
elif not _HAS_DOCUMENT and _HAS_RAG:
    # Only RAG Document available - make it the default Document
    Document = RAGDocument
    __all__.append('Document')