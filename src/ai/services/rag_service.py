"""
RAG Service - Legacy compatibility wrapper
This file now delegates to the new modular RAG architecture for better maintainability.
"""

from .rag import RAGOrchestrator, get_rag_service

# Backwards compatibility - export the same class name and factory function
RAGService = RAGOrchestrator

# Legacy imports for backwards compatibility
from .rag.embedding_service import EmbeddingService
from .rag.search_services import SearchService
from .rag.context_builder import ContextBuilder
from .rag.answer_generator import AnswerGenerator
from .rag.search_analytics import SearchAnalytics

__all__ = [
    'RAGService',
    'RAGOrchestrator', 
    'get_rag_service',
    'EmbeddingService',
    'SearchService', 
    'ContextBuilder',
    'AnswerGenerator',
    'SearchAnalytics'
]
