import logging
import re
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends
# from supabase import Client # No longer needed directly in router

# Use absolute imports
from backend.models.schemas import Document
from backend.core.dependencies import verify_api_key
# Remove direct import of get_supabase_client from here
# from ...core.dependencies import get_supabase_client 
# from ...core import config # Config is used in service layer

# Import the service and its dependency function
from backend.services.document_service import DocumentService, get_document_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Input validation pattern (can stay here or move to utils)
ID_PATTERN = re.compile(r"^\d+$")

@router.get("/api/documents", tags=["Documents"], response_model=List[Dict[str, Any]])
async def get_documents(doc_service: DocumentService = Depends(get_document_service)):
    """
    Retrieve available documents using the DocumentService.
    """
    # Logic is now in the service
    return await doc_service.get_all_documents()

@router.get("/api/documents/{document_id}", tags=["Documents"], response_model=Dict[str, Any])
async def get_document(document_id: str, doc_service: DocumentService = Depends(get_document_service)):
    """
    Retrieve a specific document by ID using the DocumentService.
    """
    if not ID_PATTERN.match(document_id):
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    try:
        doc_id = int(document_id)
        # Logic is now in the service
        return await doc_service.get_document_by_id(doc_id)
    except ValueError:
        # Handle potential int conversion error locally or in service
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    # Specific HTTP exceptions from service (like 404) will pass through
    # General exceptions are handled by the service or global handler

@router.post("/api/documents", status_code=201, tags=["Documents"], response_model=Dict[str, Any])
async def create_document(document: Document,
                          doc_service: DocumentService = Depends(get_document_service),
                          api_key: str = Depends(verify_api_key)):
    """
    Create a new document using the DocumentService.
    Requires API key authentication.
    """
    # API key is verified by dependency
    # Logic, including size validation, is now in the service
    return await doc_service.create_new_document(document) 