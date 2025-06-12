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
        
        ai_service_url = f"{config.AI_SERVICE_URL}/chat"
        
        # 🔍 DEBUG: הוספת לוג מפורט
        logger.info(f"🚀 [CHAT-DEBUG] Starting chat request process")
        logger.info(f"🚀 [CHAT-DEBUG] AI Service URL: {ai_service_url}")
        logger.info(f"🚀 [CHAT-DEBUG] Message length: {len(user_message)} chars")
        logger.info(f"🚀 [CHAT-DEBUG] Message preview: {user_message[:50]}...")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Prepare request with explicit encoding
                json_data = json.dumps({"message": user_message}, ensure_ascii=False)
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json; charset=utf-8"
                }
                
                # 🔍 DEBUG: לוג לפני השליחה
                logger.info(f"🚀 [CHAT-DEBUG] Sending request to AI service...")
                
                response = await client.post(
                    ai_service_url,
                    content=json_data.encode('utf-8'),
                    headers=headers
                )
                
                # 🔍 DEBUG: לוג אחרי קבלת התגובה
                logger.info(f"🚀 [CHAT-DEBUG] AI service response status: {response.status_code}")
                logger.info(f"🚀 [CHAT-DEBUG] Response headers: {dict(response.headers)}")
                
                response.raise_for_status()
                
                try:
                    response_json = response.json()
                    
                    # 🔍 DEBUG: לוג התגובה
                    logger.info(f"🚀 [CHAT-DEBUG] AI service response keys: {list(response_json.keys())}")
                    logger.info(f"🚀 [CHAT-DEBUG] Response preview: {str(response_json)[:100]}...")
                    logger.info(f"🚀 [CHAT-DEBUG] Chat request completed successfully")
                    
                    return response_json 
                except json.JSONDecodeError as json_err:
                    logger.error(f"❌ [CHAT-ERROR] Error parsing AI service JSON response: {json_err}")
                    logger.error(f"❌ [CHAT-ERROR] Raw response text: {response.text[:200]}")
                    raise HTTPException(status_code=500, detail="AI service returned invalid format")

        except httpx.RequestError as req_err:
            logger.error(f"❌ [CHAT-ERROR] Network error communicating with AI service: {req_err}")
            raise HTTPException(status_code=503, detail="AI service is currently unavailable")
        except httpx.HTTPStatusError as status_err:
            logger.error(f"❌ [CHAT-ERROR] AI service returned error status {status_err.response.status_code}")
            logger.error(f"❌ [CHAT-ERROR] Error response: {status_err.response.text[:200]}")
            error_detail = f"AI service failed with status {status_err.response.status_code}"
            if status_err.response.status_code == 429:
                error_detail = "AI service rate limit exceeded"
            raise HTTPException(status_code=status_err.response.status_code, detail=error_detail)
        except Exception as e:
            logger.exception(f"❌ [CHAT-ERROR] Unexpected error processing chat message: {e}")
            raise HTTPException(status_code=500, detail="Internal error processing chat message")

# Dependency function to get the service instance
# Since there's no state, we can just return a new instance each time for now
def get_chat_service() -> ChatService:
     # If we were injecting httpx.AsyncClient, it would be passed here
     # return ChatService(http_client=...) 
     return ChatService() 