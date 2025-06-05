# app/domain/base.py
"""Base domain models"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class DomainEntity(BaseModel):
    """Base domain entity with common fields"""
    
    class Config:
        # Allow ORM mode for easy conversion from database models
        from_attributes = True
        # Use enum values instead of names
        use_enum_values = True
        # Validate on assignment
        validate_assignment = True
        # Allow population by field name
        populate_by_name = True


class TimestampedEntity(DomainEntity):
    """Base entity with timestamp fields"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None