# app/services/ai_service.py
"""AI service client for clean HTTP communication with src/ai service"""

import httpx
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from app.services.base import BaseService
from app.domain.chat import ChatMessage
from app.config import settings
from app.core.exceptions import ServiceException


class AIServiceClient(BaseService):
    """Clean HTTP client for AI service communication"""
    
    def __init__(self):
        super().__init__()
        self.ai_config = settings.ai_service_config
        self._health_status: Optional[bool] = None
        self._last_health_check: Optional[datetime] = None
        
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        payload: Optional[Dict[str, Any]] = None,
        timeout_override: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to AI service with retry logic"""
        
        timeout = timeout_override or self.ai_config.timeout
        
        for attempt in range(self.ai_config.max_retries + 1):
            try:
                self._log_operation(
                    f"{method.upper()} {endpoint}", 
                    f"attempt={attempt + 1}, timeout={timeout}s"
                )
                
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(
                        connect=self.ai_config.connection_timeout,
                        read=self.ai_config.read_timeout,
                        pool=None,
                        timeout=timeout
                    )
                ) as client:
                    
                    if method.upper() == "GET":
                        response = await client.get(endpoint)
                    else:
                        headers = {
                            "Content-Type": "application/json; charset=utf-8",
                            "Accept": "application/json; charset=utf-8"
                        }
                        
                        if payload:
                            content = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                        else:
                            content = None
                            
                        response = await client.post(endpoint, content=content, headers=headers)
                    
                    # Check response status
                    if response.status_code == 200:
                        try:
                            return response.json()
                        except json.JSONDecodeError as e:
                            raise ServiceException(f"Invalid JSON response from AI service: {e}")
                    
                    elif response.status_code == 503:
                        raise ServiceException("AI service temporarily unavailable")
                    
                    else:
                        error_detail = ""
                        try:
                            error_data = response.json()
                            error_detail = error_data.get("error", error_data.get("message", ""))
                        except:
                            error_detail = response.text[:200]
                        
                        raise ServiceException(
                            f"AI service returned {response.status_code}: {error_detail}"
                        )
                        
            except httpx.ConnectError as e:
                self._log_error(f"Connection error on attempt {attempt + 1}", e)
                if attempt == self.ai_config.max_retries:
                    raise ServiceException("Unable to connect to AI service")
                    
            except httpx.TimeoutException as e:
                self._log_error(f"Timeout on attempt {attempt + 1}", e)
                if attempt == self.ai_config.max_retries:
                    raise ServiceException("AI service request timed out")
                    
            except httpx.RequestError as e:
                self._log_error(f"Request error on attempt {attempt + 1}", e)
                if attempt == self.ai_config.max_retries:
                    raise ServiceException(f"AI service request failed: {str(e)}")
                    
            except ServiceException:
                # Don't retry ServiceExceptions (4xx, 5xx status codes)
                raise
                
            except Exception as e:
                self._log_error(f"Unexpected error on attempt {attempt + 1}", e)
                if attempt == self.ai_config.max_retries:
                    raise ServiceException(f"Unexpected error calling AI service: {str(e)}")
            
            # Wait before retry (exponential backoff)
            if attempt < self.ai_config.max_retries:
                delay = self.ai_config.retry_delay * (2 ** attempt)
                self.logger.info(f"Retrying in {delay:.1f} seconds...")
                await asyncio.sleep(delay)
        
        raise ServiceException("Max retries exceeded for AI service")

    # ========================
    # CHAT METHODS
    # ========================
    
    async def chat_with_rag(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        conversation_history: Optional[List[ChatMessage]] = None,
        use_rag: bool = True
    ) -> Dict[str, Any]:
        """Send message with simple conversation context to AI service"""
        
        # ✅ SIMPLE: Build basic context
        context_messages = []
        if conversation_history:
            context_messages = self._build_simple_context(conversation_history)
        
        payload = {
            "message": message,
            "use_rag": use_rag,
            "context": context_messages
        }
        
        try:
            result = await self._make_request("POST", self.ai_config.chat_endpoint, payload)
            
            return {
                "response": result.get("result", "No response received"),
                "processing_time": result.get("processing_time", 0),
                "rag_used": result.get("rag_used", False),
                "context_messages": result.get("context_messages", 0)
            }
            
        except ServiceException as e:
            self._log_error("chat_with_rag", e)
            return {
                "response": self._get_fallback_response(),
                "processing_time": 0,
                "rag_used": False,
                "error": str(e)
            }

    def _build_simple_context(self, history: List[ChatMessage]) -> List[Dict[str, str]]:
        """Build simple context from conversation history"""
        
        if not history:
            return []
        
        context_messages = []
        
        # Take last 10 messages
        recent_history = history[-10:] if len(history) > 10 else history
        
        for message in recent_history:
            if message.content and message.content.strip():
                context_messages.append({
                    "role": message.role,
                    "content": message.content.strip()
                })
        
        return context_messages

    async def get_chat_response(
        self,
        message: str,
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> str:
        """Legacy method for backward compatibility"""
        
        # For now, we don't send conversation history to AI service
        # The AI service should handle session management internally
        result = await self.chat_with_rag(message)
        return result["response"]

    # ========================
    # RAG SEARCH METHODS  
    # ========================
    
    async def semantic_search(
        self, 
        query: str, 
        limit: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search using AI service"""
        
        self._log_operation("semantic_search", f"query_length={len(query)}")
        
        payload = {"query": query}
        
        # Only add parameters if explicitly provided - let AI service use its defaults
        if limit is not None:
            payload["limit"] = limit
        if threshold is not None:
            payload["threshold"] = threshold
            
        try:
            result = await self._make_request("POST", self.ai_config.search_endpoint, payload)
            return result.get("results", [])
            
        except ServiceException as e:
            self._log_error("semantic_search", e)
            return []

    async def hybrid_search(
        self, 
        query: str, 
        limit: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search using AI service"""
        
        self._log_operation("hybrid_search", f"query_length={len(query)}")
        
        payload = {"query": query}
        
        # Only add parameters if explicitly provided
        if limit is not None:
            payload["limit"] = limit
        if threshold is not None:
            payload["threshold"] = threshold
            
        try:
            result = await self._make_request("POST", self.ai_config.hybrid_search_endpoint, payload)
            return result.get("results", [])
            
        except ServiceException as e:
            self._log_error("hybrid_search", e)
            return []

    async def enhanced_search(
        self, 
        query: str, 
        max_results: Optional[int] = None,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """Perform enhanced RAG search using AI service"""
        
        self._log_operation("enhanced_search", f"query_length={len(query)}")
        
        payload = {
            "query": query,
            "include_context": include_context
                }
                
        # Only add max_results if explicitly provided
        if max_results is not None:
            payload["max_results"] = max_results
            
        try:
            return await self._make_request("POST", self.ai_config.enhanced_search_endpoint, payload)
            
        except ServiceException as e:
            self._log_error("enhanced_search", e)
            return {
                "answer": "Search service temporarily unavailable",
                "sources": [],
                "query": query,
                "error": str(e)
            }

    # ========================
    # DOCUMENT METHODS
    # ========================
    
    async def reprocess_document(self, document_id: int) -> Dict[str, Any]:
        """Trigger document reprocessing in AI service"""
        
        self._log_operation("reprocess_document", f"document_id={document_id}")
        
        endpoint = self.ai_config.document_reprocess_endpoint(document_id)
        
        try:
            return await self._make_request("POST", endpoint)
            
        except ServiceException as e:
            self._log_error("reprocess_document", e)
            return {
                "success": False,
                "document_id": document_id,
                "error": str(e)
            }

    async def get_document_status(self, document_id: int) -> Dict[str, Any]:
        """Get document processing status from AI service"""
        
        self._log_operation("get_document_status", f"document_id={document_id}")
        
        endpoint = self.ai_config.document_status_endpoint(document_id)
        
        try:
            return await self._make_request("GET", endpoint)
            
        except ServiceException as e:
            self._log_error("get_document_status", e)
            return {
                "document": {"id": document_id, "status": "unknown"},
                "error": str(e)
            }

    # ========================
    # STATS & HEALTH METHODS
    # ========================
    
    async def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics from AI service"""
        
        self._log_operation("get_rag_stats")
        
        try:
            return await self._make_request("GET", self.ai_config.stats_endpoint)
            
        except ServiceException as e:
            self._log_error("get_rag_stats", e)
            return {
                "error": str(e),
                "status": "unavailable"
            }

    async def health_check(self) -> Dict[str, Any]:
        """Check AI service health"""
        
        try:
            result = await self._make_request("GET", self.ai_config.health_endpoint, timeout_override=5)
            
            self._health_status = True
            self._last_health_check = datetime.now()
            
            return {
                "status": "healthy",
                "service": result.get("service", "ai-service"),
                "rag_support": result.get("rag_support", False),
                "timestamp": self._last_health_check.isoformat()
            }
            
        except Exception as e:
            self._health_status = False
            self._last_health_check = datetime.now()
            
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": self._last_health_check.isoformat()
            }

    # ========================
    # UTILITY METHODS
    # ========================
    
    def _get_fallback_response(self) -> str:
        """Get fallback response when AI service is unavailable"""
        return (
            "מצטער, השירות זמנית לא זמין. אנא נסה שוב מאוחר יותר. "
            "I apologize, but the service is temporarily unavailable. Please try again later."
        )

    @property
    def is_healthy(self) -> bool:
        """Check if AI service was healthy in last check"""
        return self._health_status is True

    @property
    def last_health_check(self) -> Optional[datetime]:
        """Get timestamp of last health check"""
        return self._last_health_check


# Legacy alias for backward compatibility
AIService = AIServiceClient
