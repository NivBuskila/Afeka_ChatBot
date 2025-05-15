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
        logger.info("Initialized MessageService")
    
    async def create_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new message."""
        try:
            # Validate required fields
            if 'conversation_id' not in data:
                raise HTTPException(status_code=400, detail="conversation_id is required")
                
            if 'user_id' not in data:
                raise HTTPException(status_code=400, detail="user_id is required")
            
            logger.info(f"Creating message for conversation: {data.get('conversation_id')}")
            result = await self.repository.create_message(data)
            return result
        except RepositoryError as e:
            logger.error(f"Repository error in create_message: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_message: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create message: {str(e)}")
    
    async def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation."""
        try:
            logger.info(f"Getting messages for conversation: {conversation_id}")
            result = await self.repository.get_messages(conversation_id)
            return result
        except RepositoryError as e:
            logger.error(f"Repository error in get_messages: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in get_messages: {e}")
            # Return empty list instead of error
            return []
    
    async def update_message(self, message_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a message."""
        try:
            logger.info(f"Updating message: {message_id}")
            result = await self.repository.update_message(message_id, data)
            return result
        except RepositoryError as e:
            logger.error(f"Repository error in update_message: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in update_message: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update message: {str(e)}")
    
    async def delete_message(self, message_id: str) -> Dict[str, Any]:
        """Delete a message."""
        try:
            logger.info(f"Deleting message: {message_id}")
            result = await self.repository.delete_message(message_id)
            return {"success": result}
        except RepositoryError as e:
            logger.error(f"Repository error in delete_message: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in delete_message: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")
    
    async def get_message_schema(self) -> Dict[str, Any]:
        """Get message table schema (column names)."""
        try:
            logger.info("Getting message schema")
            columns = await self.repository.get_message_schema()
            return {"columns": columns}
        except RepositoryError as e:
            logger.error(f"Repository error in get_message_schema: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in get_message_schema: {e}")
            # Return basic schema instead of error
            return {"columns": ["id", "conversation_id", "user_id", "message", "created_at"]}