from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import os
import tempfile
import logging
from pathlib import Path

from services.document_processor import DocumentProcessor
from app.core.auth import get_current_user
from app.core.database import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vector", tags=["Vector Management"])

# Initialize document processor
doc_processor = DocumentProcessor()

@router.post("/upload-document")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    העלאת מסמך חדש ועיבודו לוקטורים
    """
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.txt', '.docx', '.doc'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Create document record in database
        supabase = get_supabase_client()
        document_data = {
            "name": file.filename,
            "url": f"temp://{temp_file_path}",
            "type": file.content_type or "application/octet-stream",
            "size": len(content),
            "processing_status": "pending"
        }
        
        result = supabase.table("documents").insert(document_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create document record")
        
        document_id = result.data[0]["id"]
        
        # Process document in background
        background_tasks.add_task(
            process_document_background,
            document_id,
            temp_file_path
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "Document uploaded successfully and processing started",
                "document_id": document_id,
                "filename": file.filename,
                "status": "processing"
            }
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_document_background(document_id: int, file_path: str):
    """עיבוד מסמך ברקע"""
    try:
        result = await doc_processor.process_document(document_id, file_path)
        logger.info(f"Background processing completed for document {document_id}: {result}")
    except Exception as e:
        logger.error(f"Background processing failed for document {document_id}: {str(e)}")
    finally:
        # Clean up temporary file
        try:
            os.unlink(file_path)
        except:
            pass

@router.get("/document/{document_id}/status")
async def get_document_status(
    document_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    קבלת סטטוס עיבוד מסמך
    """
    try:
        supabase = get_supabase_client()
        result = supabase.rpc("get_document_processing_status", {
            "document_id": document_id
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return result.data[0]
        
    except Exception as e:
        logger.error(f"Error getting document status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/document/{document_id}")
async def delete_document_with_embeddings(
    document_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    מחיקת מסמך כולל כל ה-embeddings שלו
    """
    try:
        supabase = get_supabase_client()
        
        # Check if document exists first
        check_result = supabase.table("documents").select("id").eq("id", document_id).execute()
        if not check_result.data or len(check_result.data) == 0:
            # Document doesn't exist, return success anyway
            return {
                "message": "Document not found or already deleted",
                "document_id": document_id
            }
            
        # Delete all document chunks first
        supabase.table("document_chunks").delete().eq("document_id", document_id).execute()
        
        # Delete the document
        supabase.table("documents").delete().eq("id", document_id).execute()
        
        return {
            "message": "Document and all embeddings deleted successfully",
            "document_id": document_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def semantic_search(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    חיפוש סמנטי במסמכים
    """
    try:
        query = request.get("query", "")
        limit = request.get("limit", 10)
        threshold = request.get("threshold", 0.78)
        
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = await doc_processor.search_documents(query, limit, threshold)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error in semantic search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/hybrid")
async def hybrid_search(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    חיפוש היברידי (סמנטי + מילות מפתח)
    """
    try:
        query = request.get("query", "")
        limit = request.get("limit", 10)
        threshold = request.get("threshold", 0.78)
        
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = await doc_processor.hybrid_search(query, limit, threshold)
        
        return {
            "query": query,
            "search_type": "hybrid",
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error in hybrid search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents_with_status(
    current_user: dict = Depends(get_current_user)
):
    """
    רשימת כל המסמכים עם סטטוס העיבוד
    """
    try:
        supabase = get_supabase_client()
        
        # Get documents with chunk counts
        result = supabase.table("documents").select(
            "id, name, type, size, processing_status, embedding_model, created_at, updated_at"
        ).order("created_at", desc=True).execute()
        
        documents = result.data if result.data else []
        
        # Get chunk counts for each document
        for doc in documents:
            chunk_result = supabase.table("document_chunks").select(
                "id", count="exact"
            ).eq("document_id", doc["id"]).execute()
            
            doc["chunk_count"] = chunk_result.count if chunk_result.count else 0
        
        return {
            "documents": documents,
            "total": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/document/{document_id}/reprocess")
async def reprocess_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    עיבוד מחדש של מסמך קיים
    """
    try:
        supabase = get_supabase_client()
        
        # Get document info
        result = supabase.table("documents").select("*").eq("id", document_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = result.data[0]
        
        # Delete existing embeddings
        await doc_processor.delete_document_embeddings(document_id)
        
        # Check if we have the original file
        if document["url"].startswith("temp://"):
            raise HTTPException(
                status_code=400, 
                detail="Original file not available for reprocessing"
            )
        
        # For now, we'll need the user to re-upload
        # In a production system, you'd store files permanently
        return {
            "message": "Embeddings cleared. Please re-upload the document for reprocessing.",
            "document_id": document_id
        }
        
    except Exception as e:
        logger.error(f"Error reprocessing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_vector_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    סטטיסטיקות על מסד הנתונים הוקטורי
    """
    try:
        supabase = get_supabase_client()
        
        # Count documents by status
        docs_result = supabase.table("documents").select("processing_status", count="exact").execute()
        
        # Count total chunks
        chunks_result = supabase.table("document_chunks").select("id", count="exact").execute()
        
        # Get processing status breakdown
        status_counts = {}
        if docs_result.data:
            for doc in docs_result.data:
                status = doc.get("processing_status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_documents": docs_result.count if docs_result.count else 0,
            "total_chunks": chunks_result.count if chunks_result.count else 0,
            "status_breakdown": status_counts,
            "embedding_model": "gemini-embedding-001"
        }
        
    except Exception as e:
        logger.error(f"Error getting vector stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 