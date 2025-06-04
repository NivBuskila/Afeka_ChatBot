# app/schemas/chat_message.py
"""Enhanced chat message schemas with full business logic support"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from uuid import UUID
from pydantic import Field, validator
from .base import BaseSchema, TimestampedSchema
from .pagination import PaginatedResponse

class ChatMessageCreate(BaseSchema):
    """Schema for creating a new chat message"""
    session_id: UUID = Field(..., description="ID of the chat session")
    user_id: UUID = Field(..., description="ID of the message sender")
    content: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Message content"
    )
    role: Literal["user", "assistant", "system"] = Field(
        default="user",
        description="Role of the message sender"
    )
    parent_message_id: Optional[UUID] = Field(
        None,
        description="ID of the parent message for threading"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional message metadata"
    )
    
    @validator('content')
    def validate_content(cls, v):
        """Ensure content is meaningful"""
        if not v.strip():
            raise ValueError('Message content cannot be empty or whitespace')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "content": "מה השעות קבלה של המזכירות?",
                "role": "user",
                "metadata": {
                    "client_timestamp": "2024-01-01T12:00:00Z",
                    "user_agent": "Mozilla/5.0..."
                }
            }
        }

class ChatMessageUpdate(BaseSchema):
    """Schema for updating a chat message"""
    content: Optional[str] = Field(
        None,
        min_length=1,
        max_length=4000,
        description="Updated message content"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated message metadata"
    )
    is_edited: Optional[bool] = Field(
        None,
        description="Mark message as edited"
    )
    
    @validator('content')
    def validate_content(cls, v):
        """Ensure content is meaningful if provided"""
        if v is not None and not v.strip():
            raise ValueError('Message content cannot be empty or whitespace')
        return v.strip() if v else None
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "מה השעות הקבלה המעודכנות של המזכירות?",
                "is_edited": True,
                "metadata": {
                    "edit_reason": "clarification",
                    "edited_at": "2024-01-01T12:05:00Z"
                }
            }
        }

class ChatMessageResponse(TimestampedSchema):
    """Response schema for chat message"""
    id: UUID = Field(..., description="Unique message identifier")
    session_id: UUID = Field(..., description="ID of the parent session")
    user_id: UUID = Field(..., description="ID of the message sender")
    content: str = Field(..., description="Message content")
    role: Literal["user", "assistant", "system"] = Field(
        ...,
        description="Role of the message sender"
    )
    parent_message_id: Optional[UUID] = Field(
        None,
        description="ID of the parent message for threading"
    )
    is_edited: bool = Field(default=False, description="Whether message was edited")
    edit_count: int = Field(default=0, description="Number of times edited")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Message metadata"
    )
    
    # AI-specific fields
    ai_model: Optional[str] = Field(None, description="AI model used (for assistant messages)")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    confidence_score: Optional[float] = Field(None, description="AI confidence score")
    
    @property
    def is_from_ai(self) -> bool:
        """Check if message is from AI assistant"""
        return self.role == "assistant"
    
    @property
    def is_from_user(self) -> bool:
        """Check if message is from user"""
        return self.role == "user"
    
    @property
    def content_preview(self) -> str:
        """Get a preview of the message content (first 100 chars)"""
        if len(self.content) <= 100:
            return self.content
        return self.content[:97] + "..."
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "content": "מה השעות קבלה של המזכירות?",
                "role": "user",
                "parent_message_id": None,
                "is_edited": False,
                "edit_count": 0,
                "metadata": {
                    "client_timestamp": "2024-01-01T12:00:00Z"
                },
                "ai_model": None,
                "tokens_used": None,
                "processing_time_ms": None,
                "confidence_score": None,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": None
            }
        }

class ChatMessageSummary(BaseSchema):
    """Lightweight summary of a chat message"""
    id: UUID
    content_preview: str
    role: Literal["user", "assistant", "system"]
    created_at: datetime
    is_edited: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "content_preview": "מה השעות קבלה של המזכירות?",
                "role": "user",
                "created_at": "2024-01-01T12:00:00Z",
                "is_edited": False
            }
        }

class ChatMessageListResponse(BaseSchema):
    """Response schema for chat message list"""
    messages: List[ChatMessageResponse] = Field(
        ...,
        description="List of chat messages"
    )
    total: int = Field(..., description="Total number of messages")
    user_message_count: int = Field(default=0, description="Number of user messages")
    assistant_message_count: int = Field(default=0, description="Number of assistant messages")
    
    @validator('user_message_count', always=True)
    def calculate_user_messages(cls, v, values):
        """Calculate user messages count"""
        messages = values.get('messages', [])
        return len([m for m in messages if m.role == "user"])
    
    @validator('assistant_message_count', always=True)
    def calculate_assistant_messages(cls, v, values):
        """Calculate assistant messages count"""
        messages = values.get('messages', [])
        return len([m for m in messages if m.role == "assistant"])
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174002",
                        "session_id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174001",
                        "content": "מה השעות קבלה של המזכירות?",
                        "role": "user",
                        "created_at": "2024-01-01T12:00:00Z"
                    }
                ],
                "total": 1,
                "user_message_count": 1,
                "assistant_message_count": 0
            }
        }

class ChatMessageThread(BaseSchema):
    """Schema for message threading"""
    root_message: ChatMessageResponse = Field(..., description="Root message of the thread")
    replies: List[ChatMessageResponse] = Field(
        default_factory=list,
        description="Reply messages in the thread"
    )
    total_replies: int = Field(default=0, description="Total number of replies")
    
    @validator('total_replies', always=True)
    def calculate_replies(cls, v, values):
        """Calculate total replies"""
        replies = values.get('replies', [])
        return len(replies)
    
    class Config:
        json_schema_extra = {
            "example": {
                "root_message": {
                    "id": "123e4567-e89b-12d3-a456-426614174002",
                    "session_id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_id": "123e4567-e89b-12d3-a456-426614174001",
                    "content": "מה השעות קבלה של המזכירות?",
                    "role": "user",
                    "created_at": "2024-01-01T12:00:00Z"
                },
                "replies": [],
                "total_replies": 0
            }
        }

class ChatMessageSearch(BaseSchema):
    """Schema for message search parameters"""
    query: str = Field(..., min_length=1, description="Search query")
    session_id: Optional[UUID] = Field(None, description="Limit search to specific session")
    role: Optional[Literal["user", "assistant", "system"]] = Field(
        None,
        description="Filter by message role"
    )
    date_from: Optional[datetime] = Field(None, description="Search from date")
    date_to: Optional[datetime] = Field(None, description="Search to date")
    
    @validator('query')
    def validate_query(cls, v):
        """Validate search query"""
        if not v.strip():
            raise ValueError('Search query cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Search query must be at least 2 characters')
        return v.strip()
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        """Ensure date range is valid"""
        date_from = values.get('date_from')
        if date_from and v and v <= date_from:
            raise ValueError('date_to must be after date_from')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "שעות קבלה",
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "user",
                "date_from": "2024-01-01T00:00:00Z",
                "date_to": "2024-01-31T23:59:59Z"
            }
        }

# Pagination support
ChatMessagePaginatedResponse = PaginatedResponse[ChatMessageResponse]