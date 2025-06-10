# import httpx # No longer needed directly
import json
import logging

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse # Keep for potential error responses

# Import config and models with absolute imports
from backend.core import config
from backend.models.schemas import ChatRequest

# Import the service with absolute imports
from backend.services.chat_service import ChatService, get_chat_service

logger = logging.getLogger(__name__)
router = APIRouter()

# AI_SERVICE_URL is now in config
# AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:5000")

@router.post("/api/chat", tags=["Chat"])
async def chat(request: Request, chat_service: ChatService = Depends(get_chat_service)):
    """
    Process chat messages using the ChatService.
    Handles request parsing, validation, and calls the service.
    """
    try:
        # Log request headers for debugging
        logger.info(f"Request headers: {request.headers.get('content-type', 'Not specified')}")
        
        # Parse incoming request body - keep this logic here or create a dependency
        try:
            body_bytes = await request.body()
            body_str = body_bytes.decode('utf-8', errors='replace')
            # logger.info(f"Raw request body (first 100 chars): {body_str[:100]}...")
            
            body = json.loads(body_str)
            # Validate request body using Pydantic model
            chat_data = ChatRequest(**body)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON received in chat request")
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except Exception as pydantic_err: # Catch Pydantic validation errors
            logger.warning(f"Chat request validation failed: {pydantic_err}")
            raise HTTPException(status_code=422, detail=f"Invalid chat request data: {pydantic_err}")
        
        user_message = chat_data.message
        # Note: user_id from chat_data is available if needed: chat_data.user_id
        
        # Basic validation (presence check)
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Validate message length using config
        if len(user_message) > config.MAX_CHAT_MESSAGE_LENGTH:
            raise HTTPException(status_code=400, detail=f"Message too long (max {config.MAX_CHAT_MESSAGE_LENGTH} characters)")
        
        logger.info(f"Processing chat request (user: {chat_data.user_id}): {user_message[:50]}...")
        
        # Call the service layer
        ai_response = await chat_service.process_chat_message(user_message)
        
        # Return the response from the service directly
        # Ensure the service returns a dict/JSON-serializable object
        # Wrap in JSONResponse if specific headers are needed beyond default FastAPI handling
        return JSONResponse(
            content=ai_response,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions (including those from the service) to be caught by the global handler
        # Or handle specific ones here if needed
        raise http_exc
    except Exception as e:
        # Catch any other unexpected errors in the router layer
        logger.exception(f"Unexpected error in chat router: {e}")
        raise HTTPException(status_code=500, detail="Internal server error processing your request") 