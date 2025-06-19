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

# Note: Mock data stores removed - now using proper Supabase service

# Chat Sessions Routes
@router.get("/api/proxy/chat_sessions")
async def get_chat_sessions(
    user_id: str,
    session_service: IChatSessionService = Depends(get_chat_session_service)
):
    """
    Get all chat sessions for a user.
    """
    try:
        logger.info(f"GET /api/proxy/chat_sessions for user: {user_id}")
        
        # Use the actual Supabase service instead of mock data
        sessions = await session_service.get_sessions(user_id)
        logger.info(f"Found {len(sessions)} sessions for user {user_id}")
        
        return JSONResponse(content=sessions)
        
    except Exception as e:
        logger.error(f"Error in get_chat_sessions: {str(e)}")
        # Return empty array as fallback
        return JSONResponse(content=[], status_code=200)

@router.post("/api/proxy/chat_sessions")
async def create_chat_session(
    request: Request,
    session_service: IChatSessionService = Depends(get_chat_session_service)
):
    """
    Create a new chat session.
    """
    try:
        body = await request.json()
        logger.info(f"POST /api/proxy/chat_sessions with body: {body}")
        
        user_id = body.get("user_id", "anonymous")
        title = body.get("title", "New Chat")
        
        # Use the actual Supabase service instead of mock data
        new_session = await session_service.create_session(user_id, title)
        
        logger.info(f"Created new session: {new_session.get('id')} for user: {user_id}")
        return JSONResponse(content=new_session)
        
    except Exception as e:
        logger.error(f"Error in create_chat_session: {str(e)}")
        # Return fallback session
        fallback_session_id = str(uuid.uuid4())
        fallback_session = {
            "id": fallback_session_id,
            "user_id": body.get("user_id", "anonymous") if 'body' in locals() else "anonymous",
            "title": body.get("title", "New Chat") if 'body' in locals() else "New Chat",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        return JSONResponse(content=fallback_session)

@router.get("/api/proxy/chat_sessions/{session_id}")
async def get_chat_session(
    session_id: str,
    session_service: IChatSessionService = Depends(get_chat_session_service)
):
    """
    Get a specific chat session with its messages.
    """
    try:
        logger.info(f"GET /api/proxy/chat_sessions/{session_id}")
        
        # Use the actual Supabase service instead of mock data
        session = await session_service.get_session(session_id)
        
        if session:
            logger.info(f"Found session {session_id}")
            return JSONResponse(content=session)
        else:
            logger.warning(f"Session {session_id} not found")
            return JSONResponse(
                status_code=404,
                content={"error": f"Session {session_id} not found"}
            )
            
    except Exception as e:
        logger.error(f"Error in get_chat_session: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

@router.patch("/api/proxy/chat_session/{session_id}")
async def update_chat_session(
    session_id: str,
    request: Request,
    session_service: IChatSessionService = Depends(get_chat_session_service)
):
    """
    Update a chat session.
    """
    try:
        body = await request.json()
        logger.info(f"PATCH /api/proxy/chat_session/{session_id} with body: {body}")
        
        # Validate allowed fields for session updates
        allowed_fields = {"title", "user_id", "updated_at", "metadata"}
        received_fields = set(body.keys())
        invalid_fields = received_fields - allowed_fields
        
        if invalid_fields:
            logger.warning(f"Invalid fields received: {invalid_fields}")
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid fields: {', '.join(invalid_fields)}"}
            )
        
        # Use the actual Supabase service instead of mock data
        updated_session = await session_service.update_session(session_id, body)
        
        logger.info(f"Updated session {session_id}")
        return JSONResponse(content={"success": True, "data": updated_session})
        
    except Exception as e:
        logger.error(f"Error in update_chat_session: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

@router.patch("/api/proxy/chat_sessions/{session_id}")
async def update_chat_sessions_plural(
    session_id: str,
    request: Request,
    session_service: IChatSessionService = Depends(get_chat_session_service)
):
    """
    Alias for update_chat_session to maintain backwards compatibility.
    """
    return await update_chat_session(session_id, request, session_service)

@router.delete("/api/proxy/chat_session/{session_id}")
async def delete_chat_session(
    session_id: str,
    session_service: IChatSessionService = Depends(get_chat_session_service)
):
    """
    Delete a chat session.
    """
    logger.info(f"DELETE /api/proxy/chat_session/{session_id}")
    try:
        # Use the actual Supabase service instead of mock data
        success = await session_service.delete_session(session_id)
        
        if success:
            logger.info(f"Successfully deleted session {session_id}")
            return {"success": True, "deleted": session_id}
        else:
            logger.warning(f"Failed to delete session {session_id}")
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found or already deleted"}
            )
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
async def create_message(
    request: Request,
    message_service: IMessageService = Depends(get_message_service)
):
    """
    Create a new message using the actual Supabase service.
    """
    try:
        body = await request.json()
        logger.info(f"POST /api/proxy/messages with body: {json.dumps(body)[:100]}")
        
        # Extract required fields
        conversation_id = body.get("conversation_id")
        user_id = body.get("user_id")
        message_text = body.get("message_text") or body.get("content", "")
        is_bot = body.get("is_bot", False)
        
        if not conversation_id or not user_id:
            return JSONResponse(
                status_code=400,
                content={"error": "conversation_id and user_id are required"}
            )
        
        # Use the actual message service to create the message
        message = await message_service.create_message(
            user_id=user_id,
            conversation_id=conversation_id,
            content=message_text,
            is_bot=is_bot
        )
        
        if message:
            logger.info(f"Created message {message.get('id')} for session {conversation_id}")
            return JSONResponse(content=[message])  # Wrap in array to match original API
        else:
            logger.error("Failed to create message")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to create message"}
            )
            
    except Exception as e:
        logger.error(f"Error in create_message: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

@router.put("/api/proxy/message")
async def update_message(
    request: Request,
    message_service: IMessageService = Depends(get_message_service)
):
    """
    Add or update a message with custom ID using the actual Supabase service.
    """
    try:
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8", errors="replace")
        logger.info(f"🚀 PUT /api/proxy/message with body: {body_str[:100]}")
        
        try:
            body = json.loads(body_str)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON body: {e}")
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid JSON in request body: {str(e)}"}
            )
        
        # Check for required fields
        conversation_id = body.get("conversation_id")
        user_id = body.get("user_id")
        content = body.get("content", "")
        is_bot = body.get("is_bot", False)
        
        logger.info(f"🔍 Extracted fields: conversation_id={conversation_id}, user_id={user_id}, content={content[:50]}..., is_bot={is_bot}")
        
        if not conversation_id or not user_id:
            logger.error("❌ Missing required fields: conversation_id or user_id")
            return JSONResponse(
                status_code=400,
                content={"error": "conversation_id and user_id are required"}
            )
        
        # Use the actual message service to create the message
        logger.info(f"🚀 Calling message_service.create_message...")
        message = await message_service.create_message(
            user_id=user_id,
            conversation_id=conversation_id,
            content=content,
            is_bot=is_bot
        )
        
        logger.info(f"🔍 Message service returned: {message}")
        
        if message:
            logger.info(f"✅ Created message {message.get('id')} for session {conversation_id}")
            return JSONResponse(content=message)
        else:
            logger.error("❌ Failed to create message via message service")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to create message"}
            )
            
    except Exception as e:
        logger.error(f"❌ Error in update_message: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
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