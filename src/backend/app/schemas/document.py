# app/schemas/document.py
"""Document-related API schemas"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import Field, validator
from .base import BaseSchema, TimestampedSchema


class DocumentCreate(BaseSchema):
    """Schema for creating a document"""
    name: str = Field(..., min_length=1, max_length=255)
    type: str
    size: int = Field(..., gt=0)
    url: str
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(default_factory=list)
    
    @validator('tags')
    def validate_tags(cls, v):
        """Ensure tags are unique and not too many"""
        if v:
            # Remove duplicates
            v = list(set(v))
            # Limit number of tags
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "תקנון אקדמי 2024.pdf",
                "type": "application/pdf",
                "size": 1048576,
                "url": "https://storage.example.com/documents/academic_regulations_2024.pdf",
                "category": "regulations",
                "tags": ["תקנון", "אקדמי", "2024"]
            }
        }


class DocumentUpdate(BaseSchema):
    """Schema for updating a document"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    
    @validator('tags')
    def validate_tags(cls, v):
        """Ensure tags are unique and not too many"""
        if v is not None:
            # Remove duplicates
            v = list(set(v))
            # Limit number of tags
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
        return v


class DocumentResponse(TimestampedSchema):
    """Response schema for document"""
    id: int
    name: str
    type: str
    size: int
    url: str
    user_id: Optional[UUID]
    category: Optional[str]
    tags: List[str]
    processing_status: str
    size_mb: float
    is_processed: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "תקנון אקדמי 2024.pdf",
                "type": "application/pdf",
                "size": 1048576,
                "url": "https://storage.example.com/documents/academic_regulations_2024.pdf",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "category": "regulations",
                "tags": ["תקנון", "אקדמי", "2024"],
                "processing_status": "completed",
                "size_mb": 1.0,
                "is_processed": True,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:30:00Z"
            }
        }


class DocumentListResponse(BaseSchema):
    """Response schema for document list"""
    documents: List[DocumentResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "id": 1,
                        "name": "תקנון אקדמי 2024.pdf",
                        "type": "application/pdf",
                        "size": 1048576,
                        "url": "https://storage.example.com/documents/academic_regulations_2024.pdf",
                        "category": "regulations",
                        "tags": ["תקנון", "אקדמי", "2024"],
                        "processing_status": "completed",
                        "size_mb": 1.0,
                        "is_processed": True,
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:30:00Z"
                    }
                ],
                "total": 1
            }
        }
