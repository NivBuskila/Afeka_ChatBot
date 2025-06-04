from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import Field
from app.schemas.base import BaseSchema, TimestampedSchema
from app.domain.chat import ChatSession

class ChatSessionCreate(BaseSchema):
    """Schema for creating a chat session"""
    user_id: UUID
    title: Optional[str] = Field(None, max_length=200)

class ChatSessionUpdate(BaseSchema):
    """Schema for updating a chat session"""
    title: Optional[str] = Field(None, max_length=200)

class ChatSessionResponse(TimestampedSchema):
    """Response schema for chat session"""
    id: str
    user_id: UUID
    title: str
    is_active: bool
    message_count: int = 0
    
    @classmethod
    def from_domain(cls, session: ChatSession) -> "ChatSessionResponse":
        """Convert domain model to response schema"""
        return cls(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            is_active=session.is_active,
            created_at=session.created_at,
            updated_at=session.updated_at
        )

class ChatSessionListResponse(BaseSchema):
    """Response schema for chat session list"""
    sessions: List[ChatSessionResponse]
    total: int