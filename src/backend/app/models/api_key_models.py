from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

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

