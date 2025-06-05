# app/schemas/user.py
"""User-related API schemas"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import Field, EmailStr, validator
from .base import BaseSchema, TimestampedSchema


class UserCreate(BaseSchema):
    """Schema for creating a user"""
    email: EmailStr
    name: Optional[str] = None
    role: str = Field(default='user', pattern='^(user|admin)$')
    preferred_language: str = Field(default='he', pattern='^(he|en)$')
    timezone: str = Field(default='Asia/Jerusalem')
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@afeka.ac.il",
                "name": "ישראל ישראלי",
                "role": "user",
                "preferred_language": "he",
                "timezone": "Asia/Jerusalem"
            }
        }


class UserUpdate(BaseSchema):
    """Schema for updating a user"""
    name: Optional[str] = None
    preferred_language: Optional[str] = Field(None, pattern='^(he|en)$')
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(TimestampedSchema):
    """Response schema for user"""
    id: UUID
    email: EmailStr
    name: Optional[str]
    role: str
    is_active: bool
    last_sign_in: Optional[datetime]
    preferred_language: str
    timezone: str
    display_name: str
    is_admin: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "email": "student@afeka.ac.il",
                "name": "ישראל ישראלי",
                "role": "user",
                "is_active": True,
                "last_sign_in": "2024-01-01T12:00:00Z",
                "preferred_language": "he",
                "timezone": "Asia/Jerusalem",
                "display_name": "ישראל ישראלי",
                "is_admin": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }


class AdminCreate(BaseSchema):
    """Schema for creating an admin"""
    user_id: UUID
    department: Optional[str] = Field(None, max_length=100)
    permissions: List[str] = Field(default_factory=lambda: ['read', 'write'])
    
    @validator('permissions')
    def validate_permissions(cls, v):
        """Validate permissions"""
        allowed_permissions = {'read', 'write', 'delete', 'manage_users', 'manage_system'}
        invalid_permissions = set(v) - allowed_permissions
        
        if invalid_permissions:
            raise ValueError(f'Invalid permissions: {", ".join(invalid_permissions)}')
        
        return list(set(v))  # Remove duplicates
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "department": "IT",
                "permissions": ["read", "write", "delete", "manage_users"]
            }
        }


class AdminResponse(TimestampedSchema):
    """Response schema for admin"""
    id: int
    user_id: UUID
    department: Optional[str]
    permissions: List[str]
    user: Optional[UserResponse] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "department": "IT",
                "permissions": ["read", "write", "delete", "manage_users"],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }