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
        logger.info("Initialized ChatSessionService")
    
    async def create_session(self, user_id: str, title: str = "New Chat") -> Dict[str, Any]:
        """Create a new chat session."""
        try:
            logger.info(f"Creating chat session for user {user_id} with title: {title}")
            result = await self.repository.create_session(user_id, title)
            return result
        except RepositoryError as e:
            logger.error(f"Repository error in create_session: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in create_session: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")
    
    async def get_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user."""
        try:
            logger.info(f"Getting chat sessions for user: {user_id}")
            result = await self.repository.get_sessions(user_id)
            return result
        except RepositoryError as e:
            logger.error(f"Repository error in get_sessions: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in get_sessions: {e}")
            # Return empty list instead of error to be more resilient
            return []
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get a specific chat session with its messages."""
        try:
            logger.info(f"Getting chat session: {session_id}")
            result = await self.repository.get_session(session_id)
            return result
        except RepositoryError as e:
            logger.error(f"Repository error in get_session: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in get_session: {e}")
            # Return basic session object instead of error
            return {"id": session_id, "messages": []}
    
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a chat session."""
        try:
            logger.info(f"Updating chat session: {session_id}")
            result = await self.repository.update_session(session_id, data)
            return result
        except RepositoryError as e:
            logger.error(f"Repository error in update_session: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in update_session: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update chat session: {str(e)}")
    
    async def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete a chat session."""
        try:
            logger.info(f"Deleting chat session: {session_id}")
            result = await self.repository.delete_session(session_id)
            return {"success": result}
        except RepositoryError as e:
            logger.error(f"Repository error in delete_session: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in delete_session: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete chat session: {str(e)}")
    
    async def search_sessions(self, user_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search for chat sessions matching a term."""
        try:
            logger.info(f"Searching chat sessions for user {user_id} with term: {search_term}")
            result = await self.repository.search_sessions(user_id, search_term)
            return result
        except RepositoryError as e:
            logger.error(f"Repository error in search_sessions: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error in search_sessions: {e}")
            # Return empty list instead of error
            return []