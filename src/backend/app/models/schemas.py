from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date

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

class ApiKey(BaseModel):
    id: Optional[int] = None
    key_name: str
    api_key: str
    provider: str = "gemini"
    is_active: bool = True
    daily_limit_tokens: int = 1000000
    daily_limit_requests: int = 1500
    minute_limit_requests: int = 15
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ApiKeyUsage(BaseModel):
    id: Optional[int] = None
    api_key_id: int
    usage_date: date
    usage_minute: datetime
    tokens_used: int = 0
    requests_count: int = 0
    created_at: Optional[datetime] = None

