# app/services/user_service.py
"""User service implementation"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.services.base import BaseService
from app.repositories.user_repository import UserRepository
from app.domain.user import User
from app.core.exceptions import ServiceException


class UserService(BaseService):
    """Service for managing users"""
    
    def __init__(self, user_repository: UserRepository):
        super().__init__()
        self.user_repo = user_repository
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID"""
        try:
            self._log_operation("get_user", f"id={user_id}")
            return await self.user_repo.find_by_id(user_id)
            
        except Exception as e:
            self._log_error("get_user", e)
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        try:
            self._log_operation("get_user_by_email", email)
            return await self.user_repo.find_by_email(email)
            
        except Exception as e:
            self._log_error("get_user_by_email", e)
            return None
    
    async def create_user(self, user: User) -> User:
        """Create a new user"""
        try:
            self._log_operation("create_user", user.email)
            
            # Check if user already exists
            existing_user = await self.user_repo.find_by_email(user.email)
            if existing_user:
                raise ServiceException(f"User with email {user.email} already exists")
            
            created_user = await self.user_repo.create(user)
            if not created_user:
                raise ServiceException("Failed to create user")
            
            return created_user
            
        except Exception as e:
            self._log_error("create_user", e)
            raise ServiceException(f"Failed to create user: {str(e)}")
    
    async def update_user(
        self,
        user_id: UUID,
        updates: Dict[str, Any]
    ) -> Optional[User]:
        """Update a user"""
        try:
            self._log_operation("update_user", f"id={user_id}")
            
            # Verify user exists
            existing_user = await self.user_repo.find_by_id(user_id)
            if not existing_user:
                raise ServiceException(f"User {user_id} not found")
            
            # Don't allow email updates
            if "email" in updates:
                del updates["email"]
            
            # Add updated timestamp
            updates["updated_at"] = datetime.utcnow()
            
            return await self.user_repo.update(user_id, updates)
            
        except Exception as e:
            self._log_error("update_user", e)
            return None
    
    async def update_last_sign_in(self, user_id: UUID) -> Optional[User]:
        """Update user's last sign in timestamp"""
        try:
            self._log_operation("update_last_sign_in", f"id={user_id}")
            return await self.user_repo.update_last_sign_in(user_id)
            
        except Exception as e:
            self._log_error("update_last_sign_in", e)
            return None
    
    async def get_users_by_role(self, role: str) -> List[User]:
        """Get all users with a specific role"""
        try:
            self._log_operation("get_users_by_role", role)
            return await self.user_repo.find_by_role(role)
            
        except Exception as e:
            self._log_error("get_users_by_role", e)
            return []
    
    async def get_active_users(self) -> List[User]:
        """Get all active users"""
        try:
            self._log_operation("get_active_users")
            return await self.user_repo.find_active_users()
            
        except Exception as e:
            self._log_error("get_active_users", e)
            return []
    
    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate a user"""
        try:
            self._log_operation("deactivate_user", f"id={user_id}")
            
            updated_user = await self.user_repo.update(
                user_id,
                {"is_active": False, "updated_at": datetime.utcnow()}
            )
            
            return updated_user is not None
            
        except Exception as e:
            self._log_error("deactivate_user", e)
            return False
    
    async def activate_user(self, user_id: UUID) -> bool:
        """Activate a user"""
        try:
            self._log_operation("activate_user", f"id={user_id}")
            
            updated_user = await self.user_repo.update(
                user_id,
                {"is_active": True, "updated_at": datetime.utcnow()}
            )
            
            return updated_user is not None
            
        except Exception as e:
            self._log_error("activate_user", e)
            return False
