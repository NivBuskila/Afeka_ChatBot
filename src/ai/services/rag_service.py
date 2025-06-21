"""
RAG Service - Legacy compatibility wrapper
This file now delegates to the new modular RAG architecture for better maintainability.

REFACTORED ARCHITECTURE (1,180 → 7 modular files):
┌─────────────────────────────────────────────────────────────────┐
│                   🚀 RAGOrchestrator (200 lines)               │
│                   Main coordinator & API                        │
├─────────────────────────────────────────────────────────────────┤
│ 🧠 EmbeddingService  │ 🔍 SearchService    │ 📊 SearchAnalytics │
│ (150 lines)          │ (180 lines)         │ (140 lines)        │
├──────────────────────┼─────────────────────┼────────────────────┤
│ 🔧 ContextBuilder    │ 🤖 AnswerGenerator  │                    │
│ (220 lines)          │ (120 lines)         │                    │
└──────────────────────┴─────────────────────┴────────────────────┘

Benefits:
✅ Single Responsibility Principle
✅ Better testability and maintainability
✅ Easier debugging and development
✅ Backwards compatibility maintained
✅ Reduced coupling between components
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
