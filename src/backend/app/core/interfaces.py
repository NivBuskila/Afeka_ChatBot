from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class IChatService(ABC):
    """Interface for chat services."""
    
    @abstractmethod
    async def process_chat_message(self, user_message: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """Process a chat message and return an AI response."""
        pass

class IDocumentService(ABC):
    """Interface for document services."""
    
    @abstractmethod
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents."""
        pass
    
    @abstractmethod
    async def get_document_by_id(self, doc_id: int) -> Dict[str, Any]:
        """Get a document by its ID."""
        pass
    
    @abstractmethod
    async def create_document(self, document) -> Dict[str, Any]:
        """Create a new document."""
        pass

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

class IChatSessionService(ABC):
    """Interface for chat session services."""
    
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
        """Get a specific chat session with its messages."""
        pass
    
    @abstractmethod
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a chat session."""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete a chat session."""
        pass
    
    @abstractmethod
    async def search_sessions(self, user_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search for chat sessions matching a term."""
        pass


class IMessageService(ABC):
    """Interface for message services."""
    
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
    async def delete_message(self, message_id: str) -> Dict[str, Any]:
        """Delete a message."""
        pass
    
    @abstractmethod
    async def get_message_schema(self) -> Dict[str, Any]:
        """Get message table schema (column names)."""
        pass