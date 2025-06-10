from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# Models previously defined in main.py
class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"

class ChatResponse(BaseModel):
    response: Dict[str, Any]

class Document(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None 