import logging
import json
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from datetime import datetime

from ...core.interfaces import IChatService
from ...domain.models import ChatRequest
from ...api.deps import get_chat_service
from ...config.settings import settings
from ...services.chat_service import ChatService
from ...core.auth import get_current_user

# Try to import advanced chat service
try:
    from ...services.advanced_chat_service import AdvancedChatService
    ADVANCED_CHAT_AVAILABLE = True
except ImportError:
    ADVANCED_CHAT_AVAILABLE = False

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat"])

def get_chat_service() -> IChatService:
    """Factory to get the appropriate chat service"""
    if ADVANCED_CHAT_AVAILABLE and settings.ENABLE_ADVANCED_CHAT:
        logger.info("🚀 Using AdvancedChatService (LangGraph)")
        return AdvancedChatService()
    else:
        logger.info("🔄 Using legacy ChatService")
        return ChatService()

# Initialize the chat service
chat_service = get_chat_service()

@router.post("/api/chat")
async def chat(
    request: Request, 
    chat_service: IChatService = Depends(get_chat_service)
):
    """
    Process chat messages and return AI responses.
    """
    try:
        # Log request headers for debugging
        logger.info(f"Request headers: {request.headers.get('content-type', 'Not specified')}")
        
        # Parse request body
        try:
            body_bytes = await request.body()
            body_str = body_bytes.decode('utf-8', errors='replace')
            logger.info(f"Raw request body (first 500 chars): {body_str[:500]}...")
            
            body = json.loads(body_str)
            # Validate with Pydantic
            chat_data = ChatRequest(**body)
            logger.info(f"Validated chat_data.message: {chat_data.message[:50]}...")
            if chat_data.history:
                logger.info(f"Validated chat_data.history contains {len(chat_data.history)} messages.")
            else:
                logger.info("Validated chat_data.history is None or empty.")
        except json.JSONDecodeError:
            logger.warning("Invalid JSON received in chat request")
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except Exception as pydantic_err:
            logger.warning(f"Chat request validation failed: {pydantic_err}")
            raise HTTPException(
                status_code=422, 
                detail=f"Invalid chat request data: {pydantic_err}"
            )
        
        # Process the message through the service
        result = await chat_service.process_chat_message(
            chat_data.message, 
            chat_data.user_id,
            chat_data.history
        )
        
        # Return response
        return JSONResponse(
            content=result,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions to be caught by global handler
        raise http_exc
    except Exception as e:
        # Catch any unexpected errors
        logger.exception(f"Unexpected error in chat router: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error processing your request"
        )

@router.post("/api/chat/stream")
async def chat_stream(
    request: Request, 
    chat_service: IChatService = Depends(get_chat_service)
):
    """
    Process chat messages and return streaming AI responses using Server-Sent Events.
    """
    try:
        # Parse request body
        try:
            body_bytes = await request.body()
            body_str = body_bytes.decode('utf-8', errors='replace')
            body = json.loads(body_str)
            chat_data = ChatRequest(**body)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON received in chat stream request")
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except Exception as pydantic_err:
            logger.warning(f"Chat stream request validation failed: {pydantic_err}")
            raise HTTPException(
                status_code=422, 
                detail=f"Invalid chat request data: {pydantic_err}"
            )
        
        # Create a generator function for streaming
        async def generate_stream():
            try:
                # Send initial event
                yield f"data: {json.dumps({'type': 'start', 'content': ''})}\n\n"
                
                # Process the message through the streaming service
                async for chunk in chat_service.process_chat_message_stream(
                    chat_data.message, 
                    chat_data.user_id,
                    chat_data.history
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                # Send end event
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
            except Exception as e:
                logger.exception(f"Error in stream generation: {e}")
                yield f"data: {json.dumps({'type': 'error', 'content': 'Stream processing error'})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
            }
        )
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Unexpected error in chat stream router: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error processing your streaming request"
        )

@router.post("/chat", response_model=dict)
async def chat(
    request: ChatRequest,
    user: dict = Depends(get_current_user)
):
    """
    Enhanced Chat endpoint with advanced memory management
    
    Features:
    - Persistent conversation context across sessions
    - Automatic conversation summarization
    - Smart context trimming for token management
    - RAG integration with source tracking
    """
    try:
        logger.info(f"🚀 [ENHANCED-CHAT] Processing for user: {user.get('id', 'unknown')}")
        
        # Process with advanced chat service
        response = await chat_service.process_chat_message(
            user_message=request.message,
            user_id=str(user.get('id', 'anonymous')),
            history=request.history
        )
        
        # Enhanced response with metadata
        return {
            "message": response.get("response", ""),
            "sources": response.get("sources", []),
            "chunks": response.get("chunks", 0),
            "metadata": {
                "summary_available": bool(response.get("summary", "")),
                "context_trimmed": response.get("context_trimmed", False),
                "service_type": "advanced" if ADVANCED_CHAT_AVAILABLE else "legacy",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ [ENHANCED-CHAT] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error processing your message with advanced chat service"
        )

@router.get("/chat/status")
async def get_chat_status():
    """
    Get status of the advanced chat system
    """
    try:
        return {
            "advanced_chat_available": ADVANCED_CHAT_AVAILABLE,
            "service_type": "advanced" if ADVANCED_CHAT_AVAILABLE and settings.ENABLE_ADVANCED_CHAT else "legacy",
            "langgraph_available": ADVANCED_CHAT_AVAILABLE,
            "settings": {
                "enable_advanced_chat": settings.ENABLE_ADVANCED_CHAT,
                "max_context_tokens": settings.MAX_CONTEXT_TOKENS,
                "summary_frequency": settings.CONVERSATION_SUMMARY_FREQUENCY,
                "has_supabase_url": bool(settings.SUPABASE_DB_URL)
            },
            "features": {
                "persistent_memory": True,
                "conversation_summary": True,
                "smart_context_trimming": True,
                "rag_integration": True,
                "cross_thread_memory": True
            }
        }
    except Exception as e:
        logger.error(f"Error getting chat status: {e}")
        return {"error": str(e)}