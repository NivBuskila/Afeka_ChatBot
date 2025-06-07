# src/backend/app/core/__init__.py
"""Core application components"""

# Import base exceptions if they exist
try:
    from .exceptions import ServiceException, ValidationException
    _HAS_BASE_EXCEPTIONS = True
except ImportError:
    _HAS_BASE_EXCEPTIONS = False
    # Create minimal base exceptions
    class ServiceException(Exception):
        def __init__(self, message: str):
            super().__init__(message)
            self.message = message
    
    class ValidationException(Exception):
        def __init__(self, message: str):
            super().__init__(message)
            self.message = message

# Import RAG exceptions
try:
    from .rag_exceptions import (
        RAGException,
        DocumentProcessingException,
        EmbeddingException,
        SearchException,
        ValidationError,
        create_detailed_error_response,
        log_rag_exception
    )
    _HAS_RAG_EXCEPTIONS = True
except ImportError:
    _HAS_RAG_EXCEPTIONS = False

# Build exports list
__all__ = ["ServiceException", "ValidationException"]

if _HAS_RAG_EXCEPTIONS:
    __all__.extend([
        "RAGException",
        "DocumentProcessingException",
        "EmbeddingException", 
        "SearchException",
        "ValidationError",
        "create_detailed_error_response",
        "log_rag_exception"
    ])