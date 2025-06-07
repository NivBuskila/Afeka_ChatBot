# src/backend/app/core/rag_exceptions.py
"""Minimal RAG-specific exceptions for Phase 1"""

from typing import Optional, Dict, Any, List

# Import base exceptions - use try/except to handle missing files
try:
    from app.core.exceptions import ServiceException, ValidationException
except ImportError:
    # Create minimal base exceptions if not available
    class ServiceException(Exception):
        """Base service exception"""
        def __init__(self, message: str):
            super().__init__(message)
            self.message = message
    
    class ValidationException(Exception):
        """Base validation exception"""
        def __init__(self, message: str):
            super().__init__(message)
            self.message = message


class RAGException(ServiceException):
    """Base exception for all RAG-related errors"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.error_code = error_code or "RAG_ERROR"
        self.details = details or {}


class DocumentProcessingException(RAGException):
    """Exception raised during document processing operations"""
    
    def __init__(
        self, 
        message: str, 
        document_id: Optional[str] = None,
        processing_stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "DOCUMENT_PROCESSING_ERROR", details)
        self.document_id = document_id
        self.processing_stage = processing_stage


class EmbeddingException(RAGException):
    """Exception raised during embedding generation"""
    
    def __init__(
        self, 
        message: str, 
        text_length: Optional[int] = None,
        model_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "EMBEDDING_ERROR", details)
        self.text_length = text_length
        self.model_name = model_name


class SearchException(RAGException):
    """Exception raised during search operations"""
    
    def __init__(
        self, 
        message: str, 
        query: Optional[str] = None,
        search_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "SEARCH_ERROR", details)
        self.query = query
        self.search_type = search_type


class ValidationError(RAGException):
    """Exception for validation errors in RAG operations"""
    
    def __init__(
        self, 
        message: str, 
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        validation_rules: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field_name = field_name
        self.field_value = field_value
        self.validation_rules = validation_rules or []


# Minimal utility functions
def create_detailed_error_response(exception: RAGException) -> Dict[str, Any]:
    """Create detailed error response for API endpoints"""
    return {
        "error": {
            "message": str(exception),
            "error_code": exception.error_code,
            "details": exception.details
        }
    }


def log_rag_exception(logger, exception: RAGException, context: Optional[Dict[str, Any]] = None):
    """Log RAG exception with appropriate level and context"""
    log_data = {
        "exception_type": type(exception).__name__,
        "error_code": exception.error_code,
        "message": str(exception),
        "details": exception.details
    }
    
    if context:
        log_data["context"] = context
    
    logger.error("RAG exception", extra=log_data)


# Export minimal set for Phase 1
__all__ = [
    "RAGException",
    "DocumentProcessingException", 
    "EmbeddingException",
    "SearchException",
    "ValidationError",
    "create_detailed_error_response",
    "log_rag_exception"
]