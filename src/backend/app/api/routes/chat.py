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

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat"])

def get_chat_service() -> IChatService:
    """Factory to get the chat service"""
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
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
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
    Chat endpoint with conversation management
    
    Features:
    - Window-based conversation memory (LangChain)
    - RAG integration with source tracking
    - Streaming support
    - Session isolation
    """
    try:
        logger.info(f"🔄 [CHAT] Processing for user: {user.get('id', 'unknown')}")
        
        # Process with chat service
        response = await chat_service.process_chat_message(
            user_message=request.message,
            user_id=str(user.get('id', 'anonymous')),
            history=request.history
        )
        
        # Return response with metadata
        return {
            "message": response.get("response", ""),
            "sources": response.get("sources", []),
            "chunks": response.get("chunks", 0),
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "rag_used": len(response.get("sources", [])) > 0
            }
        }
        
    except Exception as e:
        logger.error(f"❌ [CHAT] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error processing your message with chat service"
        )

@router.get("/chat/status")
async def get_chat_status():
    """
    Get status of the chat system
    """
    try:
        return {
            "service_type": "chat_service",
            "settings": {
                "max_context_tokens": settings.MAX_CONTEXT_TOKENS,
                "langchain_history_k": settings.LANGCHAIN_HISTORY_K,
                "gemini_model": settings.GEMINI_MODEL_NAME
            },

            "features": {
                "rag_integration": True,
                "streaming": True,
                "conversation_memory": True,
                "source_tracking": True
            }
        }
    except Exception as e:
        logger.error(f"Error getting chat status: {e}")
        return {"error": str(e)}

