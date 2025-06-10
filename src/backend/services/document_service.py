# src/backend/services/document_service.py
import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, Depends
from supabase import Client

# Use absolute imports
from backend.models.schemas import Document
from backend.core import config
from backend.core.dependencies import get_supabase_client

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, supabase: Client):
        self.db = supabase

    async def get_all_documents(self) -> List[Dict[str, Any]]:
        try:
            response = self.db.table('documents').select('*').execute()
            # Check if response has data and data is a list (Supabase v2)
            if hasattr(response, 'data') and isinstance(response.data, list):
                logger.info(f"Retrieved {len(response.data)} documents")
                return response.data
            else:
                logger.warning(f"No documents found or unexpected response format. Response: {getattr(response, 'error', response)}")
                return []
        except Exception as e:
            logger.exception(f"DB error getting all documents: {e}") # Use logger.exception to include traceback
            raise HTTPException(status_code=500, detail="Failed to retrieve documents")

    async def get_document_by_id(self, doc_id: int) -> Dict[str, Any]:
        try:
            response = self.db.table('documents').select('*').eq('id', doc_id).single().execute()
             # Check if response has data and data is a dict (Supabase v2 single)
            if hasattr(response, 'data') and isinstance(response.data, dict):
                logger.info(f"Retrieved document ID {doc_id}")
                return response.data
            else:
                logger.warning(f"Document ID {doc_id} not found or unexpected response. Response: {getattr(response, 'error', response)}")
                raise HTTPException(status_code=404, detail="Document not found")
        except HTTPException: # Re-raise specific HTTP exceptions
            raise
        except Exception as e:
            logger.exception(f"DB error getting document {doc_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve document")

    async def create_new_document(self, document_data: Document) -> Dict[str, Any]:
        if len(document_data.content) > config.MAX_DOCUMENT_SIZE_BYTES:
            raise HTTPException(status_code=400, detail=f"Document content too large (max {config.MAX_DOCUMENT_SIZE_KB}KB)")
        
        try:
            doc_dict = document_data.model_dump()
            response = self.db.table('documents').insert(doc_dict).execute()
            # Check if response has data and it's a list (Supabase v2 insert)
            if hasattr(response, 'data') and isinstance(response.data, list) and len(response.data) > 0:
                new_id = response.data[0]['id']
                logger.info(f"Created document '{document_data.title}' with ID {new_id}")
                return {"success": True, "id": new_id, "message": "Document created successfully"}
            else:
                logger.error(f"DB insert failed. Error: {getattr(response, 'error', 'Unknown error')}, Response Data: {getattr(response, 'data', 'N/A')}")
                raise HTTPException(status_code=500, detail="Failed to create document")
        except HTTPException: # Re-raise specific HTTP exceptions
            raise
        except Exception as e:
            logger.exception(f"Error creating document in service: {e}")
            raise HTTPException(status_code=500, detail="Failed to create document")

# Dependency function to get the service instance
def get_document_service(supabase: Client = Depends(get_supabase_client)) -> DocumentService:
     return DocumentService(supabase) 