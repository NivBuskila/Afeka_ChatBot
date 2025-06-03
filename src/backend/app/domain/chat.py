# app/domain/chat.py
"""Chat-related domain models"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import Field, validator
from .base import TimestampedEntity


class ChatSession(TimestampedEntity):
    """Chat session domain model"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    title: Optional[str] = None
    is_active: bool = True
    messages: List['ChatMessage'] = Field(default_factory=list)
    
    @validator('title')
    def validate_title(cls, v):
        """Ensure title is not too long"""
        if v and len(v) > 200:
            raise ValueError('Title must be 200 characters or less')
        return v


class ChatMessage(TimestampedEntity):
    """Chat message domain model"""
    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    user_id: UUID
    content: str
    role: str = Field(..., pattern='^(user|assistant)$')
    metadata: Optional[dict] = None
    
    @validator('content')
    def validate_content(cls, v):
        """Ensure content is not empty and within limits"""
        if not v or not v.strip():
            raise ValueError('Message content cannot be empty')
        if len(v) > 10000:
            raise ValueError('Message content must be 10000 characters or less')
        return v.strip()


# Forward reference update
ChatSession.model_rebuild()