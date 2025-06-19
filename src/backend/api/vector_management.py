from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import os
import tempfile
import logging
from pathlib import Path

from src.ai.services.document_processor import DocumentProcessor
from src.backend.app.core.auth import get_current_user
from src.backend.app.core.database import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vector", tags=["Vector Management"])

# Lazy initialization of document processor
doc_processor = None

def get_doc_processor():
    """Get document processor instance with lazy initialization"""
    global doc_processor
    if doc_processor is None:
        doc_processor = DocumentProcessor()
    return doc_processor

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
            process_document_wrapper,
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

def process_document_wrapper(document_id: int, file_path: str):
    """Wrapper לקריאה סינכרונית לפונקציה אסינכרונית"""
    import asyncio
    try:
        # Create new event loop for background task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process_document_background(document_id, file_path))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in process_document_wrapper for document {document_id}: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

async def process_document_background(document_id: int, file_path: str):
    """עיבוד מסמך ברקע"""
    try:
        logger.info(f"Starting background processing for document {document_id} at path {file_path}")
        result = await get_doc_processor().process_document(document_id, file_path)
        logger.info(f"Background processing completed for document {document_id}: {result}")
        
        # Update document status to completed if successful
        if result.get("success", False):
            logger.info(f"Document {document_id} processed successfully")
        else:
            logger.error(f"Document {document_id} processing failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Background processing failed for document {document_id}: {str(e)}", exc_info=True)
        
        # Update document status to failed
        try:
            from src.backend.app.core.database import get_supabase_client
            supabase = get_supabase_client()
            if supabase:
                supabase.table("documents").update({
                    "processing_status": "failed"
                }).eq("id", document_id).execute()
                logger.info(f"Updated document {document_id} status to failed")
        except Exception as status_error:
            logger.error(f"Failed to update document {document_id} status to failed: {status_error}")
    finally:
        # Clean up temporary file
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as cleanup_error:
            logger.error(f"Failed to clean up temporary file {file_path}: {cleanup_error}")

@router.get("/document/{document_id}/status")
async def get_document_status(document_id: int):
    """
    קבלת סטטוס עיבוד מסמך
    """
    try:
        logger.info(f"GET /api/vector/document/{document_id}/status")
        
        # Get real data from database
        supabase = get_supabase_client()
        if not supabase:
            logger.error("Failed to get Supabase client")
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Get document info
        doc_result = supabase.table("documents").select("*").eq("id", document_id).execute()
        if not doc_result.data:
            logger.warning(f"Document {document_id} not found")
            return JSONResponse(content={
                "document_id": document_id,
                "status": "not_found",
                "progress_percentage": 0,
                "chunk_count": 0,
                "error": "Document not found"
            })
        
        document = doc_result.data[0]
        processing_status = document.get("processing_status", "unknown")
        
        # Get real chunk count
        chunks_result = supabase.table("document_chunks").select("id", count="exact").eq("document_id", document_id).execute()
        chunk_count = chunks_result.count if chunks_result.count is not None else 0
        
        # Get embeddings count (try different approaches based on schema)
        embeddings_count = 0
        try:
            # First try with document_id field
            embeddings_result = supabase.table("embeddings").select("id", count="exact").eq("document_id", document_id).execute()
            embeddings_count = embeddings_result.count if embeddings_result.count is not None else 0
        except Exception as emb_error:
            try:
                # If that fails, try to count through document_chunks
                chunk_embeddings = supabase.table("document_chunks").select("embedding_id", count="exact").eq("document_id", document_id).neq("embedding_id", "null").execute()
                embeddings_count = chunk_embeddings.count if chunk_embeddings.count is not None else 0
            except Exception:
                # If all fails, use chunk count as embeddings count
                embeddings_count = chunk_count
        
        # Determine status and progress
        if processing_status == "pending":
            status = "pending"
            progress = 0
        elif processing_status == "processing":
            status = "processing"
            progress = 50  # Assume halfway through
        elif processing_status == "completed":
            status = "completed"
            progress = 100
        elif processing_status == "failed":
            status = "failed"
            progress = 0
        else:
            # Infer status from chunk count
            if chunk_count > 0:
                status = "completed"
                progress = 100
            else:
                status = "pending"
                progress = 0
        
        logger.info(f"Document {document_id}: status={status}, chunks={chunk_count}, embeddings={embeddings_count}")
        
        status_response = {
            "document_id": document_id,
            "status": status,
            "progress_percentage": progress,
            "chunk_count": chunk_count,
            "total_chunks": chunk_count,
            "embeddings_created": embeddings_count,
            "processing_started_at": document.get("created_at", "2024-01-01T00:00:00Z"),
            "processing_completed_at": document.get("updated_at", "2024-01-01T00:00:00Z") if status == "completed" else None,
            "processing_status": processing_status
        }
        
        return JSONResponse(content=status_response)
        
    except Exception as e:
        logger.error(f"Error getting document status for document {document_id}: {str(e)}", exc_info=True)
        # Return realistic error status
        return JSONResponse(content={
            "document_id": document_id,
            "status": "error",
            "progress_percentage": 0,
            "chunk_count": 0,
            "total_chunks": 0,
            "embeddings_created": 0,
            "error": f"Failed to get status: {str(e)}",
            "processing_status": "error"
        })

@router.delete("/document/{document_id}")
async def delete_document_with_embeddings(
    document_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    מחיקת מסמך כולל כל ה-embeddings שלו
    """
    try:
        logger.info(f"Starting document deletion process for document_id: {document_id}")
        supabase = get_supabase_client()
        
        if not supabase:
            logger.error("Failed to get Supabase client")
            raise HTTPException(status_code=500, detail="Database connection error")
        
        # Check if document exists first
        logger.info(f"Checking if document {document_id} exists")
        check_result = supabase.table("documents").select("id").eq("id", document_id).execute()
        logger.debug(f"Document check result: {check_result}")
        
        if not check_result.data or len(check_result.data) == 0:
            # Document doesn't exist, return success anyway
            logger.info(f"Document {document_id} not found or already deleted")
            return {
                "message": "Document not found or already deleted",
                "document_id": document_id
            }
            
        # Batch delete document chunks
        logger.info(f"Starting batch deletion of chunks for document_id: {document_id}")
        batch_size = 500  # Define a reasonable batch size
        total_chunks_deleted = 0
        
        try:
            while True:
                # Fetch a batch of chunk IDs
                logger.debug(f"Fetching batch of chunk IDs for document_id: {document_id}")
                chunk_ids_response = supabase.table("document_chunks").select("id").eq("document_id", document_id).limit(batch_size).execute()
                logger.debug(f"Chunk IDs response: {chunk_ids_response}")
                
                if not chunk_ids_response.data:
                    logger.info(f"No more chunks found for document_id: {document_id}")
                    break  # No more chunks to delete
                    
                chunk_ids_to_delete = [chunk['id'] for chunk in chunk_ids_response.data]
                
                if not chunk_ids_to_delete:
                    logger.info(f"No chunk IDs to delete in this batch for document_id: {document_id}")
                    break

                logger.info(f"Deleting batch of {len(chunk_ids_to_delete)} chunks for document_id: {document_id}")
                try:
                    delete_response = supabase.table("document_chunks").delete().in_("id", chunk_ids_to_delete).execute()
                    logger.debug(f"Delete response: {delete_response}")
                    
                    # Check for error in response - updated to handle different response formats
                    error_detected = False
                    if hasattr(delete_response, 'error') and delete_response.error:
                        error_detected = True
                        error_message = delete_response.error
                        logger.error(f"Error attribute found in delete_response: {error_message}")
                    elif isinstance(delete_response, dict) and delete_response.get('error'):
                        error_detected = True
                        error_message = delete_response.get('error')
                        logger.error(f"Error key found in delete_response dict: {error_message}")
                    
                    if error_detected:
                        logger.error(f"Error deleting a batch of chunks for document_id {document_id}: {error_message}")
                        raise HTTPException(status_code=500, detail=f"Failed to delete document chunks: {error_message}")
                    
                    # Count deleted chunks
                    if hasattr(delete_response, 'data') and delete_response.data:
                        batch_deleted = len(delete_response.data)
                        total_chunks_deleted += batch_deleted
                        logger.info(f"Successfully deleted {batch_deleted} chunks in this batch")
                    
                except Exception as batch_error:
                    logger.error(f"Exception during batch deletion: {str(batch_error)}", exc_info=True)
                    raise HTTPException(status_code=500, detail=f"Error during batch deletion: {str(batch_error)}")

                # If fewer than batch_size chunks were processed, it means we're done or at the last batch.
                # The next iteration's select will confirm if more exist.
                if len(chunk_ids_to_delete) < batch_size:
                    logger.info(f"Processed the last batch of chunks for document_id: {document_id}")
                    break
        except Exception as chunks_error:
            logger.error(f"Error in chunk deletion loop: {str(chunks_error)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error in chunk deletion process: {str(chunks_error)}")
        
        logger.info(f"Finished batch deletion of chunks for document_id: {document_id}. Total chunks deleted: {total_chunks_deleted}")
        
        # Delete the document
        logger.info(f"Deleting document record for document_id: {document_id}")
        try:
            doc_delete_response = supabase.table("documents").delete().eq("id", document_id).execute()
            logger.debug(f"Document delete response: {doc_delete_response}")

            # Check for error in response - updated to handle different response formats
            error_detected = False
            if hasattr(doc_delete_response, 'error') and doc_delete_response.error:
                error_detected = True
                error_message = doc_delete_response.error
                logger.error(f"Error attribute found in doc_delete_response: {error_message}")
            elif isinstance(doc_delete_response, dict) and doc_delete_response.get('error'):
                error_detected = True
                error_message = doc_delete_response.get('error')
                logger.error(f"Error key found in doc_delete_response dict: {error_message}")
            
            if error_detected:
                logger.error(f"Error deleting document record for document_id {document_id}: {error_message}")
                # Even if document deletion fails, chunks might have been deleted.
                # Consider how to handle this scenario, e.g., retry or log for manual intervention.
                raise HTTPException(status_code=500, detail=f"Failed to delete document record: {error_message}")
            
            # Check if document was actually deleted
            if hasattr(doc_delete_response, 'data') and doc_delete_response.data:
                deleted_count = len(doc_delete_response.data)
                logger.info(f"Successfully deleted document record for document_id: {document_id}. Deleted count: {deleted_count}")
            else:
                logger.warning(f"Document deletion response has no data attribute or empty data for document_id: {document_id}")
                
        except Exception as doc_delete_error:
            logger.error(f"Exception during document record deletion: {str(doc_delete_error)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error deleting document record: {str(doc_delete_error)}")
        
        logger.info(f"Document deletion process completed successfully for document_id: {document_id}")
        return {
            "message": "Document and all associated chunks deleted successfully",
            "document_id": document_id,
            "chunks_deleted": total_chunks_deleted
        }
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        logger.error(f"HTTP Exception in delete_document_with_embeddings: {str(he)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_document_with_embeddings: {str(e)}", exc_info=True)
        # Try to get more details about the exception
        import traceback
        logger.error(f"Exception traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

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
        
        results = await get_doc_processor().search_documents(query, limit, threshold)
        
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
        
        results = await get_doc_processor().hybrid_search(query, limit, threshold)
        
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
        await get_doc_processor().delete_document_embeddings(document_id)
        
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