import logging
import json
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse

from ...core.interfaces import IChatService
from ...domain.models import ChatRequest
from ...api.deps import get_chat_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat"])

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
            logger.info(f"Raw request body (first 100 chars): {body_str[:100]}...")
            
            body = json.loads(body_str)
            # Validate with Pydantic
            chat_data = ChatRequest(**body)
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
            chat_data.user_id
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