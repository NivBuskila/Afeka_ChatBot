# app/services/chat_service.py
"""Chat service implementation"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from app.services.base import BaseService
from app.repositories.chat_repository import ChatSessionRepository, ChatMessageRepository
from app.repositories.user_repository import UserRepository
from app.domain.chat import ChatSession, ChatMessage
from app.services.ai_service import AIServiceClient
from app.core.exceptions import ServiceException


class ChatService(BaseService):
    """Service for managing chat sessions and messages"""
    
    def __init__(
        self,
        session_repository: ChatSessionRepository,
        message_repository: ChatMessageRepository,
        user_repository: UserRepository,
        ai_service: AIServiceClient
    ):
        super().__init__()
        self.session_repo = session_repository
        self.message_repo = message_repository
        self.user_repo = user_repository
        self.ai_service = ai_service
    
    async def create_session(self, user_id: UUID, title: Optional[str] = None) -> ChatSession:
        """Create a new chat session"""
        try:
            self._log_operation("create_session", f"user_id={user_id}")
            
            # Verify user exists
            user = await self.user_repo.find_by_id(user_id)
            if not user:
                raise ServiceException(f"User {user_id} not found")
            
            # Create session
            session = ChatSession(
                user_id=user_id,
                title=title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                is_active=True
            )
            
            created_session = await self.session_repo.create(session)
            if not created_session:
                raise ServiceException("Failed to create chat session")
            
            return created_session
            
        except Exception as e:
            self._log_error("create_session", e)
            raise ServiceException(f"Failed to create session: {str(e)}")
    
    async def get_user_sessions(
        self, 
        user_id: UUID, 
        active_only: bool = False,
        limit: Optional[int] = None
    ) -> List[ChatSession]:
        """Get chat sessions for a user"""
        try:
            self._log_operation("get_user_sessions", f"user_id={user_id}, active_only={active_only}")
            
            if active_only:
                sessions = await self.session_repo.find_active_sessions(user_id)
            else:
                sessions = await self.session_repo.find_by_user_id(user_id, limit)
            
            # Enrich sessions with message count
            for session in sessions:
                messages = await self.message_repo.find_by_session_id(session.id)
                session.messages = messages
            
            return sessions
            
        except Exception as e:
            self._log_error("get_user_sessions", e)
            return []
    
    async def process_message(
        self,
        session_id: UUID,
        user_id: UUID,
        content: str
    ) -> ChatMessage:
        """Process a user message and get AI response"""
        try:
            self._log_operation("process_message", f"session_id={session_id}")
            
            # Verify session exists and belongs to user
            session = await self.session_repo.find_by_id(session_id)
            if not session:
                raise ServiceException(f"Session {session_id} not found")
            if session.user_id != user_id:
                raise ServiceException("Session does not belong to user")
            
            # Create user message
            user_message = ChatMessage(
                session_id=session_id,
                user_id=user_id,
                content=content,
                role="user"
            )
            
            created_user_message = await self.message_repo.create(user_message)
            if not created_user_message:
                raise ServiceException("Failed to save user message")
            
            # Get conversation history for context
            history = await self.message_repo.find_by_session_id(session_id)
            
            # Get AI response
            ai_response_content = await self.ai_service.get_chat_response(
                message=content,
                conversation_history=history
            )
            
            # Create assistant message
            assistant_message = ChatMessage(
                session_id=session_id,
                user_id=user_id,
                content=ai_response_content,
                role="assistant",
                metadata={"model": "gpt-3.5-turbo"}
            )
            
            created_assistant_message = await self.message_repo.create(assistant_message)
            if not created_assistant_message:
                raise ServiceException("Failed to save assistant message")
            
            # Update session activity
            await self.session_repo.update(
                session_id,
                {"updated_at": datetime.utcnow()}
            )
            
            return created_assistant_message
            
        except Exception as e:
            self._log_error("process_message", e)
            raise ServiceException(f"Failed to process message: {str(e)}")
    
    async def get_session_with_messages(self, session_id: UUID, user_id: UUID) -> Optional[ChatSession]:
        """Get a session with all its messages"""
        try:
            self._log_operation("get_session_with_messages", f"session_id={session_id}")
            
            # Get session
            session = await self.session_repo.find_by_id(session_id)
            if not session:
                return None
            
            # Verify ownership
            if session.user_id != user_id:
                raise ServiceException("Session does not belong to user")
            
            # Get messages
            messages = await self.message_repo.find_by_session_id(session_id)
            session.messages = messages
            
            return session
            
        except Exception as e:
            self._log_error("get_session_with_messages", e)
            return None
    
    async def search_sessions(
        self,
        user_id: UUID,
        search_term: str
    ) -> List[ChatSession]:
        """Search user's chat sessions by content"""
        try:
            self._log_operation("search_sessions", f"user_id={user_id}, term={search_term}")
            
            # Get all user sessions
            sessions = await self.session_repo.find_by_user_id(user_id)
            
            # Search in messages
            matching_sessions = []
            for session in sessions:
                messages = await self.message_repo.find_by_session_id(session.id)
                
                # Check if any message contains search term
                for message in messages:
                    if search_term.lower() in message.content.lower():
                        session.messages = messages
                        matching_sessions.append(session)
                        break
                
                # Also check session title
                if session.title and search_term.lower() in session.title.lower():
                    if session not in matching_sessions:
                        session.messages = messages
                        matching_sessions.append(session)
            
            return matching_sessions
            
        except Exception as e:
            self._log_error("search_sessions", e)
            return []
    
    async def delete_session(self, session_id: UUID, user_id: UUID) -> bool:
        """Delete a chat session and all its messages"""
        try:
            self._log_operation("delete_session", f"session_id={session_id}")
            
            # Verify ownership
            session = await self.session_repo.find_by_id(session_id)
            if not session:
                return False
            if session.user_id != user_id:
                raise ServiceException("Session does not belong to user")
            
            # Delete all messages first
            messages = await self.message_repo.find_by_session_id(session_id)
            for message in messages:
                await self.message_repo.delete(message.id)
            
            # Delete session
            return await self.session_repo.delete(session_id)
            
        except Exception as e:
            self._log_error("delete_session", e)
            return False
