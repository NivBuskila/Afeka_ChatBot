# app/repositories/document_repository.py
"""Document repository implementation"""

from typing import Optional, List
from .base import BaseRepository
from app.domain.document import Document

class DocumentRepository(BaseRepository[Document]):
    """Repository for Document entities"""
    
    @property
    def table_name(self) -> str:
        return "documents"
    
    @property
    def model_class(self) -> type[Document]:
        return Document
    
    async def find_by_category(self, category: str) -> List[Document]:
        """Find documents by category"""
        return await self.find_by_field("category", category)
    
    async def find_by_user_id(self, user_id: str) -> List[Document]:
        """Find documents by user ID"""
        return await self.find_by_field("user_id", user_id)
    
    async def find_processed_documents(self) -> List[Document]:
        """Find all processed documents"""
        return await self.find_by_field("processing_status", "completed")
    
    async def find_pending_documents(self) -> List[Document]:
        """Find documents pending processing"""
        return await self.find_by_field("processing_status", "pending")
    
    async def search_by_name(self, search_term: str) -> List[Document]:
        """Search documents by name (contains search term)"""
        if not self._check_connection():
            return []
            
        try:
            response = self.supabase_client.table(self.table_name).select("*").ilike("name", f"%{search_term}%").execute()
            data = self._handle_supabase_response(response, f"search_by_name({search_term})")
            
            if data:
                return [self.model_class(**item) for item in data]
            return []
            
        except Exception as e:
            self.logger.error(f"Error searching documents by name '{search_term}': {e}")
            return []
    
    async def update_processing_status(self, document_id: int, status: str) -> Optional[Document]:
        """Update document processing status"""
        return await self.update(document_id, {"processing_status": status})