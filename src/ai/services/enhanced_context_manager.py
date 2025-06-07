"""
Enhanced Context Window Manager for Phase 2
Sophisticated conversation context with RAG integration and memory management
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import tiktoken
import time
import hashlib
from pathlib import Path
import sys
import os

# Add current directory to path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

try:
    from core.database import get_supabase_client
    database_available = True
except ImportError:
    database_available = False

logger = logging.getLogger(__name__)

class AdvancedContextManager:
    """
    Advanced context management with RAG integration and conversation memory
    """
    
    def __init__(self, 
                 max_context_messages: int = 10, 
                 token_limit: int = 4000,
                 rag_context_weight: float = 0.7,
                 conversation_weight: float = 0.3):
        
        self.max_messages = max_context_messages
        self.token_limit = token_limit
        self.rag_weight = rag_context_weight
        self.conversation_weight = conversation_weight
        
        # Initialize tokenizer
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"⚠️ tiktoken not available, using fallback: {e}")
            self.encoding = None
        
        # Initialize database if available
        self.supabase = None
        if database_available:
            try:
                self.supabase = get_supabase_client()
                logger.info("✅ Advanced Context Manager with database support")
            except Exception as e:
                logger.warning(f"⚠️ Database not available for context manager: {e}")
        else:
            logger.info("✅ Advanced Context Manager without database")
        
        # In-memory conversation cache for sessions without database
        self.conversation_cache = {}
        self.cache_ttl = 3600  # 1 hour TTL for memory cache
        
        logger.info(f"Advanced Context Manager initialized - "
                   f"Token limit: {token_limit}, RAG weight: {rag_context_weight}")

    async def build_context_with_rag(self, 
                                   conversation_history: List[Dict],
                                   rag_results: List[Dict],
                                   current_query: str,
                                   session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Build optimized context combining conversation + RAG results with smart prioritization
        """
        try:
            # Get enhanced conversation history if session_id provided
            if session_id:
                enhanced_history = await self._get_session_memory(session_id)
                # Merge with current conversation history
                conversation_history = self._merge_conversation_histories(
                    enhanced_history, conversation_history
                )
            
            # Calculate available tokens for each context type
            total_tokens = self.token_limit
            rag_tokens = int(total_tokens * self.rag_weight)
            conversation_tokens = int(total_tokens * self.conversation_weight)
            
            # Build RAG context with priority
            rag_context = await self._build_rag_context(
                rag_results, current_query, rag_tokens
            )
            
            # Build conversation context with relevance scoring
            conversation_context = await self._build_conversation_context(
                conversation_history, current_query, conversation_tokens
            )
            
            # Calculate actual token usage
            rag_context_tokens = self._count_tokens(rag_context.get('text', ''))
            conversation_context_tokens = self._count_tokens(
                ' '.join([msg.get('content', '') for msg in conversation_context.get('messages', [])])
            )
            
            # Combine contexts intelligently
            combined_context = {
                'rag_context': rag_context,
                'conversation_context': conversation_context,
                'token_usage': {
                    'rag_tokens': rag_context_tokens,
                    'conversation_tokens': conversation_context_tokens,
                    'total_tokens': rag_context_tokens + conversation_context_tokens,
                    'limit': total_tokens,
                    'utilization': round((rag_context_tokens + conversation_context_tokens) / total_tokens * 100, 2)
                },
                'context_quality_score': self._calculate_context_quality(
                    rag_context, conversation_context, current_query
                )
            }
            
            logger.info(f"✅ Built advanced context - "
                       f"RAG: {rag_context_tokens} tokens, "
                       f"Conversation: {conversation_context_tokens} tokens, "
                       f"Quality: {combined_context['context_quality_score']:.2f}")
            
            return combined_context
            
        except Exception as e:
            logger.error(f"❌ Error building advanced context: {e}")
            # Fallback to simple context
            return await self._build_fallback_context(conversation_history, current_query)

    async def _build_rag_context(self, 
                               rag_results: List[Dict], 
                               query: str, 
                               token_limit: int) -> Dict[str, Any]:
        """
        Build RAG context with intelligent prioritization and relevance scoring
        """
        if not rag_results:
            return {
                'text': '',
                'sources': [],
                'relevance_scores': [],
                'tokens_used': 0
            }
        
        # Sort results by relevance/similarity
        sorted_results = sorted(
            rag_results, 
            key=lambda x: x.get('similarity', 0), 
            reverse=True
        )
        
        context_parts = []
        sources = []
        relevance_scores = []
        tokens_used = 0
        
        for i, result in enumerate(sorted_results):
            content = result.get('content', '').strip()
            if not content:
                continue
            
            # Format the context entry
            section_number = result.get('section_number', f'מקור {i+1}')
            context_entry = f"מקור {section_number}: {content}"
            
            # Check token limit
            entry_tokens = self._count_tokens(context_entry)
            if tokens_used + entry_tokens > token_limit:
                # Try to include partial content if space allows
                remaining_tokens = token_limit - tokens_used
                if remaining_tokens > 50:  # Minimum meaningful content
                    partial_content = self._truncate_to_tokens(content, remaining_tokens - 20)
                    context_entry = f"מקור {section_number}: {partial_content}..."
                    context_parts.append(context_entry)
                    tokens_used += self._count_tokens(context_entry)
                break
            
            context_parts.append(context_entry)
            sources.append({
                'section_number': section_number,
                'similarity': result.get('similarity', 0),
                'hierarchical_path': result.get('hierarchical_path', ''),
                'content_preview': content[:150] + "..." if len(content) > 150 else content
            })
            relevance_scores.append(result.get('similarity', 0))
            tokens_used += entry_tokens
        
        return {
            'text': '\n\n'.join(context_parts),
            'sources': sources,
            'relevance_scores': relevance_scores,
            'tokens_used': tokens_used,
            'results_included': len(context_parts),
            'total_results': len(rag_results)
        }

    async def _build_conversation_context(self, 
                                        conversation_history: List[Dict], 
                                        current_query: str, 
                                        token_limit: int) -> Dict[str, Any]:
        """
        Build conversation context with relevance scoring and smart selection
        """
        if not conversation_history:
            return {
                'messages': [],
                'tokens_used': 0,
                'relevance_scores': []
            }
        
        # Score messages by relevance to current query
        scored_messages = []
        for msg in conversation_history[-self.max_messages:]:
            content = msg.get('content', '').strip()
            if not content:
                continue
            
            relevance_score = await self._calculate_message_relevance(content, current_query)
            scored_messages.append({
                'message': msg,
                'relevance_score': relevance_score,
                'tokens': self._count_tokens(content)
            })
        
        # Sort by relevance and recency (recent messages get bonus)
        for i, scored_msg in enumerate(reversed(scored_messages)):
            recency_bonus = (len(scored_messages) - i) / len(scored_messages) * 0.2
            scored_msg['final_score'] = scored_msg['relevance_score'] + recency_bonus
        
        scored_messages.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Select messages within token limit
        selected_messages = []
        relevance_scores = []
        tokens_used = 0
        
        for scored_msg in scored_messages:
            if tokens_used + scored_msg['tokens'] <= token_limit:
                selected_messages.append(scored_msg['message'])
                relevance_scores.append(scored_msg['final_score'])
                tokens_used += scored_msg['tokens']
        
        # Sort selected messages chronologically
        selected_messages.sort(key=lambda x: x.get('timestamp', 0))
        
        return {
            'messages': selected_messages,
            'tokens_used': tokens_used,
            'relevance_scores': relevance_scores,
            'total_messages': len(conversation_history),
            'selected_messages': len(selected_messages)
        }

    async def manage_conversation_memory(self, 
                                       session_id: str,
                                       new_message: Dict,
                                       response: Dict) -> bool:
        """
        Manage long-term conversation memory with relevance scoring
        """
        try:
            # Create conversation entry
            conversation_entry = {
                'session_id': session_id,
                'user_message': new_message,
                'ai_response': response,
                'timestamp': time.time(),
                'relevance_keywords': await self._extract_keywords(new_message.get('content', '')),
                'context_quality': response.get('context_quality_score', 0)
            }
            
            if self.supabase:
                # Store in database
                await self._store_conversation_in_db(conversation_entry)
            else:
                # Store in memory cache
                await self._store_conversation_in_cache(conversation_entry)
            
            logger.debug(f"✅ Stored conversation memory for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error managing conversation memory: {e}")
            return False

    async def _get_session_memory(self, session_id: str) -> List[Dict]:
        """
        Retrieve conversation memory for a session
        """
        try:
            if self.supabase:
                # Get from database
                response = self.supabase.table('conversation_memory')\
                    .select('*')\
                    .eq('session_id', session_id)\
                    .order('timestamp', desc=False)\
                    .limit(self.max_messages * 2)\
                    .execute()
                
                if response.data:
                    conversations = []
                    for entry in response.data:
                        conversations.extend([
                            entry['user_message'],
                            entry['ai_response']
                        ])
                    return conversations
            else:
                # Get from memory cache
                cache_key = f"session_{session_id}"
                if cache_key in self.conversation_cache:
                    cached_data = self.conversation_cache[cache_key]
                    if time.time() - cached_data['timestamp'] < self.cache_ttl:
                        return cached_data['conversations']
                    else:
                        # Expired, remove from cache
                        del self.conversation_cache[cache_key]
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Error retrieving session memory: {e}")
            return []

    async def _calculate_message_relevance(self, message_content: str, current_query: str) -> float:
        """
        Calculate relevance score between message and current query
        """
        try:
            # Simple keyword-based relevance for now
            # In production, could use embedding similarity
            
            message_words = set(message_content.lower().split())
            query_words = set(current_query.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(message_words.intersection(query_words))
            union = len(message_words.union(query_words))
            
            if union == 0:
                return 0.0
            
            return intersection / union
            
        except Exception:
            return 0.0

    def _calculate_context_quality(self, 
                                 rag_context: Dict, 
                                 conversation_context: Dict, 
                                 query: str) -> float:
        """
        Calculate overall context quality score
        """
        try:
            # RAG context quality (based on relevance scores)
            rag_scores = rag_context.get('relevance_scores', [])
            rag_quality = sum(rag_scores) / len(rag_scores) if rag_scores else 0
            
            # Conversation context quality (based on relevance scores)
            conv_scores = conversation_context.get('relevance_scores', [])
            conv_quality = sum(conv_scores) / len(conv_scores) if conv_scores else 0
            
            # Token utilization efficiency
            token_usage = rag_context.get('tokens_used', 0) + conversation_context.get('tokens_used', 0)
            utilization_score = min(token_usage / self.token_limit, 1.0)
            
            # Weighted final score
            final_score = (
                rag_quality * 0.5 + 
                conv_quality * 0.3 + 
                utilization_score * 0.2
            )
            
            return min(final_score, 1.0)
            
        except Exception:
            return 0.5

    # Helper methods
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            if self.encoding:
                return len(self.encoding.encode(text))
            else:
                # Fallback estimate
                return int(len(text.split()) * 1.3)
        except Exception:
            return int(len(text.split()) * 1.3)  # Rough estimate

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit"""
        try:
            if self.encoding:
                tokens = self.encoding.encode(text)
                if len(tokens) <= max_tokens:
                    return text
                
                truncated_tokens = tokens[:max_tokens]
                return self.encoding.decode(truncated_tokens)
            else:
                # Fallback to character-based truncation
                words = text.split()
                if len(words) <= max_tokens:
                    return text
                return ' '.join(words[:max_tokens])
        except Exception:
            # Fallback to character-based truncation
            return text[:max_tokens * 4]

    async def _build_fallback_context(self, conversation_history: List[Dict], query: str) -> Dict[str, Any]:
        """Fallback context building if advanced methods fail"""
        simple_context = []
        total_tokens = 0
        
        for msg in reversed(conversation_history[-5:]):
            content = msg.get('content', '').strip()
            if content and total_tokens < self.token_limit // 2:
                simple_context.insert(0, msg)
                total_tokens += self._count_tokens(content)
        
        return {
            'rag_context': {'text': '', 'sources': [], 'tokens_used': 0},
            'conversation_context': {'messages': simple_context, 'tokens_used': total_tokens},
            'token_usage': {'total_tokens': total_tokens, 'limit': self.token_limit},
            'context_quality_score': 0.5
        }

    # Additional helper methods for database and cache operations
    async def _store_conversation_in_db(self, entry: Dict) -> None:
        """Store conversation in database"""
        try:
            self.supabase.table('conversation_memory').insert({
                'session_id': entry['session_id'],
                'user_message': entry['user_message'],
                'ai_response': entry['ai_response'],
                'timestamp': entry['timestamp'],
                'relevance_keywords': entry['relevance_keywords'],
                'context_quality': entry['context_quality']
            }).execute()
        except Exception as e:
            logger.error(f"❌ Failed to store conversation in DB: {e}")

    async def _store_conversation_in_cache(self, entry: Dict) -> None:
        """Store conversation in memory cache"""
        cache_key = f"session_{entry['session_id']}"
        if cache_key not in self.conversation_cache:
            self.conversation_cache[cache_key] = {
                'conversations': [],
                'timestamp': time.time()
            }
        
        self.conversation_cache[cache_key]['conversations'].extend([
            entry['user_message'],
            entry['ai_response']
        ])
        
        # Keep only recent conversations
        if len(self.conversation_cache[cache_key]['conversations']) > self.max_messages * 2:
            self.conversation_cache[cache_key]['conversations'] = \
                self.conversation_cache[cache_key]['conversations'][-self.max_messages * 2:]

    def _merge_conversation_histories(self, enhanced_history: List[Dict], current_history: List[Dict]) -> List[Dict]:
        """Merge enhanced history with current conversation"""
        # Simple merge - in production could use deduplication
        all_messages = enhanced_history + current_history
        
        # Remove duplicates based on content and timestamp
        seen = set()
        merged = []
        for msg in all_messages:
            key = f"{msg.get('content', '')}_{msg.get('timestamp', 0)}"
            if key not in seen:
                seen.add(key)
                merged.append(msg)
        
        return merged[-self.max_messages:]

    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for relevance scoring"""
        # Simple keyword extraction - in production could use NLP
        words = text.lower().split()
        # Filter out common words and short words
        keywords = [word for word in words if len(word) > 3 and word.isalpha()]
        return keywords[:10]  # Top 10 keywords

    # Backward compatibility methods
    def build_context(self, conversation_history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Simple context building for backward compatibility"""
        if not conversation_history:
            return []
        
        # Take recent messages and format for LLM
        context = []
        total_chars = 0
        max_chars = 8000
        
        # Process messages in reverse order (most recent first)
        for msg in reversed(conversation_history[-self.max_messages:]):
            content = msg.get('content', '').strip()
            role = msg.get('role', 'user')
            
            if not content:
                continue
                
            # Check character limit
            if total_chars + len(content) > max_chars:
                break
                
            context.insert(0, {  # Insert at beginning to maintain order
                "role": role,
                "content": content
            })
            total_chars += len(content)
        
        logger.info(f"Built simple context: {len(context)} messages, {total_chars} chars")
        return context


# Backward compatibility aliases
SimpleContextManager = AdvancedContextManager
