import logging
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from ..core.interfaces import IChatSessionService
from ..repositories.interfaces import IChatSessionRepository
from ..core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

class ChatSessionService(IChatSessionService):
    """Service for chat session management."""
    
    def __init__(self, repository: IChatSessionRepository):
        """Initialize with a repository implementation."""
        self.repository = repository
    
    async def create_session(self, user_id: str, title: str) -> Dict[str, Any]:
        """Create a new chat session."""
        return await self.repository.create_session(user_id, title)
    
    async def get_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user."""
        return await self.repository.get_sessions(user_id)
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chat session with its messages."""
        return await self.repository.get_session(session_id)
    
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a chat session."""
        return await self.repository.update_session(session_id, data)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        return await self.repository.delete_session(session_id)
    
    async def search_sessions(self, user_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search for chat sessions matching a term."""
        return await self.repository.search_sessions(user_id, search_term)