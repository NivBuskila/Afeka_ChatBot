# src/backend/app/repositories/rag_document_repository.py
"""RAG Document repository implementation"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
import logging

from .base import BaseRepository
from app.domain.rag import Document, ProcessingStatus
from app.core.rag_exceptions import DocumentProcessingException

logger = logging.getLogger(__name__)


class RAGDocumentRepository(BaseRepository[Document]):
    """Repository for RAG Document entities"""
    
    @property
    def table_name(self) -> str:
        return "rag_documents"
    
    @property
    def model_class(self) -> type[Document]:
        return Document
    
    async def find_by_title(self, title: str) -> Optional[Document]:
        """Find document by title"""
        try:
            documents = await self.find_by_field("title", title)
            return documents[0] if documents else None
        except Exception as e:
            self.logger.error(f"Error finding document by title {title}: {e}")
            raise DocumentProcessingException(f"Failed to find document by title: {str(e)}")
    
    async def find_by_status(self, status: ProcessingStatus) -> List[Document]:
        """Find documents by processing status"""
        try:
            return await self.find_by_field("processing_status", status.value)
        except Exception as e:
            self.logger.error(f"Error finding documents by status {status}: {e}")
            raise DocumentProcessingException(f"Failed to find documents by status: {str(e)}")
    
    async def find_pending_documents(self) -> List[Document]:
        """Find all pending documents for processing"""
        return await self.find_by_status(ProcessingStatus.PENDING)
    
    async def find_completed_documents(self) -> List[Document]:
        """Find all completed documents"""
        return await self.find_by_status(ProcessingStatus.COMPLETED)
    
    async def find_failed_documents(self) -> List[Document]:
        """Find all failed documents"""
        return await self.find_by_status(ProcessingStatus.FAILED)
    
    async def update_processing_status(self, document_id: UUID, status: ProcessingStatus, error_message: Optional[str] = None) -> Optional[Document]:
        """Update document processing status"""
        try:
            update_data = {
                "processing_status": status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if error_message:
                if not update_data.get("metadata"):
                    update_data["metadata"] = {}
                update_data["metadata"]["error_message"] = error_message
            
            return await self.update(document_id, update_data)
            
        except Exception as e:
            self.logger.error(f"Error updating document status {document_id}: {e}")
            raise DocumentProcessingException(
                f"Failed to update document status: {str(e)}",
                document_id=str(document_id),
                processing_stage="status_update"
            )
    
    async def find_by_file_path(self, file_path: str) -> Optional[Document]:
        """Find document by file path"""
        try:
            documents = await self.find_by_field("file_path", file_path)
            return documents[0] if documents else None
        except Exception as e:
            self.logger.error(f"Error finding document by file path {file_path}: {e}")
            raise DocumentProcessingException(f"Failed to find document by file path: {str(e)}")
    
    async def get_processing_statistics(self) -> Dict[str, int]:
        """Get document processing statistics"""
        try:
            stats = {}
            for status in ProcessingStatus:
                count = len(await self.find_by_status(status))
                stats[status.value] = count
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting processing statistics: {e}")
            raise DocumentProcessingException(f"Failed to get processing statistics: {str(e)}")
    
    async def find_recent_documents(self, limit: int = 10) -> List[Document]:
        """Find most recently created documents"""
        try:
            # For now, use find_all with limit - in a real implementation,
            # this would use proper ordering by created_at
            all_docs = await self.find_all(limit=limit)
            
            # Sort by created_at (most recent first)
            sorted_docs = sorted(
                all_docs, 
                key=lambda doc: doc.created_at if doc.created_at else datetime.min,
                reverse=True
            )
            
            return sorted_docs[:limit]
            
        except Exception as e:
            self.logger.error(f"Error finding recent documents: {e}")
            raise DocumentProcessingException(f"Failed to find recent documents: {str(e)}")
    
    async def search_by_content(self, search_term: str, limit: int = 10) -> List[Document]:
        """Search documents by content (basic text search)"""
        try:
            # Get all completed documents
            completed_docs = await self.find_completed_documents()
            
            # Filter by search term in title or content
            search_term_lower = search_term.lower()
            matching_docs = []
            
            for doc in completed_docs:
                if (search_term_lower in doc.title.lower() or 
                    search_term_lower in doc.content.lower()):
                    matching_docs.append(doc)
                
                if len(matching_docs) >= limit:
                    break
            
            return matching_docs
            
        except Exception as e:
            self.logger.error(f"Error searching documents by content: {e}")
            raise DocumentProcessingException(f"Failed to search documents: {str(e)}")
    
    def _entity_to_dict(self, entity: Document) -> Dict[str, Any]:
        """Convert RAG Document entity to dictionary for database storage"""
        data = super()._entity_to_dict(entity)
        
        # Handle enum serialization
        if 'processing_status' in data and hasattr(data['processing_status'], 'value'):
            data['processing_status'] = data['processing_status'].value
        
        # Handle datetime serialization
        if 'created_at' in data and isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
        
        if 'updated_at' in data and isinstance(data['updated_at'], datetime):
            data['updated_at'] = data['updated_at'].isoformat()
        
        return data
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> Document:
        """Convert dictionary from database to RAG Document entity"""
        # Handle enum deserialization
        if 'processing_status' in data and isinstance(data['processing_status'], str):
            try:
                data['processing_status'] = ProcessingStatus(data['processing_status'])
            except ValueError:
                data['processing_status'] = ProcessingStatus.PENDING
        
        # Handle datetime deserialization
        if 'created_at' in data and isinstance(data['created_at'], str):
            try:
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            except ValueError:
                data['created_at'] = datetime.utcnow()
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            try:
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            except ValueError:
                data['updated_at'] = datetime.utcnow()
        
        return super()._dict_to_entity(data)