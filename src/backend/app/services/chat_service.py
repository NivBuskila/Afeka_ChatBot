import logging
import json
import httpx
from typing import Dict, Any
from fastapi import HTTPException

from ..core.interfaces import IChatService
from ..config.settings import settings

logger = logging.getLogger(__name__)

class ChatService(IChatService):
    """Implementation of chat service interface."""
    
    async def process_chat_message(self, user_message: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """Process a chat message and return a response from the AI service."""
        
        # Validate message length
        if len(user_message) > settings.MAX_CHAT_MESSAGE_LENGTH:
            raise HTTPException(
                status_code=400, 
                detail=f"Message too long (max {settings.MAX_CHAT_MESSAGE_LENGTH} characters)"
            )
        
        logger.info(f"Processing chat request (user: {user_id}): {user_message[:50]}...")
        
        try:
            # Call AI service
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Prepare request with explicit encoding
                json_data = json.dumps({"message": user_message}, ensure_ascii=False)
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json; charset=utf-8"
                }
                
                response = await client.post(
                    f"{settings.AI_SERVICE_URL}/chat",
                    content=json_data.encode('utf-8'),
                    headers=headers
                )
                
                logger.info(f"AI service response status: {response.status_code}")
                response.raise_for_status()  # Raise for HTTP error status
                
                # Parse the response
                try:
                    return response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing AI service response: {e}. Response text: {response.text[:200]}")
                    raise HTTPException(status_code=500, detail="AI service returned invalid response format")
                
        except httpx.RequestError as e:
            logger.error(f"Error communicating with AI service: {e}")
            # Fallback response when AI service is unavailable
            return {
                "message": "This is a placeholder response. The AI service is currently unavailable."
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"AI service returned error status {e.response.status_code}: {e.response.text[:200]}")
            # Determine appropriate status code to return
            status_code = e.response.status_code if e.response.status_code != 500 else 503
            detail = "AI service is currently unavailable" if status_code == 503 else "AI service error"
            raise HTTPException(status_code=status_code, detail=detail)
        except Exception as e:
            logger.exception(f"Unexpected error in chat service: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")