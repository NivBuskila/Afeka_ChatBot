# app/schemas/base.py
"""Base schemas for API DTOs"""

from datetime import datetime
from typing import Optional, TypeVar, Generic
from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    class Config:
        # Allow ORM mode for easy conversion from domain models
        from_attributes = True
        # Use enum values
        use_enum_values = True
        # Validate on assignment
        validate_assignment = True
        # Allow population by field name
        populate_by_name = True
        # Include example values in schema
        json_schema_extra = {}


class TimestampedSchema(BaseSchema):
    """Base schema with timestamp fields"""
    created_at: datetime
    updated_at: Optional[datetime] = None
