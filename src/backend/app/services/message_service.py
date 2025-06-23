import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from ..core.interfaces import IMessageService
from ..repositories.interfaces import IMessageRepository, IChatSessionRepository
from ..core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

class MessageService(IMessageService):
    """Service for message management."""
    
    def __init__(self, repository: IMessageRepository, chat_session_repository: IChatSessionRepository = None):
        """Initialize with a repository implementation."""
        self.repository = repository
        self.chat_session_repository = chat_session_repository
    
    async def create_message(
        self, 
        user_id: str = None, 
        conversation_id: str = None, 
        content: str = None, 
        is_bot: bool = False, 
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new message - supports both individual parameters and data dict."""
        
        if data:
            message_data = data.copy()
        else:
            message_data = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "content": content or "",
                "is_bot": is_bot,
            }
        
        logger.info(f"Creating message for conversation: {message_data.get('conversation_id')} - is_bot: {is_bot}")
        
        cleaned_data = self._clean_message_data(message_data)
        
        result = await self.repository.create_message(cleaned_data)
        
        if result and self.chat_session_repository and message_data.get('conversation_id'):
            try:
                await self.chat_session_repository.update_session(
                    message_data['conversation_id'], 
                    {'updated_at': datetime.utcnow().isoformat() + "Z"}
                )
                logger.info(f"Updated chat session {message_data['conversation_id']} timestamp")
            except Exception as e:
                logger.warning(f"Failed to update chat session timestamp: {e}")
        
        return result
    
    def _clean_message_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize message data for the actual messages table structure."""
        cleaned = {}
        
        cleaned["conversation_id"] = data.get("conversation_id", "")
        cleaned["user_id"] = data.get("user_id", "")
        cleaned["status"] = "completed"
        
        content = data.get("content") or data.get("message_text") or ""
        is_bot = data.get("is_bot", False)
        
        if is_bot:
            cleaned["response"] = content
            cleaned["request"] = None
        else:
            cleaned["request"] = content
            cleaned["response"] = None
        
        now_iso = datetime.utcnow().isoformat() + "Z"
        cleaned["created_at"] = now_iso
        cleaned["status_updated_at"] = now_iso
        
        cleaned["error_message"] = None
        cleaned["request_type"] = "TEXT"
        cleaned["request_payload"] = None
        cleaned["response_payload"] = None
        cleaned["status_code"] = None
        cleaned["processing_start_time"] = None
        cleaned["processing_end_time"] = None
        cleaned["processing_time_ms"] = None
        cleaned["is_sensitive"] = False
        cleaned["metadata"] = {}
        cleaned["chat_session_id"] = data.get("conversation_id")
        
        return cleaned
    
    async def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation."""
        return await self.repository.get_messages(conversation_id)
    
    async def update_message(self, message_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a message."""
        return await self.repository.update_message(message_id, data)
    
    async def delete_message(self, message_id: str) -> bool:
        """Delete a message."""
        return await self.repository.delete_message(message_id)
    
    async def get_schema(self) -> List[str]:
        """Get the message table schema."""
        return await self.repository.get_message_schema()