"""
RAG Service Modules - Refactored Architecture
========================================

This package contains the refactored RAG service split into modular components:

- rag_orchestrator: Main coordinator (200 lines)
- embedding_service: Handles embeddings and caching
- search_services: Semantic, hybrid, and contextual search
- context_builder: Context assembly and prompt building
- answer_generator: Answer generation with retry logic
- search_analytics: Analytics and usage tracking
"""

from .rag_orchestrator import RAGOrchestrator
from .embedding_service import EmbeddingService
from .search_services import SearchService
from .context_builder import ContextBuilder
from .answer_generator import AnswerGenerator
from .search_analytics import SearchAnalytics

# Backwards compatibility - maintain the same interface
def get_rag_service():
    """Factory function for RAG service - maintains backwards compatibility"""
    return RAGOrchestrator()

__all__ = [
    'RAGOrchestrator',
    'EmbeddingService', 
    'SearchService',
    'ContextBuilder',
    'AnswerGenerator',
    'SearchAnalytics',
    'get_rag_service'
] 