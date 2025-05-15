import logging
import re
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends

from ...domain.models import Document
from ...core.interfaces import IDocumentService
from ...api.deps import get_document_service, verify_api_key

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Documents"])

# Input validation pattern
ID_PATTERN = re.compile(r"^\d+$")

@router.get("/api/documents", response_model=List[Dict[str, Any]])
async def get_documents(
    document_service: IDocumentService = Depends(get_document_service)
):
    """
    Retrieve all available documents.
    
    Returns a list of documents with their metadata.
    """
    return await document_service.get_all_documents()

@router.get("/api/documents/{document_id}", response_model=Dict[str, Any])
async def get_document(
    document_id: str, 
    document_service: IDocumentService = Depends(get_document_service)
):
    """
    Retrieve a specific document by ID.
    
    Args:
        document_id: The ID of the document to retrieve
        
    Returns:
        Document data
    """
    # Validate document_id format
    if not ID_PATTERN.match(document_id):
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    
    try:
        doc_id = int(document_id)
        return await document_service.get_document_by_id(doc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

@router.post("/api/documents", status_code=201, response_model=Dict[str, Any])
async def create_document(
    document: Document,
    document_service: IDocumentService = Depends(get_document_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new document.
    
    Requires API key authentication.
    """
    # API key is already verified by the dependency
    return await document_service.create_document(document)