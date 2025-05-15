import logging
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from ..core.interfaces import IDocumentService, IDocumentRepository
from ..domain.models import Document
from ..config.settings import settings
from ..core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

class DocumentService(IDocumentService):
    """Service for document management."""
    
    def __init__(self, repository: IDocumentRepository):
        """Initialize with a repository implementation."""
        self.repository = repository
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all available documents."""
        try:
            return await self.repository.get_all()
        except RepositoryError as e:
            logger.error(f"Repository error in get_all_documents: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in get_all_documents: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve documents")
    
    async def get_document_by_id(self, doc_id: int) -> Dict[str, Any]:
        """Get a specific document by ID."""
        try:
            return await self.repository.get_by_id(doc_id)
        except RepositoryError as e:
            logger.error(f"Repository error in get_document_by_id({doc_id}): {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in get_document_by_id({doc_id}): {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve document")
    
    async def create_document(self, document: Document) -> Dict[str, Any]:
        """Create a new document."""
        # Validate document size
        if len(document.content) > settings.MAX_DOCUMENT_SIZE_BYTES:
            raise HTTPException(
                status_code=400, 
                detail=f"Document content too large (max {settings.MAX_DOCUMENT_SIZE_KB}KB)"
            )
        
        try:
            result = await self.repository.create(document)
            return {
                "success": True, 
                "id": result.get("id"), 
                "message": "Document created successfully"
            }
        except RepositoryError as e:
            logger.error(f"Repository error in create_document: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in create_document: {e}")
            raise HTTPException(status_code=500, detail="Failed to create document")