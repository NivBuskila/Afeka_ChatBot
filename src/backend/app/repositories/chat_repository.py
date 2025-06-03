# app/repositories/chat_repository.py
"""Chat-related repository implementations"""

from typing import Optional, List
from uuid import UUID
from .base import BaseRepository
from app.domain.chat import ChatSession, ChatMessage

class ChatSessionRepository(BaseRepository[ChatSession]):
    """Repository for ChatSession entities"""
    
    @property
    def table_name(self) -> str:
        return "chat_sessions"
    
    @property
    def model_class(self) -> type[ChatSession]:
        return ChatSession
    
    async def find_by_user_id(self, user_id: UUID, limit: Optional[int] = None) -> List[ChatSession]:
        """Find chat sessions by user ID, ordered by most recent"""
        if not self._check_connection():
            return []
            
        try:
            query = self.supabase_client.table(self.table_name).select("*").eq("user_id", user_id).order("updated_at", desc=True)
            
            if limit:
                query = query.limit(limit)
                
            response = query.execute()
            data = self._handle_supabase_response(response, f"find_by_user_id({user_id})")
            
            if data:
                return [self.model_class(**item) for item in data]
            return []
            
        except Exception as e:
            self.logger.error(f"Error finding sessions for user {user_id}: {e}")
            return []
    
    async def find_active_sessions(self, user_id: UUID) -> List[ChatSession]:
        """Find active chat sessions for a user"""
        if not self._check_connection():
            return []
            
        try:
            response = self.supabase_client.table(self.table_name).select("*").eq("user_id", user_id).eq("is_active", True).order("updated_at", desc=True).execute()
            data = self._handle_supabase_response(response, f"find_active_sessions({user_id})")
            
            if data:
                return [self.model_class(**item) for item in data]
            return []
            
        except Exception as e:
            self.logger.error(f"Error finding active sessions for user {user_id}: {e}")
            return []
    
    async def deactivate_session(self, session_id: UUID) -> Optional[ChatSession]:
        """Deactivate a chat session"""
        return await self.update(session_id, {"is_active": False})

class ChatMessageRepository(BaseRepository[ChatMessage]):
    """Repository for ChatMessage entities"""
    
    @property
    def table_name(self) -> str:
        return "messages"
    
    @property
    def model_class(self) -> type[ChatMessage]:
        return ChatMessage
    
    async def find_by_session_id(self, session_id: UUID) -> List[ChatMessage]:
        """Find messages by session ID, ordered chronologically"""
        if not self._check_connection():
            return []
            
        try:
            response = self.supabase_client.table(self.table_name).select("*").eq("session_id", session_id).order("created_at", desc=False).execute()
            data = self._handle_supabase_response(response, f"find_by_session_id({session_id})")
            
            if data:
                return [self.model_class(**item) for item in data]
            return []
            
        except Exception as e:
            self.logger.error(f"Error finding messages for session {session_id}: {e}")
            return []
    
    async def find_by_user_id(self, user_id: UUID, limit: Optional[int] = None) -> List[ChatMessage]:
        """Find messages by user ID"""
        if not self._check_connection():
            return []
            
        try:
            query = self.supabase_client.table(self.table_name).select("*").eq("user_id", user_id).order("created_at", desc=True)
            
            if limit:
                query = query.limit(limit)
                
            response = query.execute()
            data = self._handle_supabase_response(response, f"find_by_user_id({user_id})")
            
            if data:
                return [self.model_class(**item) for item in data]
            return []
            
        except Exception as e:
            self.logger.error(f"Error finding messages for user {user_id}: {e}")
            return []