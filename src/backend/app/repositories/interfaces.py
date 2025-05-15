from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class IDocumentRepository(ABC):
    """Interface for document data repositories."""
    
    @abstractmethod
    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all documents."""
        pass
    
    @abstractmethod
    async def get_by_id(self, doc_id: int) -> Dict[str, Any]:
        """Get a document by ID."""
        pass
    
    @abstractmethod
    async def create(self, document) -> Dict[str, Any]:
        """Create a new document."""
        pass

class IChatSessionRepository(ABC):
    """Interface for chat session repositories."""
    
    @abstractmethod
    async def create_session(self, user_id: str, title: str = "New Chat") -> Dict[str, Any]:
        """Create a new chat session."""
        pass
    
    @abstractmethod
    async def get_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user."""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get a specific chat session."""
        pass
    
    @abstractmethod
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a chat session."""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        pass
    
    @abstractmethod
    async def search_sessions(self, user_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search for chat sessions matching a term."""
        pass


class IMessageRepository(ABC):
    """Interface for message repositories."""
    
    @abstractmethod
    async def create_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new message."""
        pass
    
    @abstractmethod
    async def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation."""
        pass
    
    @abstractmethod
    async def update_message(self, message_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a message."""
        pass
    
    @abstractmethod
    async def delete_message(self, message_id: str) -> bool:
        """Delete a message."""
        pass
    
    @abstractmethod
    async def get_message_schema(self) -> List[str]:
        """Get message table schema (column names)."""
        pass