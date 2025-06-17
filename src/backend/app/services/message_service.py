import logging
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from ..core.interfaces import IMessageService
from ..repositories.interfaces import IMessageRepository
from ..core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

class MessageService(IMessageService):
    """Service for message management."""
    
    def __init__(self, repository: IMessageRepository):
        """Initialize with a repository implementation."""
        self.repository = repository
        logger.debug("💬 MessageService initialized")
    
    async def create_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new message."""
        logger.debug(f"Creating message for conversation: {data.get('conversation_id')}")
        return await self.repository.create_message(data)
    
    async def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation."""
        logger.debug(f"Getting messages for conversation: {conversation_id}")
        return await self.repository.get_messages(conversation_id)
    
    async def update_message(self, message_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a message."""
        logger.debug(f"Updating message: {message_id}")
        return await self.repository.update_message(message_id, data)
    
    async def delete_message(self, message_id: str) -> bool:
        """Delete a message."""
        logger.debug(f"Deleting message: {message_id}")
        return await self.repository.delete_message(message_id)
    
    async def get_schema(self) -> List[str]:
        """Get the message table schema."""
        logger.debug("Getting message schema")
        return await self.repository.get_message_schema()