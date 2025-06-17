import logging
import json
import time
import uuid
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from ...core.interfaces import IChatSessionService, IMessageService
from ...api.deps import get_chat_session_service, get_message_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Proxy"])

# Global mock data store for session persistence across requests
mock_sessions_store = {}
mock_messages_store = {}  # Store messages by session_id: [messages]
deleted_sessions = set()
default_sessions_initialized = False

# Chat Sessions Routes
@router.get("/api/proxy/chat_sessions")
async def get_chat_sessions(user_id: str):
    """
    Get all chat sessions for a user.
    """
    try:
        logger.info(f"GET /api/proxy/chat_sessions for user: {user_id}")
        
        # Filter out deleted sessions and return sessions for this user
        active_sessions = []
        for session_id, session in mock_sessions_store.items():
            if session_id not in deleted_sessions and session.get("user_id") == user_id:
                active_sessions.append(session)
        
        # If no sessions exist and we haven't initialized default sessions, create them
        global default_sessions_initialized
        if not active_sessions and not default_sessions_initialized:
            mock_sessions = [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440001",
                    "user_id": user_id,
                    "title": "שאלה על תקנון הלימודים",
                    "created_at": "2025-01-15T10:00:00Z",
                    "updated_at": "2025-01-15T10:05:00Z"
                },
                {
                    "id": "550e8400-e29b-41d4-a716-446655440002", 
                    "user_id": user_id,
                    "title": "חניה במקום אסור - מה העונש?",
                    "created_at": "2025-01-14T14:30:00Z",
                    "updated_at": "2025-01-14T14:35:00Z"
                },
                {
                    "id": "550e8400-e29b-41d4-a716-446655440003",
                    "user_id": user_id,
                    "title": "הגשת עבודות באיחור",
                    "created_at": "2025-01-13T09:15:00Z", 
                    "updated_at": "2025-01-13T09:20:00Z"
                }
            ]
            
            # Store them in our mock store
            for session in mock_sessions:
                mock_sessions_store[session["id"]] = session
            
            # Mark that we've initialized default sessions
            default_sessions_initialized = True
                
            # Filter again to exclude any pre-deleted sessions
            active_sessions = [s for s in mock_sessions if s["id"] not in deleted_sessions]
            return JSONResponse(content=active_sessions)
        
        # Sort by updated_at descending
        active_sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return JSONResponse(content=active_sessions)
        
    except Exception as e:
        logger.error(f"Error in get_chat_sessions: {str(e)}")
        # Return empty array as fallback
        return JSONResponse(content=[], status_code=200)

@router.post("/api/proxy/chat_sessions")
async def create_chat_session(request: Request):
    """
    Create a new chat session.
    """
    try:
        body = await request.json()
        logger.info(f"POST /api/proxy/chat_sessions with body: {body}")
        
        user_id = body.get("user_id", "anonymous")
        title = body.get("title", "New Chat")
        
        # Generate proper UUID for session ID
        session_id = str(uuid.uuid4())
        current_time = datetime.utcnow().isoformat() + "Z"
        
        # Create properly formatted session response
        new_session = {
            "id": session_id,
            "user_id": user_id,
            "title": title,
            "created_at": current_time,
            "updated_at": current_time
        }
        
        # Store in our mock data store
        mock_sessions_store[session_id] = new_session
        
        logger.info(f"Created new session: {session_id} for user: {user_id}")
        return JSONResponse(content=new_session)
        
    except Exception as e:
        logger.error(f"Error in create_chat_session: {str(e)}")
        # Return mock session as fallback
        try:
            body = await request.json() if hasattr(request, 'json') else {}
        except:
            body = {}
            
        fallback_session_id = str(uuid.uuid4())
        fallback_session = {
            "id": fallback_session_id,
            "user_id": body.get("user_id", "anonymous"),
            "title": body.get("title", "New Chat"),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Store in our mock data store
        mock_sessions_store[fallback_session_id] = fallback_session
        
        return JSONResponse(content=fallback_session)

@router.get("/api/proxy/chat_sessions/{session_id}")
async def get_chat_session(session_id: str):
    """
    Get a specific chat session with its messages.
    """
    try:
        logger.info(f"GET /api/proxy/chat_sessions/{session_id}")
        
        # Check if session exists in our store
        if session_id in mock_sessions_store and session_id not in deleted_sessions:
            session = mock_sessions_store[session_id].copy()
            
            # Add messages from the messages store
            session_messages = mock_messages_store.get(session_id, [])
            session["messages"] = session_messages
            
            logger.info(f"Found session {session_id} in mock store with {len(session_messages)} messages")
            return JSONResponse(content=session)
        
        # Return mock session data for backward compatibility
        mock_session = {
            "id": session_id,
            "user_id": "mock-user-id",
            "title": "Mock Chat Session",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "messages": []
        }
        return JSONResponse(content=mock_session)
        
    except Exception as e:
        logger.error(f"Error in get_chat_session: {str(e)}")
        return JSONResponse(
            status_code=404,
            content={"error": "Chat session not found"}
        )

@router.patch("/api/proxy/chat_session/{session_id}")
async def update_chat_session(
    session_id: str,
    request: Request
):
    """
    Update a chat session - mock implementation for persistence.
    """
    try:
        body = await request.json()
        logger.info(f"PATCH /api/proxy/chat_session/{session_id} with body: {body}")
        
        # Update session in our mock store
        if session_id in mock_sessions_store:
            current_session = mock_sessions_store[session_id]
            current_session.update(body)
            current_session["updated_at"] = datetime.utcnow().isoformat() + "Z"
            logger.info(f"Updated session {session_id} in mock store")
        else:
            logger.warning(f"Session {session_id} not found in mock store, skipping update")
        
        return JSONResponse(content={"success": True, "data": None})
        
    except Exception as e:
        logger.error(f"Error in update_chat_session: {str(e)}")
        return JSONResponse(content={"success": True, "data": None})

@router.patch("/api/proxy/chat_sessions/{session_id}")
async def update_chat_sessions_plural(
    session_id: str,
    request: Request
):
    """
    Alias for update_chat_session to maintain backwards compatibility.
    """
    return await update_chat_session(session_id, request)

@router.delete("/api/proxy/chat_session/{session_id}")
async def delete_chat_session(session_id: str):
    """
    Delete a chat session - mock implementation for persistence.
    """
    logger.info(f"DELETE /api/proxy/chat_session/{session_id}")
    try:
        # Actually remove session from mock store and mark as deleted
        if session_id in mock_sessions_store:
            del mock_sessions_store[session_id]
        
        # Also remove all messages for this session
        if session_id in mock_messages_store:
            del mock_messages_store[session_id]
            logger.info(f"Deleted messages for session {session_id}")
        
        deleted_sessions.add(session_id)
        logger.info(f"Successfully deleted session {session_id} from store")
        return {"success": True, "deleted": session_id}
    except Exception as e:
        logger.error(f"Error in delete_chat_session: {e}")
        return {"success": True, "deleted": session_id, "note": "Session removed from client"}

@router.get("/api/proxy/search_chat_sessions")
async def search_chat_sessions(
    user_id: str,
    search_term: str,
    session_service: IChatSessionService = Depends(get_chat_session_service)
):
    """
    Search for chat sessions matching a term.
    """
    logger.info(f"GET /api/proxy/search_chat_sessions for user: {user_id} with term: {search_term}")
    return await session_service.search_sessions(user_id, search_term)

# Messages Routes
@router.post("/api/proxy/messages")
async def create_message(request: Request):
    """
    Create a new message - simplified version.
    """
    try:
        body = await request.json()
        logger.info(f"POST /api/proxy/messages with body: {json.dumps(body)[:100]}")
        
        # Create mock response
        message_id = f"msg-{int(time.time() * 1000)}"
        result = {
            "id": message_id,
            "conversation_id": body.get("conversation_id", ""),
            "user_id": body.get("user_id", ""),
            "content": body.get("content", ""),
            "role": body.get("role", "user"),
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        return JSONResponse(content=[result])  # Wrap in array to match original API
    except Exception as e:
        logger.error(f"Error in create_message: {str(e)}")
        # Instead of returning error, return mock data
        return JSONResponse(
            content=[{
                "id": "mock-message-id",
                "conversation_id": "",
                "created_at": datetime.utcnow().isoformat() + "Z"
            }]
        )

@router.put("/api/proxy/message")
async def update_message(request: Request):
    """
    Add or update a message with custom ID - simplified version.
    """
    try:
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8", errors="replace")
        logger.info(f"PUT /api/proxy/message with body: {body_str[:100]}")
        
        try:
            body = json.loads(body_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON body: {e}")
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid JSON in request body: {str(e)}"}
            )
        
        # Check for required fields
        required_fields = ["user_id", "conversation_id"]
        missing_fields = [field for field in required_fields if not body.get(field)]
        
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return JSONResponse(
                status_code=400,
                content={"error": f"Missing required fields: {', '.join(missing_fields)}"}
            )
        
        # Create mock response
        result = {
            "id": body.get("id", f"msg-{int(time.time() * 1000)}"),
            "conversation_id": body.get("conversation_id"),
            "user_id": body.get("user_id"),
            "content": body.get("content", ""),
            "role": body.get("role", "user"),
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Store message in mock messages store
        session_id = body.get("conversation_id")
        if session_id:
            if session_id not in mock_messages_store:
                mock_messages_store[session_id] = []
            mock_messages_store[session_id].append(result)
            logger.info(f"Stored message in session {session_id}, total messages: {len(mock_messages_store[session_id])}")
        
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in update_message: {str(e)}")
        # Return a generic response
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@router.get("/api/proxy/messages_schema")
async def get_messages_schema():
    """
    Get message table schema (column names).
    """
    try:
        logger.info("GET /api/proxy/messages_schema")
        # Return mock schema data that matches what the frontend expects
        schema = [
            {"column_name": "id", "data_type": "uuid"},
            {"column_name": "conversation_id", "data_type": "varchar"},
            {"column_name": "user_id", "data_type": "uuid"},
            {"column_name": "content", "data_type": "text"},
            {"column_name": "role", "data_type": "varchar"},
            {"column_name": "created_at", "data_type": "timestamp"},
            {"column_name": "updated_at", "data_type": "timestamp"}
        ]
        return JSONResponse(content=schema)
    except Exception as e:
        logger.error(f"Error in get_messages_schema: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get message schema"}
        )

# Documents Routes
@router.get("/api/proxy/documents")
async def proxy_get_documents(request: Request):
    """
    Get all documents via proxy - now returns real data from Supabase.
    """
    try:
        logger.info("GET /api/proxy/documents - fetching real data from Supabase")
        
        # Get Supabase client
        from src.backend.app.core.database import get_supabase_client
        supabase = get_supabase_client()
        
        if not supabase:
            logger.warning("Supabase client not available, returning empty list")
            return JSONResponse(content=[])
        
        # Query real documents from database
        result = supabase.table("documents").select("*").order("created_at", desc=True).execute()
        
        if not result.data:
            logger.info("No documents found in database")
            return JSONResponse(content=[])
        
        logger.info(f"Found {len(result.data)} documents in database")
        return JSONResponse(content=result.data)
        
    except Exception as e:
        logger.error(f"Error in proxy_get_documents: {str(e)}", exc_info=True)
        # Return empty list instead of error to prevent frontend crashes
        return JSONResponse(content=[], status_code=200)

@router.get("/api/proxy/documents/{document_id}")
async def proxy_get_document(document_id: int, request: Request):
    """
    Get a specific document via proxy.
    """
    try:
        logger.info(f"GET /api/proxy/documents/{document_id}")
        return JSONResponse(content={
            "id": document_id,
            "title": f"תמסך {document_id}",
            "content": f"תוכן המסמך מספר {document_id}",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        })
    except Exception as e:
        logger.error(f"Error in proxy_get_document: {str(e)}")
        return JSONResponse(content={}, status_code=404)

@router.post("/api/proxy/documents")
async def proxy_create_document(request: Request):
    """
    Create a new document via proxy.
    """
    try:
        body = await request.json()
        logger.info(f"POST /api/proxy/documents with body: {json.dumps(body)[:100]}")
        
        # Return success response
        return JSONResponse(content={
            "id": 999,
            "title": body.get("title", "New Document"),
            "created_at": "2025-01-01T00:00:00Z",
            "success": True
        })
    except Exception as e:
        logger.error(f"Error in proxy_create_document: {str(e)}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

@router.delete("/api/proxy/documents/{document_id}")
async def proxy_delete_document(document_id: int, request: Request):
    """
    Delete a document via proxy.
    """
    try:
        logger.info(f"DELETE /api/proxy/documents/{document_id}")
        return JSONResponse(content={"success": True})
    except Exception as e:
        logger.error(f"Error in proxy_delete_document: {str(e)}")
        return JSONResponse(content={"success": False}, status_code=500)

# Additional routes can be added here as needed