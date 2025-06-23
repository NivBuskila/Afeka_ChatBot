from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

# Ensure ChatMessageHistoryItem is imported from the correct location
from ..domain.models import ChatMessageHistoryItem 

class IChatService(ABC):
    """Interface for chat services."""
    
    @abstractmethod
    async def process_chat_message(
        self, 
        user_message: str, 
        user_id: str = "anonymous",
        history: list[ChatMessageHistoryItem] | None = None # Added history parameter
    ) -> dict[str, object]:
        """Process a chat message and return an AI response."""
        pass
    
    @abstractmethod
    def process_chat_message_stream(
        self, 
        user_message: str, 
        user_id: str = "anonymous",
        history: list[ChatMessageHistoryItem] | None = None
    ) -> AsyncGenerator[dict[str, object], None]:
        """Process a chat message and return streaming AI response chunks."""
        pass

class IDocumentService(ABC):
    """Interface for document services."""
    
    @abstractmethod
    async def get_all_documents(self) -> list[dict[str, object]]:
        """Get all documents."""
        pass
    
    @abstractmethod
    async def get_document_by_id(self, doc_id: int) -> dict[str, object]:
        """Get a document by its ID."""
        pass
    
    @abstractmethod
    async def create_document(self, document: object) -> dict[str, object]:
        """Create a new document."""
        pass

class IDocumentRepository(ABC):
    """Interface for document data repositories."""
    
    @abstractmethod
    async def get_all(self) -> list[dict[str, object]]:
        """Get all documents."""
        pass
    
    @abstractmethod
    async def get_by_id(self, doc_id: int) -> dict[str, object]:
        """Get a document by ID."""
        pass
    
    @abstractmethod
    async def create(self, document: object) -> dict[str, object]:
        """Create a new document."""
        pass

class IChatSessionService(ABC):
    """Interface for chat session services."""
    
    @abstractmethod
    async def create_session(self, user_id: str, title: str = "New Chat") -> dict[str, object]:
        """Create a new chat session."""
        pass
    
    @abstractmethod
    async def get_sessions(self, user_id: str) -> list[dict[str, object]]:
        """Get all chat sessions for a user."""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> dict[str, object]:
        """Get a specific chat session with its messages."""
        pass
    
    @abstractmethod
    async def update_session(self, session_id: str, data: dict[str, object]) -> dict[str, object]:
        """Update a chat session."""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> dict[str, object]:
        """Delete a chat session."""
        pass
    
    @abstractmethod
    async def search_sessions(self, user_id: str, search_term: str) -> list[dict[str, object]]:
        """Search for chat sessions matching a term."""
        pass


class IMessageService(ABC):
    """Interface for message services."""
    
    @abstractmethod
    async def create_message(
        self, 
        user_id: str | None = None, 
        conversation_id: str | None = None, 
        content: str | None = None, 
        is_bot: bool = False, 
        data: dict[str, object] | None = None
    ) -> dict[str, object]:
        """Create a new message - supports both individual parameters and data dict."""
        pass
    
    @abstractmethod
    async def get_messages(self, conversation_id: str) -> list[dict[str, object]]:
        """Get all messages for a conversation."""
        pass
    
    @abstractmethod
    async def update_message(self, message_id: str, data: dict[str, object]) -> dict[str, object]:
        """Update a message."""
        pass
    
    @abstractmethod
    async def delete_message(self, message_id: str) -> dict[str, object]:
        """Delete a message."""
        pass
    
    @abstractmethod
    async def get_schema(self) -> list[str]:
        """Get message table schema (column names)."""
        pass