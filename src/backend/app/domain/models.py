from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class ChatMessageHistoryItem(BaseModel):
    type: str # 'user' or 'bot'
    content: str

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, description="Message cannot be empty")
    user_id: str = "anonymous"
    history: Optional[List[ChatMessageHistoryItem]] = None

class ChatResponse(BaseModel):
    """Chat response model."""
    message: Any

class Document(BaseModel):
    """Document model for creation and updating."""
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class DocumentResponse(BaseModel):
    """Document response model with ID and creation date."""
    id: int
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: str