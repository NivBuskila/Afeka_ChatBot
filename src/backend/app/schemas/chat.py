# app/schemas/chat.py
"""Chat-related API schemas"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import Field, validator
from .base import BaseSchema, TimestampedSchema


class ChatRequest(BaseSchema):
    """Request schema for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=1000)
    user_id: str = Field(default="anonymous")
    
    @validator('message')
    def validate_message(cls, v):
        """Ensure message is not just whitespace"""
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "מה השעות קבלה של המזכירות?",
                "user_id": "user123"
            }
        }


class ChatResponse(BaseSchema):
    """Response schema for chat endpoint"""
    message: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "שעות הקבלה של המזכירות הן בימים א-ה בין 8:00-16:00",
                "metadata": {
                    "confidence": 0.95,
                    "sources": ["student_handbook.pdf"]
                }
            }
        }


class ChatSessionCreate(BaseSchema):
    """Schema for creating a chat session"""
    title: Optional[str] = Field(None, max_length=200)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "שאלות על תקנון אקדמי"
            }
        }


class ChatSessionUpdate(BaseSchema):
    """Schema for updating a chat session"""
    title: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class ChatSessionResponse(TimestampedSchema):
    """Response schema for chat session"""
    id: UUID
    user_id: UUID
    title: Optional[str]
    is_active: bool
    message_count: Optional[int] = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "שאלות על תקנון אקדמי",
                "is_active": True,
                "message_count": 5,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:30:00Z"
            }
        }


class ChatMessageResponse(TimestampedSchema):
    """Response schema for chat message"""
    id: UUID
    session_id: UUID
    user_id: UUID
    content: str
    role: str
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "content": "מה השעות קבלה של המזכירות?",
                "role": "user",
                "metadata": None,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": None
            }
        }
