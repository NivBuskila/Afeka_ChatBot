# app/api/v1/proxy.py
"""Proxy endpoints for direct Supabase operations and AI service integration"""

from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from datetime import datetime
import json
import uuid
import time
import logging
from app.config import settings
from app.dependencies import get_ai_service, get_chat_service
from app.services.ai_service import AIServiceClient
from app.services.chat_service import ChatService
from app.core.exceptions import ServiceException

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/proxy",
    tags=["proxy"],
    responses={
        503: {"description": "Service Unavailable"},
        500: {"description": "Internal Server Error"}
    }
)

def get_supabase_client():
    """Get Supabase client from app state"""
    from app.repositories.factory import get_repository_factory
    try:
        factory = get_repository_factory()
        return factory.supabase_client
    except:
        return None

# ========================
# AI SERVICE ENDPOINTS
# ========================

@router.post("/ai/chat")
async def ai_chat(
    request: Request,
    ai_service: AIServiceClient = Depends(get_ai_service),
    chat_service: ChatService = Depends(get_chat_service)
) -> JSONResponse:
    """Process chat message with conversation context"""
    try:
        body = await request.json()
        
        user_message = body.get("message", "")
        session_id = body.get("session_id")
        user_id = body.get("user_id")
        use_rag = body.get("use_rag", True)
        
        if not user_message.strip():
            return JSONResponse(
                content={"error": "Message cannot be empty"}, 
                status_code=400
            )
        
        # ✅ FIX: Actually fetch conversation history from database
        conversation_history = []
        if session_id:
            try:
                # Get messages from the session using Supabase directly
                supabase_client = get_supabase_client()
                if supabase_client:
                    result = supabase_client.table("messages")\
                        .select("*")\
                        .eq("conversation_id", session_id)\
                        .order("created_at", desc=False)\
                        .execute()
                    
                    if result.data:
                        # Convert database messages to ChatMessage format
                        for msg_data in result.data:
                            # Handle both request and response messages
                            if msg_data.get("request"):  # User message
                                conversation_history.append(type('ChatMessage', (), {
                                    'content': msg_data["request"],
                                    'role': 'user',
                                    'created_at': msg_data["created_at"]
                                })())
                            
                            if msg_data.get("response"):  # Bot message
                                conversation_history.append(type('ChatMessage', (), {
                                    'content': msg_data["response"],
                                    'role': 'assistant', 
                                    'created_at': msg_data["created_at"]
                                })())
                        
                        logger.info(f"Fetched {len(conversation_history)} messages for session {session_id}")
                
            except Exception as e:
                logger.error(f"Error fetching conversation history: {e}")
                conversation_history = []
        
        # Send to AI service with conversation history
        ai_response = await ai_service.chat_with_rag(
            message=user_message,
            session_id=session_id,
            conversation_history=conversation_history,
            use_rag=use_rag
        )
        
        return JSONResponse(content=ai_response)
        
    except Exception as e:
        logger.error(f"Error in ai_chat: {e}")
        return JSONResponse(
            content={"error": "Failed to process chat message", "details": str(e)},
            status_code=500
        )

@router.post("/ai/search")
async def ai_semantic_search(
    request: Request,
    ai_service: AIServiceClient = Depends(get_ai_service)
) -> JSONResponse:
    """
    Proxy endpoint for AI semantic search
    Maps to AI service /rag/search
    """
    try:
        body = await request.json()
        
        if not body.get("query"):
            return JSONResponse(
                status_code=400,
                content={"error": "Query field is required"}
            )
        
        query = body["query"]
        limit = body.get("limit")  # Let AI service use defaults if not provided
        threshold = body.get("threshold")  # Let AI service use defaults if not provided
        
        logger.info(f"AI semantic search: query_length={len(query)}")
        
        results = await ai_service.semantic_search(
            query=query,
            limit=limit,
            threshold=threshold
        )
        
        return JSONResponse(content={
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except ServiceException as e:
        logger.error(f"AI search service error: {e}")
        return JSONResponse(
            status_code=503,
            content={"error": "Search service temporarily unavailable", "detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Error in AI search: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@router.post("/ai/search/hybrid")
async def ai_hybrid_search(
    request: Request,
    ai_service: AIServiceClient = Depends(get_ai_service)
) -> JSONResponse:
    """
    Proxy endpoint for AI hybrid search
    Maps to AI service /rag/search/hybrid
    """
    try:
        body = await request.json()
        
        if not body.get("query"):
            return JSONResponse(
                status_code=400,
                content={"error": "Query field is required"}
            )
        
        query = body["query"]
        limit = body.get("limit")
        threshold = body.get("threshold")
        
        logger.info(f"AI hybrid search: query_length={len(query)}")
        
        results = await ai_service.hybrid_search(
            query=query,
            limit=limit,
            threshold=threshold
        )
        
        return JSONResponse(content={
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except ServiceException as e:
        logger.error(f"AI hybrid search service error: {e}")
        return JSONResponse(
            status_code=503,
            content={"error": "Hybrid search service temporarily unavailable", "detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Error in AI hybrid search: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@router.post("/ai/search/enhanced")
async def ai_enhanced_search(
    request: Request,
    ai_service: AIServiceClient = Depends(get_ai_service)
) -> JSONResponse:
    """
    Proxy endpoint for AI enhanced search
    Maps to AI service /rag/enhanced_search
    """
    try:
        body = await request.json()
        
        if not body.get("query"):
            return JSONResponse(
                status_code=400,
                content={"error": "Query field is required"}
            )
        
        query = body["query"]
        max_results = body.get("max_results")
        include_context = body.get("include_context", True)
        
        logger.info(f"AI enhanced search: query_length={len(query)}")
        
        result = await ai_service.enhanced_search(
            query=query,
            max_results=max_results,
            include_context=include_context
        )
        
        return JSONResponse(content=result)
        
    except ServiceException as e:
        logger.error(f"AI enhanced search service error: {e}")
        return JSONResponse(
            status_code=503,
            content={"error": "Enhanced search service temporarily unavailable", "detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Error in AI enhanced search: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@router.get("/ai/stats")
async def ai_rag_stats(
    ai_service: AIServiceClient = Depends(get_ai_service)
) -> JSONResponse:
    """
    Proxy endpoint for AI/RAG statistics
    Maps to AI service /rag/stats
    """
    try:
        logger.info("Fetching AI/RAG statistics")
        
        result = await ai_service.get_rag_stats()
        
        return JSONResponse(content=result)
        
    except ServiceException as e:
        logger.error(f"AI stats service error: {e}")
        return JSONResponse(
            status_code=503,
            content={"error": "Stats service temporarily unavailable", "detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Error fetching AI stats: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@router.post("/ai/documents/{document_id}/reprocess")
async def ai_reprocess_document(
    document_id: int,
    ai_service: AIServiceClient = Depends(get_ai_service)
) -> JSONResponse:
    """
    Proxy endpoint for document reprocessing
    Maps to AI service /rag/document/{document_id}/reprocess
    """
    try:
        logger.info(f"Triggering document reprocessing: document_id={document_id}")
        
        result = await ai_service.reprocess_document(document_id)
        
        return JSONResponse(content=result)
        
    except ServiceException as e:
        logger.error(f"AI document reprocess service error: {e}")
        return JSONResponse(
            status_code=503,
            content={"error": "Document reprocessing service temporarily unavailable", "detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Error reprocessing document: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@router.get("/ai/documents/{document_id}/status")
async def ai_document_status(
    document_id: int,
    ai_service: AIServiceClient = Depends(get_ai_service)
) -> JSONResponse:
    """
    Proxy endpoint for document processing status
    Maps to AI service /rag/document/{document_id}
    """
    try:
        logger.info(f"Fetching document status: document_id={document_id}")
        
        result = await ai_service.get_document_status(document_id)
        
        return JSONResponse(content=result)
        
    except ServiceException as e:
        logger.error(f"AI document status service error: {e}")
        return JSONResponse(
            status_code=503,
            content={"error": "Document status service temporarily unavailable", "detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Error fetching document status: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@router.get("/ai/health")
async def ai_health_check(
    ai_service: AIServiceClient = Depends(get_ai_service)
) -> JSONResponse:
    """
    Proxy endpoint for AI service health check
    Maps to AI service /
    """
    try:
        result = await ai_service.health_check()
        
        if result.get("status") == "healthy":
            return JSONResponse(content=result)
        else:
            return JSONResponse(
                status_code=503,
                content=result
            )
        
    except Exception as e:
        logger.error(f"Error checking AI service health: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# ========================
# EXISTING ENDPOINTS (Updated to use AI service where relevant)
# ========================

@router.post("/chat_sessions")
async def create_chat_session(request: Request) -> JSONResponse:
    """
    Create a new chat session
    
    Direct proxy to Supabase for frontend compatibility
    """
    supabase_client = get_supabase_client()
    if not supabase_client:
        # Return mock response when Supabase is unavailable
        body = await request.json()
        session_id = str(uuid.uuid4())
        mock_response = [{
            "id": session_id,
            "user_id": body.get('user_id', 'unknown'),
            "title": body.get('title', 'New Chat'),
            "created_at": body.get('created_at', datetime.now().isoformat()),
            "updated_at": body.get('updated_at', datetime.now().isoformat())
        }]
        logger.info(f"Returning mock session response with ID: {session_id}")
        return JSONResponse(content=mock_response)
    
    try:
        body = await request.json()
        logger.info(f"Creating chat session for user: {body.get('user_id', 'unknown')}")
        
        # Check if table exists and create session
        try:
            result = supabase_client.table("chat_sessions").insert(body).execute()
            
            # Also create conversation record if table exists
            if result.data:
                try:
                    conversation_data = {
                        "conversation_id": result.data[0]["id"],
                        "user_id": body.get("user_id"),
                        "title": body.get("title"),
                        "created_at": body.get("created_at", result.data[0].get("created_at")),
                        "updated_at": body.get("updated_at", result.data[0].get("updated_at")),
                        "is_active": True
                    }
                    supabase_client.table("conversations").insert(conversation_data).execute()
                except Exception as conv_err:
                    logger.warning(f"Couldn't create conversation record: {conv_err}")
            
            return JSONResponse(content=result.data)
            
        except Exception as table_err:
            logger.warning(f"chat_sessions table may not exist: {table_err}")
            # Return mock response
            session_id = str(uuid.uuid4())
            mock_response = [{
                "id": session_id,
                "user_id": body.get('user_id', 'unknown'),
                "title": body.get('title', 'New Chat'),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }]
            return JSONResponse(content=mock_response)
            
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        # Return mock response on error
        session_id = str(uuid.uuid4())
        return JSONResponse(content=[{
            "id": session_id,
            "user_id": "unknown",
            "title": "New Chat",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }])

@router.get("/chat_sessions")
async def get_chat_sessions(user_id: str) -> JSONResponse:
    """Get all chat sessions for a user"""
    supabase_client = get_supabase_client()
    if not supabase_client:
        return JSONResponse(content=[])
    
    try:
        logger.info(f"Fetching chat sessions for user: {user_id}")
        
        # Check if table exists
        try:
            result = supabase_client.table("chat_sessions").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
            return JSONResponse(content=result.data if hasattr(result, 'data') else [])
        except Exception as e:
            logger.warning(f"Error querying chat_sessions: {e}")
            return JSONResponse(content=[])
            
    except Exception as e:
        logger.error(f"Error fetching chat sessions: {e}")
        return JSONResponse(content=[])

@router.get("/chat_sessions/{session_id}")
async def get_chat_session(session_id: str) -> JSONResponse:
    """Get a specific chat session with messages"""
    supabase_client = get_supabase_client()
    if not supabase_client:
        return JSONResponse(content={"id": session_id, "messages": []})
    
    try:
        logger.info(f"Fetching chat session with ID: {session_id}")
        
        # Get session
        try:
            session_result = supabase_client.table("chat_sessions").select("*").eq("id", session_id).single().execute()
            
            if not session_result.data:
                return JSONResponse(content={"id": session_id, "messages": []})
            
            # Get messages
            try:
                messages_result = supabase_client.table("messages").select("*").eq("conversation_id", session_id).order("created_at").execute()
                messages = messages_result.data or []
            except:
                messages = []
            
            result = {
                **session_result.data,
                "messages": messages
            }
            
            return JSONResponse(content=result)
            
        except Exception as e:
            logger.error(f"Error fetching session: {e}")
            return JSONResponse(content={"id": session_id, "messages": []})
            
    except Exception as e:
        logger.error(f"Error getting chat session: {e}")
        return JSONResponse(content={"id": session_id, "messages": []})

@router.patch("/chat_sessions/{session_id}")
async def update_chat_session(session_id: str, request: Request) -> JSONResponse:
    """Update a chat session"""
    supabase_client = get_supabase_client()
    if not supabase_client:
        return JSONResponse(content={"success": True, "data": []})
    
    try:
        body = await request.json()
        
        # Ensure updated timestamp
        if 'updated_at' not in body:
            body['updated_at'] = datetime.now().isoformat()
        
        result = supabase_client.table("chat_sessions").update(body).eq("id", session_id).execute()
        
        # Update conversation if exists
        try:
            conversation_update = {
                'updated_at': body.get('updated_at'),
                'last_message_at': body.get('updated_at')
            }
            if 'title' in body:
                conversation_update['title'] = body['title']
            
            supabase_client.table("conversations").update(conversation_update).eq("conversation_id", session_id).execute()
        except Exception as conv_err:
            logger.warning(f"Error updating conversation: {conv_err}")
        
        return JSONResponse(content={"success": True, "data": result.data})
        
    except Exception as e:
        logger.error(f"Error updating chat session: {e}")
        return JSONResponse(content={"success": False, "error": str(e)})

@router.delete("/chat_session/{session_id}")
async def delete_chat_session(session_id: str) -> JSONResponse:
    """Delete a chat session"""
    supabase_client = get_supabase_client()
    if not supabase_client:
        return JSONResponse(content={"success": True})
    
    try:
        # Delete from database
        supabase_client.table("chat_sessions").delete().eq("id", session_id).execute()
        
        # Also delete messages
        try:
            supabase_client.table("messages").delete().eq("conversation_id", session_id).execute()
        except Exception as msg_err:
            logger.warning(f"Error deleting messages: {msg_err}")
            
        # Delete conversation record
        try:
            supabase_client.table("conversations").delete().eq("conversation_id", session_id).execute()
        except Exception as conv_err:
            logger.warning(f"Error deleting conversation: {conv_err}")
        
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        return JSONResponse(content={"success": False, "error": str(e)})

@router.get("/search_chat_sessions")
async def search_chat_sessions(user_id: str, search_term: str) -> JSONResponse:
    """Search user's chat sessions by content"""
    supabase_client = get_supabase_client()
    if not supabase_client:
        return JSONResponse(content=[])
    
    try:
        logger.info(f"Searching chat sessions for user: {user_id}, term: {search_term}")
        
        # Search in session titles
        sessions_result = supabase_client.table("chat_sessions").select("*").eq("user_id", user_id).ilike("title", f"%{search_term}%").execute()
        sessions = sessions_result.data or []
        
        # Search in messages
        messages_result = supabase_client.table("messages").select("conversation_id").eq("user_id", user_id).ilike("request", f"%{search_term}%").execute()
        message_sessions = [msg["conversation_id"] for msg in messages_result.data or []]
        
        # Get sessions from message matches
        for session_id in message_sessions:
            try:
                session_result = supabase_client.table("chat_sessions").select("*").eq("id", session_id).single().execute()
                if session_result.data and session_result.data not in sessions:
                    sessions.append(session_result.data)
            except:
                continue
        
        return JSONResponse(content=sessions)
        
    except Exception as e:
        logger.error(f"Error searching chat sessions: {e}")
        return JSONResponse(content=[])

@router.post("/messages")
async def create_message(request: Request) -> JSONResponse:
    """Create a new message"""
    supabase_client = get_supabase_client()
    
    try:
        body = await request.json()
        
        # Validate required fields
        required_fields = ['conversation_id', 'user_id', 'request']
        missing_fields = [field for field in required_fields if not body.get(field)]
        
        if missing_fields:
            return JSONResponse(
                status_code=400,
                content={"error": f"Missing required fields: {', '.join(missing_fields)}"}
            )
        
        # Generate ID if not provided
        if 'message_id' not in body and 'id' not in body:
            import random
            body['message_id'] = int(time.time() * 1000) * 1000 + random.randint(0, 999)
        
        # Ensure created_at
        if 'created_at' not in body:
            body['created_at'] = datetime.now().isoformat()
        
        # Clean and prepare data
        cleaned_body = {}
        for key, value in body.items():
            if value is not None and value != "" and key != "":
                if key in ['request_payload', 'response_payload', 'metadata'] and isinstance(value, dict):
                    cleaned_body[key] = json.dumps(value)
                else:
                    cleaned_body[key] = value
        
        # Ensure IDs are strings
        if 'conversation_id' in cleaned_body:
            cleaned_body['conversation_id'] = str(cleaned_body['conversation_id'])
        if 'user_id' in cleaned_body:
            cleaned_body['user_id'] = str(cleaned_body['user_id'])
        
        if not supabase_client:
            # Return mock response
            return JSONResponse(content={
                "id": cleaned_body.get('message_id', 'unknown'),
                "created_at": cleaned_body.get('created_at'),
                "conversation_id": cleaned_body.get('conversation_id'),
                "user_id": cleaned_body.get('user_id')
            })
        
        # Insert into database
        result = supabase_client.table("messages").insert(cleaned_body).execute()
        
        if hasattr(result, 'data') and result.data:
            return JSONResponse(content=result.data[0])
        else:
            return JSONResponse(content={
                "id": cleaned_body.get('message_id', 'unknown'),
                "created_at": cleaned_body.get('created_at'),
                "conversation_id": cleaned_body.get('conversation_id'),
                "user_id": cleaned_body.get('user_id')
            })
        
    except Exception as e:
        logger.error(f"Error creating message: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@router.put("/message")
async def update_message(request: Request) -> JSONResponse:
    """Update an existing message"""
    supabase_client = get_supabase_client()
    
    try:
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8', errors='replace')
        body = json.loads(body_str)
        
        logger.info(f"Creating message with custom ID: {body.get('message_id', 'unknown')}")
        
        # Validate required fields
        required_fields = ["user_id", "conversation_id"]
        missing_fields = [field for field in required_fields if not body.get(field)]
        
        if missing_fields:
            return JSONResponse(
                status_code=400,
                content={"error": f"Missing required fields: {', '.join(missing_fields)}"}
            )
        
        # Generate ID if not provided
        if 'message_id' not in body and 'id' not in body:
            import random
            body['message_id'] = int(time.time() * 1000) * 1000 + random.randint(0, 999)
        
        # Ensure created_at
        if 'created_at' not in body:
            body['created_at'] = datetime.now().isoformat()
        
        # Clean and prepare data
        cleaned_body = {}
        for key, value in body.items():
            if value is not None and value != "" and key != "":
                if key in ['request_payload', 'response_payload', 'metadata'] and isinstance(value, dict):
                    cleaned_body[key] = json.dumps(value)
                else:
                    cleaned_body[key] = value
        
        # Ensure IDs are strings
        if 'conversation_id' in cleaned_body:
            cleaned_body['conversation_id'] = str(cleaned_body['conversation_id'])
        if 'user_id' in cleaned_body:
            cleaned_body['user_id'] = str(cleaned_body['user_id'])
        
        if not supabase_client:
            # Return mock response
            return JSONResponse(content={
                "id": cleaned_body.get('message_id', 'unknown'),
                "created_at": cleaned_body.get('created_at'),
                "conversation_id": cleaned_body.get('conversation_id'),
                "user_id": cleaned_body.get('user_id')
            })
        
        # Insert into database
        result = supabase_client.table("messages").insert(cleaned_body).execute()
        
        if hasattr(result, 'data') and result.data:
            return JSONResponse(content=result.data[0])
        else:
            return JSONResponse(content={
                "id": cleaned_body.get('message_id', 'unknown'),
                "created_at": cleaned_body.get('created_at'),
                "conversation_id": cleaned_body.get('conversation_id'),
                "user_id": cleaned_body.get('user_id')
            })
            
    except Exception as e:
        logger.error(f"Error creating message: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@router.get("/messages_schema")
async def get_messages_schema() -> JSONResponse:
    """Get the schema of the messages table"""
    supabase_client = get_supabase_client()
    
    # Default schema
    dummy_schema = {
        "message_id": 0,
        "conversation_id": "",
        "user_id": "",
        "request": "",
        "response": "",
        "created_at": "",
        "status": "",
        "status_updated_at": "",
        "error_message": "",
        "request_type": "",
        "request_payload": {},
        "response_payload": {},
        "status_code": 0,
        "processing_start_time": "",
        "processing_end_time": "",
        "processing_time_ms": 0,
        "is_sensitive": False,
        "metadata": {},
        "chat_session_id": ""
    }
    
    if not supabase_client:
        return JSONResponse(content={"columns": list(dummy_schema.keys())})
    
    try:
        result = supabase_client.table("messages").select("*").limit(1).execute()
        
        if result.data and len(result.data) > 0:
            columns = list(result.data[0].keys())
            return JSONResponse(content={"columns": columns})
        
        return JSONResponse(content={"columns": list(dummy_schema.keys())})
        
    except Exception as e:
        logger.error(f"Error getting messages schema: {e}")
        return JSONResponse(content={"columns": list(dummy_schema.keys())})

# Documents Endpoints (Enhanced with AI service integration)

@router.get("/documents")
async def get_documents() -> JSONResponse:
    """Get all documents"""
    supabase_client = get_supabase_client()
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        result = supabase_client.table("documents").select("*").order("created_at", desc=True).execute()
        return JSONResponse(content=result.data)
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document(document_id: int) -> JSONResponse:
    """Get a specific document"""
    supabase_client = get_supabase_client()
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        result = supabase_client.table("documents").select("*").eq("id", document_id).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        return JSONResponse(content=result.data)
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents")
async def create_document(request: Request) -> JSONResponse:
    """Create a new document"""
    supabase_client = get_supabase_client()
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        body = await request.json()
        
        # Try RPC function first
        try:
            result = supabase_client.rpc("create_document", {
                "name": body.get("name"),
                "type": body.get("type"),
                "size": body.get("size"),
                "url": body.get("url"),
                "user_id": body.get("user_id")
            }).execute()
            
            if result.data:
                doc_result = supabase_client.table("documents").select("*").eq("id", result.data).single().execute()
                return JSONResponse(content=doc_result.data)
        except Exception as rpc_err:
            logger.warning(f"RPC failed, using direct insert: {rpc_err}")
            result = supabase_client.table("documents").insert(body).execute()
            return JSONResponse(content=result.data[0] if result.data else None)
            
    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: int) -> JSONResponse:
    """Delete a document"""
    supabase_client = get_supabase_client()
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        # Get document info first
        doc_result = supabase_client.table("documents").select("*").eq("id", document_id).single().execute()
        if not doc_result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from database
        supabase_client.table("documents").delete().eq("id", document_id).execute()
        
        # Try to delete from storage
        if doc_result.data.get("url"):
            try:
                url = doc_result.data.get("url")
                parts = url.split("/")
                filename = parts[-1].split("?")[0]
                supabase_client.storage.from_("documents").remove([filename])
            except Exception as storage_err:
                logger.warning(f"Failed to delete file from storage: {storage_err}")
        
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ SIMPLE: Context Management Endpoints only
@router.get("/ai/context/stats")
async def get_context_stats(ai_service: AIServiceClient = Depends(get_ai_service)):
    """Get context management statistics"""
    try:
        stats = await ai_service.get_context_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting context stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/ai/context/clear/{session_id}")
async def clear_session_context(
    session_id: str,
    ai_service: AIServiceClient = Depends(get_ai_service)
):
    """Clear context cache for specific session"""
    try:
        result = await ai_service.clear_session_context(session_id)
        return result
    except Exception as e:
        logger.error(f"Error clearing session context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/ai/context/clear-all")
async def clear_all_context(
    ai_service: AIServiceClient = Depends(get_ai_service)
):
    """Clear all context caches"""
    try:
        result = await ai_service.clear_all_context()
        return result
    except Exception as e:
        logger.error(f"Error clearing all context: {e}")
        raise HTTPException(status_code=500, detail=str(e))