# app/repositories/user_repository.py
"""User repository implementation"""

from typing import Optional, List
from uuid import UUID
from .base import BaseRepository
from app.domain.user import User

class UserRepository(BaseRepository[User]):
    """Repository for User entities"""
    
    @property
    def table_name(self) -> str:
        return "users"
    
    @property
    def model_class(self) -> type[User]:
        return User
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email address"""
        users = await self.find_by_field("email", email)
        return users[0] if users else None
    
    async def find_by_role(self, role: str) -> List[User]:
        """Find users by role"""
        return await self.find_by_field("role", role)
    
    async def find_active_users(self) -> List[User]:
        """Find all active users"""
        return await self.find_by_field("is_active", True)
    
    async def update_last_sign_in(self, user_id: UUID) -> Optional[User]:
        """Update user's last sign in timestamp"""
        from datetime import datetime
        return await self.update(user_id, {"last_sign_in": datetime.utcnow()})