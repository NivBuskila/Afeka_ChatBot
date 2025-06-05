# app/domain/document.py
"""Document-related domain models"""

from datetime import datetime
from typing import Optional, List
from pydantic import Field, validator
from uuid import UUID
from .base import TimestampedEntity


class Document(TimestampedEntity):
    """Document domain model"""
    id: int = Field(default=None)
    name: str
    type: str
    size: int
    url: str
    user_id: Optional[UUID] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    processing_status: str = 'pending'
    content: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        """Ensure name is not empty"""
        if not v or not v.strip():
            raise ValueError('Document name cannot be empty')
        return v.strip()
    
    @validator('type')
    def validate_type(cls, v):
        """Validate file type"""
        allowed_types = {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain'
        }
        if v not in allowed_types:
            raise ValueError(f'Invalid file type. Allowed types: {", ".join(allowed_types)}')
        return v
    
    @validator('size')
    def validate_size(cls, v):
        """Validate file size"""
        max_size = 100 * 1024 * 1024  # 100MB
        if v > max_size:
            raise ValueError(f'File size exceeds maximum limit of {max_size / 1024 / 1024}MB')
        if v <= 0:
            raise ValueError('File size must be positive')
        return v
    
    @property
    def size_mb(self) -> float:
        """Get size in megabytes"""
        return self.size / (1024 * 1024)
    
    @property
    def is_processed(self) -> bool:
        """Check if document has been processed"""
        return self.processing_status == 'completed'