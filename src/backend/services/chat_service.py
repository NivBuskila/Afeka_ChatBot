# src/backend/services/chat_service.py
import logging
import json
import httpx
from typing import Dict, Any
from fastapi import HTTPException

from backend.core import config # For AI_SERVICE_URL

logger = logging.getLogger(__name__)

class ChatService:
    # Consider injecting httpx.AsyncClient if needed for advanced usage (e.g., connection pooling)
    # def __init__(self, http_client: httpx.AsyncClient):
    #     self.http_client = http_client
    
    async def process_chat_message(self, user_message: str) -> Dict[str, Any]:
        """Sends the user message to the AI service and returns the response."""
        
        # Note: Input validation (length, presence) is assumed to be done in the router
        
        ai_service_url = f"{config.AI_SERVICE_URL}/gemini"
        logger.info(f"Forwarding chat message to AI service at {ai_service_url}: {user_message[:50]}...")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client: # Add a timeout
                # Prepare request with explicit encoding
                json_data = json.dumps({"message": user_message}, ensure_ascii=False)
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json; charset=utf-8"
                }
                
                response = await client.post(
                    ai_service_url,
                    content=json_data.encode('utf-8'),
                    headers=headers
                )
                
                logger.info(f"AI service response status: {response.status_code}")
                response.raise_for_status() # Raise exception for 4xx or 5xx status codes
                
                # Try to parse JSON response
                try:
                    response_json = response.json()
                    # Ensure response is returned with correct content type header
                    # The router will handle wrapping this in JSONResponse if needed
                    return response_json 
                except json.JSONDecodeError as json_err:
                    logger.error(f"Error parsing AI service JSON response: {json_err}. Response text: {response.text[:200]}")
                    raise HTTPException(status_code=500, detail="AI service returned invalid format")

        except httpx.RequestError as req_err:
            logger.error(f"Error communicating with AI service at {ai_service_url}: {req_err}")
            raise HTTPException(status_code=503, detail="AI service is currently unavailable")
        except httpx.HTTPStatusError as status_err:
             logger.error(f"AI service returned error status {status_err.response.status_code}: {status_err.response.text[:200]}")
             # You might want to customize the detail based on the status code
             error_detail = f"AI service failed with status {status_err.response.status_code}"
             if status_err.response.status_code == 429: # Example: Pass through rate limit error
                 error_detail = "AI service rate limit exceeded"
             raise HTTPException(status_code=status_err.response.status_code, detail=error_detail)
        except Exception as e:
            logger.exception(f"Unexpected error processing chat message in service: {e}")
            raise HTTPException(status_code=500, detail="Internal error processing chat message")

# Dependency function to get the service instance
# Since there's no state, we can just return a new instance each time for now
def get_chat_service() -> ChatService:
     # If we were injecting httpx.AsyncClient, it would be passed here
     # return ChatService(http_client=...) 
     return ChatService() 