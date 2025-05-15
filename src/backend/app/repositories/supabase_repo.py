import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from supabase import Client

from .interfaces import IDocumentRepository
from ..domain.models import Document
from ..core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

class SupabaseDocumentRepository(IDocumentRepository):
    """Supabase implementation of document repository."""
    
    def __init__(self, client: Client):
        """Initialize with Supabase client."""
        self.client = client
        self.table_name = "documents"
    
    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all documents from Supabase."""
        try:
            response = self.client.table(self.table_name).select('*').order('created_at', desc=True).execute()
            
            if hasattr(response, 'data') and isinstance(response.data, list):
                logger.info(f"Retrieved {len(response.data)} documents")
                return response.data
            else:
                logger.warning("No data or unexpected response format from Supabase")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise RepositoryError(f"Failed to retrieve documents: {e}")
    
    async def get_by_id(self, doc_id: int) -> Dict[str, Any]:
        """Get a document by ID from Supabase."""
        try:
            response = self.client.table(self.table_name).select('*').eq('id', doc_id).single().execute()
            
            if hasattr(response, 'data') and response.data:
                logger.info(f"Retrieved document {doc_id}")
                return response.data
            else:
                logger.warning(f"Document with ID {doc_id} not found")
                raise RepositoryError(f"Document {doc_id} not found", status_code=404)
                
        except Exception as e:
            if isinstance(e, RepositoryError):
                raise e
            logger.error(f"Error retrieving document {doc_id}: {e}")
            raise RepositoryError(f"Failed to retrieve document: {e}")
    
    async def create(self, document: Document) -> Dict[str, Any]:
        """Create a new document in Supabase."""
        try:
            # Convert document to dict and add timestamp
            doc_dict = document.model_dump(exclude_unset=True)
            doc_dict['created_at'] = datetime.now().isoformat()
            
            # Handle JSON serialization for tags if present
            if 'tags' in doc_dict and isinstance(doc_dict['tags'], list):
                # Some Supabase setups require JSON to be stored as strings
                doc_dict['tags'] = json.dumps(doc_dict['tags'])
            
            response = self.client.table(self.table_name).insert(doc_dict).execute()
            
            if hasattr(response, 'data') and response.data and len(response.data) > 0:
                new_id = response.data[0].get('id')
                logger.info(f"Created document '{document.title}' with ID {new_id}")
                return response.data[0]
            else:
                logger.error("Failed to create document: No data returned")
                raise RepositoryError("Failed to create document: No data returned")
                
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise RepositoryError(f"Failed to create document: {e}")
            
    async def update(self, doc_id: int, document: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing document in Supabase."""
        try:
            # Ensure the document exists first
            await self.get_by_id(doc_id)
            
            # Add updated timestamp
            update_data = document.copy()
            update_data['updated_at'] = datetime.now().isoformat()
            
            # Handle JSON serialization for tags if present
            if 'tags' in update_data and isinstance(update_data['tags'], list):
                update_data['tags'] = json.dumps(update_data['tags'])
            
            response = self.client.table(self.table_name).update(update_data).eq('id', doc_id).execute()
            
            if hasattr(response, 'data') and response.data and len(response.data) > 0:
                logger.info(f"Updated document with ID {doc_id}")
                return response.data[0]
            else:
                logger.error(f"Failed to update document {doc_id}: No data returned")
                raise RepositoryError(f"Failed to update document {doc_id}")
                
        except Exception as e:
            if isinstance(e, RepositoryError):
                raise e
            logger.error(f"Error updating document {doc_id}: {e}")
            raise RepositoryError(f"Failed to update document: {e}")
            
    async def delete(self, doc_id: int) -> bool:
        """Delete a document from Supabase."""
        try:
            # Ensure the document exists first
            await self.get_by_id(doc_id)
            
            response = self.client.table(self.table_name).delete().eq('id', doc_id).execute()
            
            if hasattr(response, 'data'):
                logger.info(f"Deleted document with ID {doc_id}")
                return True
            else:
                logger.error(f"Failed to delete document {doc_id}")
                raise RepositoryError(f"Failed to delete document {doc_id}")
                
        except Exception as e:
            if isinstance(e, RepositoryError):
                raise e
            logger.error(f"Error deleting document {doc_id}: {e}")
            raise RepositoryError(f"Failed to delete document: {e}")
            
    async def search(self, search_term: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for documents by title or content."""
        try:
            # Start with base query
            query = self.client.table(self.table_name).select('*')
            
            # Apply title search (case insensitive)
            title_query = f"%{search_term}%"
            query = query.ilike('title', title_query)
            
            # Filter by category if provided
            if category:
                query = query.eq('category', category)
                
            # Execute query
            response = query.execute()
            
            if hasattr(response, 'data') and isinstance(response.data, list):
                logger.info(f"Search found {len(response.data)} documents matching '{search_term}'")
                return response.data
            else:
                logger.warning(f"No search results found for '{search_term}'")
                return []
                
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise RepositoryError(f"Failed to search documents: {e}")