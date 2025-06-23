import logging
import time
import json
import random
from datetime import datetime
from typing import Dict, Any, List, Optional

from .interfaces import IMessageRepository
from ..core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

class SupabaseMessageRepository(IMessageRepository):
    """Supabase implementation of message repository."""
    
    def __init__(self, client):
        self.client = client
        self.table_name = "messages"
    
    async def create_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new message"""
        logger.info(f"Creating message for conversation: {data.get('conversation_id', 'unknown')}")
        logger.info(f"Message data keys: {list(data.keys())}")
        logger.info(f"Raw data: {data}")
        
        try:
            insert_data = data.copy()
            logger.info(f"Insert data: {insert_data}")
            
            test_query = self.client.table(self.table_name).select("count").limit(1).execute()
            logger.info(f"Table {self.table_name} test query successful")
            
            logger.info(f"Attempting to insert message with data: {insert_data}")
            result = self.client.table(self.table_name).insert(insert_data).execute()
            
            logger.info(f"Insert result type: {type(result)}")
            logger.info(f"Insert result attributes: {dir(result) if result else 'None'}")
            logger.info(f"Insert result data: {getattr(result, 'data', 'No data attr') if result else 'No result'}")
            logger.info(f"Insert result error: {getattr(result, 'error', 'No error attr') if result else 'No result'}")
            
            if result.data and len(result.data) > 0:
                created_message = result.data[0]
                logger.info(f"Successfully created message with ID: {created_message.get('id') or created_message.get('message_id')}")
                
                return {
                    "id": str(created_message.get('message_id') or created_message.get('id')),
                    "conversation_id": created_message.get('conversation_id'),
                    "user_id": created_message.get('user_id'),
                    "content": created_message.get('request') or created_message.get('response') or "",
                    "role": "bot" if created_message.get('response') else "user",
                    "created_at": created_message.get('created_at')
                }
            else:
                logger.error(f"Insert successful but no data returned. Result: {result}")
                logger.error(f"Result data is: {result.data if hasattr(result, 'data') else 'No data attribute'}")
                logger.error(f"Result error is: {result.error if hasattr(result, 'error') else 'No error attribute'}")
                
                mock_id = f"msg-{int(time.time() * 1000)}"
                mock_response = {
                    "id": mock_id,
                    "conversation_id": data.get('conversation_id', 'unknown'),
                    "created_at": datetime.now().isoformat() + "Z",
                    "content": data.get('request') or data.get('response') or data.get('content', ''),
                    "role": "bot" if data.get('response') else "user",
                    "error": "Insert successful but no data returned"
                }
                logger.warning(f"Returning mock message response with ID: {mock_id}")
                return mock_response
                
        except Exception as e:
            logger.error(f"Error creating message: {e}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error details: {str(e)}")
            logger.error(f"Data that failed: {data}")
            
            mock_id = f"msg-{int(time.time() * 1000)}"
            return {
                "id": mock_id,
                "conversation_id": data.get('conversation_id', 'unknown'),
                "created_at": datetime.now().isoformat() + "Z",
                "content": data.get('request') or data.get('response') or data.get('content', ''),
                "role": "bot" if data.get('response') else "user",
                "error": str(e)
            }
    
    async def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation"""
        try:
            test_query = self.client.table(self.table_name).select("count").limit(1).execute()
            
            result = self.client.table(self.table_name).select("*").eq("conversation_id", conversation_id).order("created_at").execute()
            
            if result.data:
                return result.data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            return []
    
    async def update_message(self, message_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a message"""
        try:
            result = self.client.table(self.table_name).update(data).eq("id", message_id).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            else:
                raise ValueError(f"Message {message_id} not found or update failed")
        except Exception as e:
            logger.error(f"Error updating message: {e}")
            raise
    
    async def delete_message(self, message_id: str) -> bool:
        """Delete a message"""
        try:
            result = self.client.table(self.table_name).delete().eq("id", message_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return False
    
    async def get_message_schema(self) -> List[str]:
        """Get the message table schema"""
        try:
            result = self.client.table(self.table_name).select("*").limit(1).execute()
            
            if result.data and len(result.data) > 0:
                return list(result.data[0].keys())
            else:
                return ["id", "conversation_id", "user_id", "message_text", "created_at"]
                
        except Exception as e:
            logger.error(f"Error fetching schema: {e}")
            return ["id", "conversation_id", "user_id", "message_text", "created_at"]