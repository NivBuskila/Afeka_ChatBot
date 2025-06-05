# app/services/auth_service.py
"""Authentication service implementation"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from app.services.base import BaseService
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.domain.user import User
from supabase import Client


class AuthService(BaseService):
    """Service for authentication-related business logic"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        user_service: UserService,
        supabase_client: Optional[Client] = None
    ):
        super().__init__()
        self.user_repo = user_repository
        self.user_service = user_service
        self.supabase_client = supabase_client
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email and password"""
        self._log_operation("authenticate_user", {"email": email})
        
        try:
            if not self.supabase_client:
                self.logger.error("Supabase client not available")
                return {
                    "success": False,
                    "error": "Authentication service unavailable",
                    "user": None
                }
            
            # Authenticate with Supabase
            auth_response = self.supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Get user from our database
                user = await self.user_service.get_user_by_email(email)
                
                if user:
                    # Update last sign in
                    await self.user_service.update_last_sign_in(user.id)
                    
                    return {
                        "success": True,
                        "user": user,
                        "session": auth_response.session,
                        "is_admin": user.is_admin
                    }
                else:
                    # User authenticated but not in our database
                    self.logger.warning(f"User {email} authenticated but not found in database")
                    
                    return {
                        "success": False,
                        "error": "User not found in system",
                        "user": None
                    }
            else:
                return {
                    "success": False,
                    "error": "Invalid credentials",
                    "user": None
                }
                
        except Exception as e:
            self._log_error("authenticate_user", e)
            return {
                "success": False,
                "error": str(e),
                "user": None
            }
    
    async def validate_session(self, session_token: str) -> Optional[User]:
        """Validate session token and return user"""
        self._log_operation("validate_session")
        
        try:
            if not self.supabase_client:
                self.logger.error("Supabase client not available")
                return None
            
            # Get user from session
            user_response = self.supabase_client.auth.get_user(session_token)
            
            if user_response and user_response.user:
                # Get user from our database
                user = await self.user_service.get_user_by_id(
                    UUID(user_response.user.id)
                )
                
                return user
            
            return None
            
        except Exception as e:
            self._log_error("validate_session", e)
            return None
    
    async def check_user_permissions(
        self,
        user_id: UUID,
        required_role: Optional[str] = None,
        required_permissions: Optional[List[str]] = None
    ) -> bool:
        """Check if user has required role or permissions"""
        self._log_operation("check_user_permissions", {
            "user_id": str(user_id),
            "required_role": required_role,
            "required_permissions": required_permissions
        })
        
        try:
            user = await self.user_service.get_user_by_id(user_id)
            
            if not user or not user.is_active:
                return False
            
            # Check role
            if required_role and user.role != required_role:
                return False
            
            # TODO: Implement permission checking when Admin model is used
            # For now, admins have all permissions
            if required_permissions and user.role != "admin":
                return False
            
            return True
            
        except Exception as e:
            self._log_error("check_user_permissions", e)
            return False