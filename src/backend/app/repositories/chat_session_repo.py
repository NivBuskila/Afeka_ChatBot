import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import time

from .interfaces import IChatSessionRepository
from ..core.exceptions import RepositoryError
from ..utils.cache import sessions_cache

logger = logging.getLogger(__name__)

class SupabaseChatSessionRepository(IChatSessionRepository):
    """Supabase implementation of chat session repository."""
    
    def __init__(self, client):
        """Initialize with Supabase client."""
        self.client = client
        self.table_name = "chat_sessions"
        logger.info(f"Initialized SupabaseChatSessionRepository with table: {self.table_name}")
    
    async def create_session(self, user_id: str, title: str = "New Chat") -> Dict[str, Any]:
        """Create a new chat session for a user."""
        try:
            logger.info(f"Creating chat session for user: {user_id}")
            current_time = datetime.now().isoformat()
            
            session_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": title,
                "created_at": current_time,
                "updated_at": current_time
            }
            
            response = self.client.table(self.table_name).insert(session_data).execute()
            
            if hasattr(response, 'data') and response.data:
                logger.info(f"Created chat session with ID: {response.data[0].get('id')}")
                
                try:
                    conversation_data = {
                        "conversation_id": response.data[0].get("id"),
                        "user_id": user_id,
                        "title": title,
                        "created_at": current_time,
                        "updated_at": current_time,
                        "is_active": True
                    }
                    self.client.table("conversations").insert(conversation_data).execute()
                except Exception as conv_err:
                    logger.warning(f"Could not create conversation record: {conv_err}")
                
                cache_key = f"sessions:{user_id}"
                sessions_cache.invalidate(cache_key)
                
                return response.data[0]
            else:
                logger.warning("No data returned from chat session creation, returning input data")
                return session_data
                
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            
            session_id = str(uuid.uuid4())
            logger.info(f"Returning mock session with ID: {session_id}")
            
            return {
                "id": session_id,
                "user_id": user_id,
                "title": title,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
    
    async def get_sessions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat sessions for a user with caching and pagination."""
        try:
            cache_key = f"sessions:{user_id}"
            cached_sessions = sessions_cache.get(cache_key)
            if cached_sessions is not None:
                return cached_sessions[:limit]
            
            logger.info(f"[CACHE-MISS] Fetching chat sessions for user: {user_id}")
            
            try:
                self.client.table(self.table_name).select("id").limit(0).execute()
            except Exception as table_err:
                logger.warning(f"Chat sessions table may not exist: {table_err}")
                return []
            
            response = self.client.table(self.table_name)\
                .select("id, user_id, title, created_at, updated_at")\
                .eq("user_id", user_id)\
                .order("updated_at", desc=True)\
                .limit(limit)\
                .execute()
            
            if hasattr(response, 'data') and response.data:
                sessions = response.data
                logger.info(f"Found {len(sessions)} chat sessions for user: {user_id}")
                
                cache_key = f"sessions:{user_id}"
                sessions_cache.set(cache_key, sessions)
                return sessions
            else:
                logger.info(f"No chat sessions found for user: {user_id}")
                cache_key = f"sessions:{user_id}"
                sessions_cache.set(cache_key, [])
                return []
                
        except Exception as e:
            logger.error(f"Error fetching chat sessions: {e}")
            return []
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get a specific chat session."""
        try:
            logger.info(f"Fetching chat session with ID: {session_id}")
            
            try:
                test_query = self.client.table(self.table_name).select("count").limit(1).execute()
            except Exception as table_err:
                logger.warning(f"Chat sessions table may not exist: {table_err}")
                return {"id": session_id, "messages": []}
            
            session_result = self.client.table(self.table_name).select("*").eq("id", session_id).single().execute()
            
            if not hasattr(session_result, 'data') or not session_result.data:
                logger.warning(f"Chat session with ID {session_id} not found")
                return {"id": session_id, "messages": []}
            
            try:
                logger.info(f"Searching for messages with conversation_id: {session_id}")
                messages_result = self.client.table("messages").select("*").eq("conversation_id", session_id).order("created_at").execute()
                raw_messages = messages_result.data if hasattr(messages_result, 'data') else []
                
                logger.info(f"Found {len(raw_messages)} raw messages in database")
                if len(raw_messages) > 0:
                    logger.info(f"First message sample: {raw_messages[0]}")
                
                formatted_messages = []
                for i, msg in enumerate(raw_messages):
                    logger.info(f"Processing message {i+1}: message_id={msg.get('message_id')}, request={bool(msg.get('request'))}, response={bool(msg.get('response'))}")
                    
                    if msg.get('request') and not msg.get('response'):
                        formatted_msg = {
                            'id': msg.get('message_id', msg.get('id', f'msg-{i}')),
                            'content': msg.get('request'),
                            'role': 'user',
                            'is_bot': False,
                            'created_at': msg.get('created_at'),
                            'conversation_id': session_id,
                            'user_id': msg.get('user_id'),
                            'message_text': msg.get('request'),
                            'text': msg.get('request')
                        }
                        formatted_messages.append(formatted_msg)
                        logger.info(f"Added user message: {formatted_msg['id']} - '{formatted_msg['content'][:50]}...'")
                    
                    elif msg.get('response') and not msg.get('request'):
                        formatted_msg = {
                            'id': msg.get('message_id', msg.get('id', f'msg-{i}')),
                            'content': msg.get('response'),
                            'role': 'bot',
                            'is_bot': True,
                            'created_at': msg.get('created_at'),
                            'conversation_id': session_id,
                            'user_id': msg.get('user_id'),
                            'message_text': msg.get('response'),
                            'text': msg.get('response')
                        }
                        formatted_messages.append(formatted_msg)
                        logger.info(f"Added bot message: {formatted_msg['id']} - '{formatted_msg['content'][:50]}...'")
                    
                    elif msg.get('request') and msg.get('response'):
                        user_msg = {
                            'id': f"{msg.get('message_id', msg.get('id', f'msg-{i}'))}-user",
                            'content': msg.get('request'),
                            'role': 'user',
                            'is_bot': False,
                            'created_at': msg.get('created_at'),
                            'conversation_id': session_id,
                            'user_id': msg.get('user_id'),
                            'message_text': msg.get('request'),
                            'text': msg.get('request')
                        }
                        formatted_messages.append(user_msg)
                        
                        bot_msg = {
                            'id': f"{msg.get('message_id', msg.get('id', f'msg-{i}'))}-bot",
                            'content': msg.get('response'),
                            'role': 'bot',
                            'is_bot': True,
                            'created_at': msg.get('created_at'),
                            'conversation_id': session_id,
                            'user_id': msg.get('user_id'),
                            'message_text': msg.get('response'),
                            'text': msg.get('response')
                        }
                        formatted_messages.append(bot_msg)
                        logger.info(f"Added legacy message pair: user and bot")
                
                formatted_messages.sort(key=lambda x: x.get('created_at', ''))
                
                logger.info(f"Final formatted messages count: {len(formatted_messages)}")
                
            except Exception as msg_err:
                logger.warning(f"Messages table may not exist or error fetching messages: {msg_err}")
                formatted_messages = []
                
            result = {
                **session_result.data,
                "messages": formatted_messages
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching chat session {session_id}: {e}")
            return {"id": session_id, "messages": []}
    
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a chat session."""
        try:
            logger.info(f"Updating chat session with ID: {session_id}")
            
            if 'updated_at' not in data:
                data['updated_at'] = datetime.now().isoformat()
                
            result = self.client.table(self.table_name).update(data).eq("id", session_id).execute()
            
            try:
                conversation_update = {
                    'updated_at': data.get('updated_at'),
                    'last_message_at': data.get('updated_at')
                }
                if 'title' in data:
                    conversation_update['title'] = data['title']
                    
                self.client.table("conversations").update(conversation_update).eq("conversation_id", session_id).execute()
            except Exception as conv_err:
                logger.warning(f"Error updating conversation: {conv_err}")
            
            if hasattr(result, 'data') and result.data:
                logger.info(f"Successfully updated chat session: {session_id}")
                return {"success": True, "data": result.data}
            else:
                logger.warning(f"Update may have failed for session: {session_id}")
                return {"success": True, "data": None}
                
        except Exception as e:
            logger.error(f"Error updating chat session {session_id}: {e}")
            raise RepositoryError(f"Failed to update chat session: {e}", status_code=500)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        try:
            logger.info(f"Deleting chat session with ID: {session_id}")
            
            try:
                self.client.table("messages").delete().eq("conversation_id", session_id).execute()
                logger.info(f"Deleted messages for session: {session_id}")
            except Exception as msg_err:
                logger.warning(f"Error deleting messages: {msg_err}")
            
            try:
                self.client.table("conversations").delete().eq("conversation_id", session_id).execute()
                logger.info(f"Deleted conversation record for session: {session_id}")
            except Exception as conv_err:
                logger.warning(f"Error deleting conversation: {conv_err}")
            
            result = self.client.table(self.table_name).delete().eq("id", session_id).execute()
            
            logger.info(f"Successfully deleted chat session: {session_id}")
            return True
                
        except Exception as e:
            logger.error(f"Error deleting chat session {session_id}: {e}")
            raise RepositoryError(f"Failed to delete chat session: {e}", status_code=500)
            
    async def search_sessions(self, user_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search for chat sessions matching a term."""
        try:
            logger.info(f"Searching chat sessions for user {user_id} with term: {search_term}")
            
            title_result = self.client.table(self.table_name).select("*").eq("user_id", user_id).ilike("title", f"%{search_term}%").execute()
            title_matches = title_result.data if hasattr(title_result, 'data') else []
            
            try:
                message_result = self.client.table("messages").select("conversation_id").eq("user_id", user_id).or_(f"request.ilike.%{search_term}%,response.ilike.%{search_term}%").execute()
                message_matches = message_result.data if hasattr(message_result, 'data') else []
                
                session_ids = list(set([msg.get("conversation_id") for msg in message_matches if msg.get("conversation_id")]))
                
                content_match_sessions = []
                if session_ids:
                    content_result = self.client.table(self.table_name).select("*").eq("user_id", user_id).in_("id", session_ids).execute()
                    content_match_sessions = content_result.data if hasattr(content_result, 'data') else []
            except Exception as msg_err:
                logger.warning(f"Error searching messages: {msg_err}")
                content_match_sessions = []
            
            all_sessions = title_matches + content_match_sessions
            
            unique_sessions = {}
            for session in all_sessions:
                if session.get("id") not in unique_sessions:
                    unique_sessions[session.get("id")] = session
            
            result = list(unique_sessions.values())
            result.sort(key=lambda x: x.get("updated_at", x.get("created_at", "")), reverse=True)
            
            logger.info(f"Found {len(result)} chat sessions matching '{search_term}' for user {user_id}")
            return result
                
        except Exception as e:
            logger.error(f"Error searching chat sessions: {e}")
            return []