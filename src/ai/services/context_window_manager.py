"""
Simple Context Manager - Basic conversation context
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SimpleContextManager:
    """Simple context management - just recent messages"""
    
    def __init__(self):
        self.max_messages = 10  # Keep last 10 messages
        self.max_chars = 8000   # Roughly 2000 tokens
        logger.info("Simple Context Manager initialized")

    def build_context(self, conversation_history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Build simple context from conversation history"""
        
        if not conversation_history:
            return []
        
        # Take recent messages and format for LLM
        context = []
        total_chars = 0
        
        # Process messages in reverse order (most recent first)
        for msg in reversed(conversation_history[-self.max_messages:]):
            content = msg.get('content', '').strip()
            role = msg.get('role', 'user')
            
            if not content:
                continue
                
            # Check character limit
            if total_chars + len(content) > self.max_chars:
                break
                
            context.insert(0, {  # Insert at beginning to maintain order
                "role": role,
                "content": content
            })
            total_chars += len(content)
        
        logger.info(f"Built simple context: {len(context)} messages, {total_chars} chars")
        return context 