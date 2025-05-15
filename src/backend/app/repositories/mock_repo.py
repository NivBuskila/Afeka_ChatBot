import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .interfaces import IDocumentRepository
from ..domain.models import Document
from ..core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

class MockDocumentRepository(IDocumentRepository):
    """Mock implementation of document repository for testing and fallbacks."""
    
    def __init__(self):
        """Initialize with mock data."""
        self.documents = {
            1: {
                "id": 1,
                "title": "Academic Regulations",
                "content": "This document contains the academic regulations for Afeka College",
                "category": "Academic",
                "created_at": "2024-01-01T00:00:00"
            },
            2: {
                "id": 2,
                "title": "Student Handbook",
                "content": "A comprehensive guide for Afeka College students",
                "category": "Student",
                "created_at": "2024-01-15T00:00:00"
            },
            3: {
                "id": 3, 
                "title": "Course Catalog",
                "content": "List of all courses offered at Afeka College",
                "category": "Academic",
                "created_at": "2024-02-01T00:00:00"
            }
        }
        self.next_id = max(self.documents.keys()) + 1 if self.documents else 1
    
    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all documents from mock storage."""
        logger.info("Retrieving all documents (mock)")
        return list(self.documents.values())
    
    async def get_by_id(self, doc_id: int) -> Dict[str, Any]:
        """Get document by ID from mock storage."""
        logger.info(f"Retrieving document {doc_id} (mock)")
        
        if doc_id in self.documents:
            return self.documents[doc_id]
        
        # If not found, return a new mock document or raise exception
        if doc_id > 0 and doc_id < 100:  # Arbitrary limit for mock data
            return {
                "id": doc_id,
                "title": f"Document {doc_id}",
                "content": f"This is a mock document with ID {doc_id}",
                "category": "General",
                "created_at": "2024-01-01T00:00:00"
            }
        else:
            raise RepositoryError(f"Document {doc_id} not found", status_code=404)
    
    async def create(self, document: Document) -> Dict[str, Any]:
        """Create document in mock storage."""
        logger.info(f"Creating document '{document.title}' (mock)")
        
        new_id = self.next_id
        self.next_id += 1
        
        new_doc = {
            "id": new_id,
            "title": document.title,
            "content": document.content,
            "category": document.category,
            "tags": document.tags,
            "created_at": datetime.now().isoformat()
        }
        
        self.documents[new_id] = new_doc
        return new_doc