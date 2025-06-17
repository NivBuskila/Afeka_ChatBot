import logging
import time
import json
import random
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from .interfaces import IMessageRepository
from ..core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

def is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False

class SupabaseMessageRepository(IMessageRepository):
    """Supabase implementation of message repository."""
    
    def __init__(self, client=None):
        if client:
            self.supabase = client
        else:
            from ..core.database import get_supabase_client
            self.supabase = get_supabase_client()
        self.table_name = "messages"
        logger.debug(f"💬 MessageRepository initialized with table: {self.table_name}")
    
    async def create_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new message"""
        logger.debug(f"Creating message for conversation: {data.get('conversation_id', 'unknown')}")
        
        # Check if conversation_id is valid UUID
        conversation_id = data.get('conversation_id')
        if conversation_id and not is_valid_uuid(conversation_id):
            logger.error(f"Conversation ID {conversation_id} is not a valid UUID, returning mock response")
            mock_id = f"mock-invalid-uuid-{int(time.time())}"
            return {
                "id": mock_id,
                "conversation_id": conversation_id,
                "created_at": datetime.now().isoformat(),
                "error": "Invalid conversation ID format"
            }
        
        try:
            # Check if messages table exists - minimal check
            test_query = self.supabase.table(self.table_name).select("count").limit(1).execute()
            
            # Proceed with normal insert
            result = self.supabase.table(self.table_name).insert(data).execute()
            
            if result.data and len(result.data) > 0:
                logger.debug(f"✅ Created message with ID: {result.data[0].get('id') or result.data[0].get('message_id')}")
                return result.data[0]
            else:
                # Return a mock response if no data returned but no error
                mock_id = data.get('id', f"mock-{int(time.time())}")
                mock_response = {
                    "id": mock_id,
                    "conversation_id": data.get('conversation_id', 'unknown'),
                    "created_at": data.get('created_at', datetime.now().isoformat()),
                    "message_text": data.get('message_text', '')
                }
                logger.debug(f"🎭 Returning mock message response with ID: {mock_id}")
                return mock_response
                
        except Exception as e:
            logger.error(f"❌ Error creating message: {e}")
            # Return a mock response on error to prevent app crash
            mock_id = f"mock-{int(time.time())}"
            return {
                "id": mock_id,
                "created_at": datetime.now().isoformat(),
                "error": str(e)
            }

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new message - backward compatibility"""
        return await self.create_message(data)
    
    async def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation"""
        logger.debug(f"Fetching messages for conversation: {conversation_id}")
        
        # Check if conversation_id is valid UUID
        if not is_valid_uuid(conversation_id):
            logger.error(f"Conversation ID {conversation_id} is not a valid UUID, returning empty list")
            return []
        
        try:
            # Check if messages table exists - minimal check
            test_query = self.supabase.table(self.table_name).select("count").limit(1).execute()
            
            # Execute the actual query
            result = self.supabase.table(self.table_name).select("*").eq("conversation_id", conversation_id).order("created_at").execute()
            
            if result.data:
                logger.debug(f"📊 Found {len(result.data)} messages for conversation: {conversation_id}")
                return result.data
            else:
                logger.debug(f"No messages found for conversation: {conversation_id}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching messages: {e}")
            return []

    async def get_by_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation - backward compatibility"""
        return await self.get_messages(conversation_id)
    
    async def update_message(self, message_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a message"""
        logger.debug(f"Updating message with ID: {message_id}")
        
        try:
            result = self.supabase.table(self.table_name).update(data).eq("id", message_id).execute()
            if result.data and len(result.data) > 0:
                logger.debug(f"✅ Successfully updated message: {message_id}")
                return result.data[0]
            else:
                raise ValueError(f"Message {message_id} not found or update failed")
        except Exception as e:
            logger.error(f"❌ Error updating message: {e}")
            raise

    async def update(self, message_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a message - backward compatibility"""
        return await self.update_message(message_id, data)
    
    async def delete_message(self, message_id: str) -> bool:
        """Delete a message"""
        logger.debug(f"Deleting message with ID: {message_id}")
        
        try:
            result = self.supabase.table(self.table_name).delete().eq("id", message_id).execute()
            logger.debug(f"✅ Successfully deleted message: {message_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting message: {e}")
            return False

    async def delete(self, message_id: str) -> bool:
        """Delete a message - backward compatibility"""
        return await self.delete_message(message_id)
    
    async def get_message_schema(self) -> List[str]:
        """Get message table schema (column names)"""
        logger.debug("Fetching message table schema")
        
        try:
            # Get a single message to determine schema
            result = self.supabase.table(self.table_name).select("*").limit(1).execute()
            
            if result.data and len(result.data) > 0:
                # Return the column names from the first row
                return list(result.data[0].keys())
            else:
                # Return a default schema if no messages exist
                return ["id", "conversation_id", "user_id", "message_text", "created_at"]
                
        except Exception as e:
            logger.error(f"❌ Error fetching schema: {e}")
            # Return basic schema on error
            return ["id", "conversation_id", "user_id", "message_text", "created_at"]

    async def get_schema(self) -> Dict[str, Any]:
        """Get the message table schema - backward compatibility"""
        columns = await self.get_message_schema()
        return {"columns": columns}
    
    def _clean_data_for_insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and prepare data for insertion or update."""
        cleaned_data = {}
        
        # Remove None values and empty strings
        for key, value in data.items():
            if value is not None and value != "" and key != "":
                # Convert JSON fields if needed
                if key in ['request_payload', 'response_payload', 'metadata'] and isinstance(value, dict):
                    try:
                        cleaned_data[key] = json.dumps(value)
                    except Exception as e:
                        logger.warning(f"Could not serialize JSON field {key}: {e}")
                        # Use original value if conversion fails
                        cleaned_data[key] = str(value)
                else:
                    cleaned_data[key] = value
        
        # Ensure IDs are strings
        if 'conversation_id' in cleaned_data and not isinstance(cleaned_data['conversation_id'], str):
            cleaned_data['conversation_id'] = str(cleaned_data['conversation_id'])
            
        if 'user_id' in cleaned_data and not isinstance(cleaned_data['user_id'], str):
            cleaned_data['user_id'] = str(cleaned_data['user_id'])
            
        return cleaned_data

    async def create_or_update_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a message with custom ID (used by PUT endpoint)"""
        logger.debug(f"Creating/updating message with data: {str(data)[:200]}...")
        
        # Check if conversation_id is valid UUID
        conversation_id = data.get('conversation_id')
        if conversation_id and not is_valid_uuid(conversation_id):
            logger.error(f"Conversation ID {conversation_id} is not a valid UUID, returning mock response")
            mock_response = {
                "id": f"mock-invalid-uuid-{int(time.time())}",
                "conversation_id": conversation_id,
                "user_id": data.get('user_id', ''),
                "content": data.get('content', ''),
                "role": data.get('role', 'user'),
                "created_at": datetime.now().isoformat(),
                "error": "Invalid conversation ID format"
            }
            return mock_response
        
        try:
            # Clean the data first
            cleaned_data = self._clean_data_for_insert(data)
            
            # Generate ID if not provided
            if 'id' not in cleaned_data and 'message_id' not in cleaned_data:
                cleaned_data['id'] = f"msg-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
            
            # Ensure created_at is set
            if 'created_at' not in cleaned_data:
                cleaned_data['created_at'] = datetime.now().isoformat()
            
            logger.debug(f"Cleaned data for insert: {str(cleaned_data)[:200]}...")
            
            # Try to insert/upsert the message
            result = self.supabase.table(self.table_name).upsert(cleaned_data).execute()
            
            if result.data and len(result.data) > 0:
                logger.debug(f"✅ Created/updated message with ID: {result.data[0].get('id')}")
                return result.data[0]
            else:
                # Return fallback response
                fallback_response = {
                    "id": cleaned_data.get('id', f"fallback-{int(time.time())}"),
                    "conversation_id": cleaned_data.get('conversation_id', ''),
                    "user_id": cleaned_data.get('user_id', ''),
                    "content": cleaned_data.get('content', ''),
                    "role": cleaned_data.get('role', 'user'),
                    "created_at": cleaned_data.get('created_at', datetime.now().isoformat())
                }
                logger.debug(f"No data returned, using fallback: {fallback_response}")
                return fallback_response
                
        except Exception as e:
            logger.error(f"❌ Error creating/updating message: {e}")
            # Return mock response to prevent crash
            mock_response = {
                "id": f"error-{int(time.time())}",
                "conversation_id": data.get('conversation_id', ''),
                "user_id": data.get('user_id', ''),
                "content": data.get('content', ''),
                "role": data.get('role', 'user'),
                "created_at": datetime.now().isoformat(),
                "error": str(e)
            }
            return mock_response