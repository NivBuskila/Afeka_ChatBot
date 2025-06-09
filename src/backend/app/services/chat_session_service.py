import logging
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from ..core.interfaces import IChatSessionService
from ..repositories.interfaces import IChatSessionRepository
from ..core.exceptions import RepositoryError
from ..repositories.chat_session_repo import SupabaseChatSessionRepository

logger = logging.getLogger(__name__)

class ChatSessionService(IChatSessionService):
    """Service for chat session management."""
    
    def __init__(self):
        """Initialize with a repository implementation."""
        self.repository = SupabaseChatSessionRepository()
        logger.debug("💬 ChatSessionService initialized")
    
    async def create_session(self, user_id: str, title: str) -> Dict[str, Any]:
        """Create a new chat session."""
        logger.debug(f"Creating chat session for user {user_id} with title: {title}")
        return await self.repository.create(user_id, title)
    
    async def get_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user."""
        logger.debug(f"Getting chat sessions for user: {user_id}")
        return await self.repository.get_by_user(user_id)
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chat session with its messages."""
        logger.debug(f"Getting chat session: {session_id}")
        return await self.repository.get_by_id(session_id)
    
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a chat session."""
        logger.debug(f"Updating chat session: {session_id}")
        return await self.repository.update(session_id, data)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        logger.debug(f"Deleting chat session: {session_id}")
        return await self.repository.delete(session_id)
    
    async def search_sessions(self, user_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search for chat sessions matching a term."""
        logger.debug(f"Searching chat sessions for user {user_id} with term: {search_term}")
        return await self.repository.search(user_id, search_term)