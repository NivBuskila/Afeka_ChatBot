# app/services/document_service.py
"""Document service implementation"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.base import BaseService
from app.repositories.document_repository import DocumentRepository
from app.domain.document import Document
from app.core.exceptions import ServiceException


class DocumentService(BaseService):
    """Service for managing documents"""
    
    def __init__(self, document_repository: DocumentRepository):
        super().__init__()
        self.document_repo = document_repository
    
    async def get_all_documents(
        self,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Document]:
        """Get all documents, optionally filtered by category"""
        try:
            self._log_operation("get_all_documents", f"category={category}")
            
            if category:
                documents = await self.document_repo.find_by_category(category)
            else:
                documents = await self.document_repo.find_all(limit=limit)
            
            return documents
            
        except Exception as e:
            self._log_error("get_all_documents", e)
            return []
    
    async def get_document(self, document_id: int) -> Optional[Document]:
        """Get a specific document by ID"""
        try:
            self._log_operation("get_document", f"id={document_id}")
            return await self.document_repo.find_by_id(document_id)
            
        except Exception as e:
            self._log_error("get_document", e)
            return None
    
    async def create_document(self, document: Document) -> Document:
        """Create a new document"""
        try:
            self._log_operation("create_document", document.name)
            
            # Validate document
            if not document.name or not document.url:
                raise ServiceException("Document name and URL are required")
            
            # Set processing status
            document.processing_status = "pending"
            
            created_doc = await self.document_repo.create(document)
            if not created_doc:
                raise ServiceException("Failed to create document")
            
            # TODO: Trigger document processing (OCR, embedding, etc.)
            self._trigger_document_processing(created_doc)
            
            return created_doc
            
        except Exception as e:
            self._log_error("create_document", e)
            raise ServiceException(f"Failed to create document: {str(e)}")
    
    async def update_document(
        self,
        document_id: int,
        updates: Dict[str, Any]
    ) -> Optional[Document]:
        """Update a document"""
        try:
            self._log_operation("update_document", f"id={document_id}")
            
            # Verify document exists
            existing_doc = await self.document_repo.find_by_id(document_id)
            if not existing_doc:
                raise ServiceException(f"Document {document_id} not found")
            
            # Add updated timestamp
            updates["updated_at"] = datetime.utcnow()
            
            return await self.document_repo.update(document_id, updates)
            
        except Exception as e:
            self._log_error("update_document", e)
            return None
    
    async def delete_document(self, document_id: int) -> bool:
        """Delete a document"""
        try:
            self._log_operation("delete_document", f"id={document_id}")
            
            # Get document info before deletion
            document = await self.document_repo.find_by_id(document_id)
            if not document:
                return False
            
            # Delete from repository
            success = await self.document_repo.delete(document_id)
            
            if success:
                # TODO: Delete from storage service
                self._delete_from_storage(document.url)
            
            return success
            
        except Exception as e:
            self._log_error("delete_document", e)
            return False
    
    async def search_documents(self, search_term: str) -> List[Document]:
        """Search documents by name"""
        try:
            self._log_operation("search_documents", search_term)
            return await self.document_repo.search_by_name(search_term)
            
        except Exception as e:
            self._log_error("search_documents", e)
            return []
    
    async def get_user_documents(self, user_id: str) -> List[Document]:
        """Get all documents uploaded by a user"""
        try:
            self._log_operation("get_user_documents", f"user_id={user_id}")
            return await self.document_repo.find_by_user_id(user_id)
            
        except Exception as e:
            self._log_error("get_user_documents", e)
            return []
    
    async def process_document(self, document_id: int) -> bool:
        """Process a document (OCR, embeddings, etc.)"""
        try:
            self._log_operation("process_document", f"id={document_id}")
            
            # Update status to processing
            await self.document_repo.update_processing_status(document_id, "processing")
            
            # TODO: Implement actual processing
            # - Download document
            # - Extract text (OCR if needed)
            # - Generate embeddings
            # - Store in vector database
            
            # Update status to completed
            await self.document_repo.update_processing_status(document_id, "completed")
            
            return True
            
        except Exception as e:
            self._log_error("process_document", e)
            # Update status to failed
            await self.document_repo.update_processing_status(document_id, "failed")
            return False
    
    def _trigger_document_processing(self, document: Document):
        """Trigger async document processing"""
        # TODO: Send to background task queue
        self.logger.info(f"Document processing triggered for: {document.name}")
    
    def _delete_from_storage(self, url: str):
        """Delete document from storage service"""
        # TODO: Implement storage deletion
        self.logger.info(f"Storage deletion triggered for: {url}")
