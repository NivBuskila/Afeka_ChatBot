# app/domain/user.py
"""User-related domain models"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID,uuid4
from pydantic import Field, EmailStr, validator
from .base import TimestampedEntity


class User(TimestampedEntity):
    """User domain model"""
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    name: Optional[str] = None
    role: str = Field(default='user', pattern='^(user|admin)$')
    is_active: bool = True
    last_sign_in: Optional[datetime] = None
    preferred_language: str = 'he'
    timezone: str = 'Asia/Jerusalem'
    
    @validator('name')
    def validate_name(cls, v, values):
        """Set default name from email if not provided"""
        if not v and 'email' in values:
            return values['email'].split('@')[0]
        return v
    
    @property
    def display_name(self) -> str:
        """Get display name"""
        return self.name or self.email.split('@')[0]
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == 'admin'


class Admin(TimestampedEntity):
    """Admin domain model"""
    id: int = Field(default=None)
    user_id: UUID
    department: Optional[str] = None
    permissions: List[str] = Field(default_factory=lambda: ['read', 'write'])
    
    @validator('permissions')
    def validate_permissions(cls, v):
        """Validate permissions"""
        allowed_permissions = {'read', 'write', 'delete', 'manage_users', 'manage_system'}
        invalid_permissions = set(v) - allowed_permissions
        
        if invalid_permissions:
            raise ValueError(f'Invalid permissions: {", ".join(invalid_permissions)}')
        
        # Ensure at least read permission
        if 'read' not in v:
            v.append('read')
        
        return list(set(v))  # Remove duplicates