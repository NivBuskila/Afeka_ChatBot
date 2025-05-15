from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    user_id: str = "anonymous"

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