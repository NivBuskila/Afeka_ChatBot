# app/services/ai_service.py
"""AI service for chat interactions"""

import httpx
import json
from typing import List, Dict, Any, Optional
from app.services.base import BaseService
from app.domain.chat import ChatMessage
from app.config import settings
from app.core.exceptions import ServiceException


class AIService(BaseService):
    """Service for AI/LLM interactions"""
    
    def __init__(self):
        super().__init__()
        self.ai_service_url = settings.ai_service_url
        self.timeout = 30.0
    
    async def get_chat_response(
        self,
        message: str,
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> str:
        """Get AI response for a chat message"""
        try:
            self._log_operation("get_chat_response", f"message_length={len(message)}")
            
            # Prepare context from conversation history
            context = self._prepare_context(conversation_history)
            
            # Call AI service
            async with httpx.AsyncClient() as client:
                payload = {
                    "message": message,
                    "context": context
                }
                
                response = await client.post(
                    f"{self.ai_service_url}/chat",
                    content=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                    headers={
                        "Content-Type": "application/json; charset=utf-8",
                        "Accept": "application/json; charset=utf-8"
                    },
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    raise ServiceException(f"AI service returned status {response.status_code}")
                
                response_data = response.json()
                ai_response = (
                    response_data.get("result") or
                    response_data.get("response") or
                    response_data.get("answer") or
                    "I'm sorry, I couldn't process your request."
                )
                
                return ai_response
                
        except httpx.RequestError as e:
            self._log_error("get_chat_response", e)
            # Return fallback response
            return self._get_fallback_response()
        except Exception as e:
            self._log_error("get_chat_response", e)
            raise ServiceException(f"Failed to get AI response: {str(e)}")
    
    def _prepare_context(self, conversation_history: Optional[List[ChatMessage]]) -> List[Dict[str, str]]:
        """Prepare conversation context for AI"""
        if not conversation_history:
            return []
        
        # Take last 10 messages for context
        recent_messages = conversation_history[-10:]
        
        context = []
        for msg in recent_messages:
            context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return context
    
    def _get_fallback_response(self) -> str:
        """Get fallback response when AI service is unavailable"""
        return (
            "I apologize, but I'm currently unable to process your request. "
            "This is a placeholder response. In the future, I'll use RAG "
            "to query the document knowledge base and provide relevant information."
        )
    
    async def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """Analyze a document and extract key information"""
        try:
            self._log_operation("analyze_document", f"text_length={len(document_text)}")
            
            # TODO: Implement document analysis
            # - Extract entities
            # - Generate summary
            # - Extract key points
            
            return {
                "summary": "Document analysis not yet implemented",
                "entities": [],
                "key_points": []
            }
            
        except Exception as e:
            self._log_error("analyze_document", e)
            raise ServiceException(f"Failed to analyze document: {str(e)}")
