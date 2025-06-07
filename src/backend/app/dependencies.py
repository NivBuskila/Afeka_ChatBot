# src/backend/app/dependencies.py
"""FastAPI dependency injection helpers with RAG support"""

from fastapi import Depends
from app.repositories.factory import get_repository_factory, RepositoryFactory, is_rag_available
from app.repositories.user_repository import UserRepository
from app.repositories.chat_repository import ChatSessionRepository, ChatMessageRepository
from app.repositories.document_repository import DocumentRepository

# Import RAG repositories if available
if is_rag_available():
    from app.repositories.rag_document_repository import RAGDocumentRepository
    from app.repositories.chunk_repository import ChunkRepository

# Import services
from app.services.factory import get_service_factory, ServiceFactory
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.user_service import UserService
from app.services.ai_service import AIServiceClient, AIService


# === Existing Repository Dependencies ===

def get_user_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
) -> UserRepository:
    """Dependency to get UserRepository instance"""
    return factory.user_repository

def get_chat_session_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
) -> ChatSessionRepository:
    """Dependency to get ChatSessionRepository instance"""
    return factory.chat_session_repository

def get_chat_message_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
) -> ChatMessageRepository:
    """Dependency to get ChatMessageRepository instance"""
    return factory.chat_message_repository

def get_document_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
) -> DocumentRepository:
    """Dependency to get DocumentRepository instance"""
    return factory.document_repository


# === New RAG Repository Dependencies ===

def get_rag_document_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
):
    """Dependency to get RAG DocumentRepository instance"""
    if not is_rag_available():
        raise RuntimeError("RAG repositories not available. Ensure Phase 1 foundation is properly installed.")
    return factory.create_rag_document_repository()

def get_chunk_repository(
    factory: RepositoryFactory = Depends(get_repository_factory)
):
    """Dependency to get ChunkRepository instance"""
    if not is_rag_available():
        raise RuntimeError("RAG repositories not available. Ensure Phase 1 foundation is properly installed.")
    return factory.create_chunk_repository()


# === Existing Service Dependencies ===

def get_chat_service(
    factory: ServiceFactory = Depends(get_service_factory)
) -> ChatService:
    """Dependency to get ChatService instance"""
    return factory.chat_service

def get_document_service(
    factory: ServiceFactory = Depends(get_service_factory)
) -> DocumentService:
    """Dependency to get DocumentService instance"""
    return factory.document_service

def get_user_service(
    factory: ServiceFactory = Depends(get_service_factory)
) -> UserService:
    """Dependency to get UserService instance"""
    return factory.create_user_service()

def get_ai_service(
    factory: ServiceFactory = Depends(get_service_factory)
) -> AIServiceClient:
    """Dependency to get AI service client instance"""
    return factory.ai_service

# Legacy alias for backward compatibility
def get_ai_service_legacy(
    factory: ServiceFactory = Depends(get_service_factory)
) -> AIService:
    """Legacy dependency - use get_ai_service instead"""
    return factory.get_ai_service()

# Additional AI-specific dependencies for direct injection
def get_ai_service_client() -> AIServiceClient:
    """Direct AI service client dependency (singleton)"""
    return _get_ai_service_singleton()

# Health check dependency
async def get_ai_service_health() -> dict:
    """Get AI service health status"""
    ai_service = _get_ai_service_singleton()
    return await ai_service.health_check()


# === New RAG Service Dependencies (when services are implemented) ===

# Note: These will be implemented in Phase 3 (Service Layer)
# Commented out for now to avoid import errors

# def get_document_processing_service(
#     factory: ServiceFactory = Depends(get_service_factory)
# ):
#     """Dependency to get Document Processing Service instance"""
#     return factory.create_document_processing_service()

# def get_rag_search_service(
#     factory: ServiceFactory = Depends(get_service_factory)
# ):
#     """Dependency to get RAG Search Service instance"""
#     return factory.create_rag_search_service()

# def get_enhanced_rag_service(
#     factory: ServiceFactory = Depends(get_service_factory)
# ):
#     """Dependency to get Enhanced RAG Service instance"""
#     return factory.create_enhanced_rag_service()


# === Combined Dependencies for Complex Operations ===

def get_repositories_bundle(factory: RepositoryFactory = Depends(get_repository_factory)):
    """Get multiple repositories for complex operations"""
    bundle = {
        'user': factory.create_user_repository(),
        'chat_session': factory.create_chat_session_repository(),
        'chat_message': factory.create_chat_message_repository(),
        'document': factory.create_document_repository(),
    }
    
    # Add RAG repositories if available
    if is_rag_available():
        bundle.update({
            'rag_document': factory.create_rag_document_repository(),
            'chunk': factory.create_chunk_repository(),
        })
    
    return bundle

def get_services_bundle(factory: ServiceFactory = Depends(get_service_factory)):
    """Get multiple services for complex operations"""
    return {
        'chat_service': factory.chat_service,
        'ai_service': factory.ai_service,
        'document_service': factory.document_service,
        'user_service': factory.create_user_service(),
    }


# === Health Check Dependencies ===

def get_repository_health(factory: RepositoryFactory = Depends(get_repository_factory)) -> dict:
    """Get repository layer health status"""
    return factory.health_check()

async def get_system_health(
    repo_health: dict = Depends(get_repository_health),
    ai_health: dict = Depends(get_ai_service_health)
) -> dict:
    """Get comprehensive system health status"""
    return {
        "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
        "status": "healthy",
        "repositories": repo_health,
        "ai_service": ai_health,
        "rag_support": is_rag_available()
    }


# === Private Utility Functions ===

# Private singleton management
_ai_service_instance: AIServiceClient = None

def _get_ai_service_singleton() -> AIServiceClient:
    """Get or create AI service singleton instance"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIServiceClient()
    return _ai_service_instance

def reset_ai_service_singleton():
    """Reset the AI service singleton (for testing)"""
    global _ai_service_instance
    _ai_service_instance = None


# === Conditional Type Hints (for IDE support) ===

# Type hints that work regardless of RAG availability
if is_rag_available():
    RAGDocumentRepositoryType = RAGDocumentRepository
    ChunkRepositoryType = ChunkRepository
else:
    # Create placeholder types for IDE support
    RAGDocumentRepositoryType = type('RAGDocumentRepository', (), {})
    ChunkRepositoryType = type('ChunkRepository', (), {})


# === Utility Functions ===

def get_available_dependencies() -> dict:
    """Get information about available dependencies"""
    return {
        "repositories": {
            "user": True,
            "chat_session": True,
            "chat_message": True,
            "document": True,
            "rag_document": is_rag_available(),
            "chunk": is_rag_available(),
        },
        "services": {
            "chat": True,
            "document": True,
            "user": True,
            "ai": True,
        },
        "rag_support": is_rag_available(),
        "features": {
            "vector_search": is_rag_available(),
            "semantic_search": is_rag_available(),
            "document_processing": is_rag_available(),
        }
    }