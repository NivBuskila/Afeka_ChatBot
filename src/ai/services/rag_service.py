import os
import asyncio
import logging
import time
import re
from typing import List, Dict, Any, Optional, Tuple
import json
import hashlib
from functools import lru_cache
from datetime import datetime, timedelta

import google.generativeai as genai
from supabase import create_client, Client
import numpy as np

try:
    from ..config.current_profile import get_current_profile
    from ..config.rag_config_profiles import get_profile
    from ..config.rag_config import (
        rag_config,
        get_search_config,
        get_embedding_config,
        get_context_config,
        get_llm_config,
        get_database_config,
        get_performance_config
    )
except ImportError:
    from src.ai.config.current_profile import get_current_profile
    from src.ai.config.rag_config_profiles import get_profile
    from src.ai.config.rag_config import (
        rag_config,
        get_search_config,
        get_embedding_config,
        get_context_config,
        get_llm_config,
        get_database_config,
        get_performance_config
    )

try:
    from ..core.database_key_manager import DatabaseKeyManager
except ImportError:
    from src.ai.core.database_key_manager import DatabaseKeyManager

logger = logging.getLogger(__name__)

class RAGService:
    # Class-level cache for embeddings (shared across instances)
    _embedding_cache = {}
    _cache_ttl = 300  # 5 minutes TTL
    
    def __init__(self, config_profile: Optional[str] = None):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        )
        
        # Replace with Database Key Manager with direct Supabase connection
        self.key_manager = DatabaseKeyManager(use_direct_supabase=True)
        logger.info("🔑 RAG Service using Database Key Manager with direct Supabase connection")
        
        # Load profile from central system
        if config_profile is None:
            try:
                config_profile = get_current_profile()
                logger.info(f"Loaded central profile: {config_profile}")
            except Exception as e:
                logger.warning(f"Central profile system not found: {e}, using manual profile selection")
        
        # Load settings by profile or default
        if config_profile:
            try:
                profile_config = get_profile(config_profile)
                self.search_config = profile_config.search
                self.embedding_config = profile_config.embedding
                self.context_config = profile_config.context
                self.llm_config = profile_config.llm
                self.db_config = profile_config.database
                self.performance_config = profile_config.performance
                logger.info(f"Using config profile: {config_profile}")
            except Exception as e:
                logger.warning(f"Failed to load profile '{config_profile}': {e}. Using default config.")
                # Fallback to default settings
                self.search_config = get_search_config()
                self.embedding_config = get_embedding_config()
                self.context_config = get_context_config()
                self.llm_config = get_llm_config()
                self.db_config = get_database_config()
                self.performance_config = get_performance_config()
        else:
            # Get settings from new config
            self.search_config = get_search_config()
            self.embedding_config = get_embedding_config()
            self.context_config = get_context_config()
            self.llm_config = get_llm_config()
            self.db_config = get_database_config()
            self.performance_config = get_performance_config()
        
        # Configure Key Manager - keys will be loaded when first needed in ensure_available_key()
        # Note: Keys will be loaded when first needed in ensure_available_key()
        logger.info("Database Key Manager configured - keys will be loaded on first use")
        
        # Create Gemini model - fallback to environment
        # Try to get key from environment first (safe init approach)
        fallback_key = os.getenv("GEMINI_API_KEY")
        if fallback_key:
            genai.configure(api_key=fallback_key)
            logger.info("Using GEMINI_API_KEY from environment for initialization")
        else:
            # Try to use Key Manager for initialization
            try:
                if self.key_manager:
                    # Just configure with environment key for now, database keys will be loaded lazily
                    logger.info("Database Key Manager configured - will use environment key for init")
                    # Will switch to database keys when needed
                else:
                    raise Exception("No API keys available from Database or environment")
            except Exception as e:
                logger.error(f"Key initialization failed: {e}")
                raise Exception("No API keys available")
        
        # Create Gemini model with settings from config
        self.model = genai.GenerativeModel(
            self.llm_config.MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                temperature=self.llm_config.TEMPERATURE,
                max_output_tokens=self.llm_config.MAX_OUTPUT_TOKENS
            )
        )
        
        logger.info(f"RAG Service initialized with profile '{config_profile or 'default'}' - "
                   f"Similarity threshold: {self.search_config.SIMILARITY_THRESHOLD}, "
                   f"Max chunks: {self.search_config.MAX_CHUNKS_RETRIEVED}, "
                   f"Model: {self.llm_config.MODEL_NAME}")
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: dict) -> bool:
        """Check if cache entry is still valid"""
        return (datetime.now() - cache_entry['timestamp']).seconds < self._cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[float]]:
        """Get embedding from cache if valid"""
        if cache_key in self._embedding_cache:
            entry = self._embedding_cache[cache_key]
            if self._is_cache_valid(entry):
                logger.info(f"Using cached embedding for key: {cache_key[:8]}")
                return entry['embedding']
            else:
                # Remove expired cache entry
                del self._embedding_cache[cache_key]
        return None
    
    def _cache_embedding(self, cache_key: str, embedding: List[float]):
        """Cache embedding with timestamp"""
        self._embedding_cache[cache_key] = {
            'embedding': embedding,
            'timestamp': datetime.now()
        }
        # Clean old cache entries (keep max 1000 entries)
        if len(self._embedding_cache) > 1000:
            # Remove oldest 100 entries
            sorted_items = sorted(self._embedding_cache.items(), key=lambda x: x[1]['timestamp'])
            for key, _ in sorted_items[:100]:
                del self._embedding_cache[key]

    async def _track_embedding_usage(self, text: str, key_id: int = None):
        """Track token usage for embedding generation"""
        # Estimate tokens for embedding (much smaller than generation)
        estimated_tokens = len(text) // 8  # Embeddings use fewer tokens
        logger.info(f"Estimated {estimated_tokens} tokens for embedding")
        
        # FIX: Actually track usage with key manager
        try:
            if self.key_manager and key_id:
                await self.key_manager.record_usage(key_id, estimated_tokens, 1)
                logger.info(f"Successfully tracked {estimated_tokens} tokens for key {key_id}")
            else:
                logger.warning("No key_id provided or key_manager not available")
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")

    async def _track_generation_usage(self, prompt: str, response: str, key_id: int = None):
        """Track token usage for text generation"""
        input_tokens = len(prompt) // 4
        output_tokens = len(response) // 4
        total_tokens = input_tokens + output_tokens
        logger.info(f"Estimated {total_tokens} tokens ({input_tokens} input + {output_tokens} output)")
        
        # FIX: Actually track usage with key manager
        try:
            if self.key_manager and key_id:
                await self.key_manager.record_usage(key_id, total_tokens, 1)
                logger.info(f"Successfully tracked {total_tokens} tokens for key {key_id}")
            else:
                logger.warning("No key_id provided or key_manager not available")
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Create embedding for query with caching"""
        cache_key = self._get_cache_key(query)
        
        # Check cache first
        cached_embedding = self._get_from_cache(cache_key)
        if cached_embedding:
            return cached_embedding
        
        try:
            # Ensure we're using current key if Key Manager available
            key_id = None
            if self.key_manager:
                available_key = await self.key_manager.get_available_key()
                if not available_key:
                    raise Exception("No available API keys for embedding")
                
                # Configure with the available key
                genai.configure(api_key=available_key['api_key'])
                key_id = available_key.get('id')
                logger.info(f"Using key {available_key.get('key_name', 'unknown')} for embedding")
            
            # Generate embedding
            start_time = time.time()
            embedding_model = genai.embed_content(
                model=self.embedding_config.MODEL_NAME,
                content=query,
                task_type=self.embedding_config.TASK_TYPE_QUERY
            )
            
            embedding = embedding_model['embedding']
            generation_time = int((time.time() - start_time) * 1000)
            
            # Cache the result
            self._cache_embedding(cache_key, embedding)
            
            # Track usage
            await self._track_embedding_usage(query, key_id)
            
            logger.info(f"Embedding generated in {generation_time}ms (cached for future use)")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    async def semantic_search(
        self, 
        query: str, 
        document_id: Optional[int] = None,
        max_results: int = None
    ) -> List[Dict[str, Any]]:
        """Semantic search in documents"""
        start_time = time.time()
        
        try:
            # Create embedding for the query
            query_embedding = await self.generate_query_embedding(query)
            
            # Perform search using RPC
            max_results = max_results or self.search_config.MAX_CHUNKS_RETRIEVED
            
            response = self.supabase.rpc(self.db_config.SEMANTIC_SEARCH_FUNCTION, {
                'query_embedding': query_embedding,
                'match_threshold': self.search_config.SIMILARITY_THRESHOLD,
                'match_count': max_results,
                'target_document_id': document_id
            }).execute()
            
            results = response.data or []
            response_time = int((time.time() - start_time) * 1000)
            
            # Log analytics
            if self.performance_config.LOG_SEARCH_ANALYTICS:
                await self._log_search_analytics(
                    query, 
                    'semantic', 
                    len(results),
                    results[0]['similarity_score'] if results else 0.0,
                    response_time,
                    document_id=document_id
                )
            
            logger.info(f"Semantic search completed: {len(results)} results in {response_time}ms")
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise
    
    async def hybrid_search(
        self, 
        query: str, 
        document_id: Optional[int] = None,
        semantic_weight: float = None,
        keyword_weight: float = None
    ) -> List[Dict[str, Any]]:
        """Hybrid search (semantic + keyword)"""
        start_time = time.time()
        
        try:
            query_embedding = await self.generate_query_embedding(query)
            
            # Use weights from config if not provided
            semantic_weight = semantic_weight or self.search_config.HYBRID_SEMANTIC_WEIGHT
            keyword_weight = keyword_weight or self.search_config.HYBRID_KEYWORD_WEIGHT
            
            response = self.supabase.rpc(self.db_config.HYBRID_SEARCH_FUNCTION, {
                'query_text': query,
                'query_embedding': query_embedding,
                'match_threshold': self.search_config.SIMILARITY_THRESHOLD,
                'match_count': self.search_config.MAX_CHUNKS_RETRIEVED,
                'target_document_id': document_id,
                'semantic_weight': semantic_weight,
                'keyword_weight': keyword_weight
            }).execute()
            
            results = response.data or []
            response_time = int((time.time() - start_time) * 1000)
            
            if self.performance_config.LOG_SEARCH_ANALYTICS:
                await self._log_search_analytics(
                    query, 
                    'hybrid', 
                    len(results),
                    results[0]['combined_score'] if results else 0.0,
                    response_time,
                    document_id=document_id
                )
            
            logger.info(f"Hybrid search completed: {len(results)} results in {response_time}ms")
            return results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            raise
    
    async def contextual_search(
        self,
        query: str,
        section_filter: Optional[str] = None,
        content_type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Contextual search"""
        try:
            query_embedding = await self.generate_query_embedding(query)
            
            response = self.supabase.rpc(self.db_config.CONTEXTUAL_SEARCH_FUNCTION, {
                'query_embedding': query_embedding,
                'section_filter': section_filter,
                'content_type_filter': content_type_filter,
                'similarity_threshold': self.search_config.SIMILARITY_THRESHOLD,
                'max_results': self.search_config.MAX_RESULTS_EXTENDED
            }).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error in contextual search: {e}")
            raise

    async def section_specific_search(
        self,
        query: str,
        target_section: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Section-specific search"""
        try:
            start_time = time.time()
            
            # Identify section number in the question
            section_patterns = [
                r'סעיף\s+(\d+(?:\.\d+)*)',
                r'בסעיף\s+(\d+(?:\.\d+)*)',
                r'מה\s+(?:אומר|כתוב|נאמר)\s+(?:ב)?סעיף\s+(\d+(?:\.\d+)*)',
                r'(\d+(?:\.\d+)+)(?:\s|$)',  # Section numbers like 1.5.1
            ]
            
            extracted_section = target_section
            if not extracted_section:
                for pattern in section_patterns:
                    match = re.search(pattern, query)
                    if match:
                        extracted_section = match.group(1)
                        logger.info(f"Extracted section number: {extracted_section}")
                        break
            
            if extracted_section:
                # Special search for sections with pattern matching
                query_embedding = await self.generate_query_embedding(query)
                
                response = self.supabase.rpc(self.db_config.SECTION_SEARCH_FUNCTION, {
                    'query_embedding': query_embedding,
                    'section_number': extracted_section,
                    'similarity_threshold': 0.3,  # Lower threshold for section search
                    'max_results': self.search_config.MAX_CHUNKS_FOR_CONTEXT
                }).execute()
                
                section_results = response.data or []
                
                # If no results, perform regular hybrid search
                if not section_results:
                    logger.info(f"No section-specific results found for {extracted_section}, falling back to hybrid search")
                    section_results = await self.hybrid_search(query)
                
                response_time = int((time.time() - start_time) * 1000)
                logger.info(f"Section search completed: {len(section_results)} results in {response_time}ms")
                
                return section_results
            else:
                # If no section number, fall back to regular hybrid search
                logger.info("No section number detected, falling back to hybrid search")
                return await self.hybrid_search(query)
                
        except Exception as e:
            logger.error(f"Error in section specific search: {e}")
            # Fall back to regular hybrid search in case of error
            return await self.hybrid_search(query)

    def _build_context(self, search_results: List[Dict[str, Any]]) -> Tuple[str, List[str], List[Dict[str, Any]]]:
        """Build context from search results and return also the chunks that were actually included"""
        context_chunks = []
        citations = []
        included_chunks = []  # List of chunks that were actually included in the context
        total_tokens = 0
        
        # Remove hard-coding! Now rely on smart algorithm only
        # Search is already ranked by relevance - keep this order
        reordered_results = search_results
        
        # Limit number of chunks and token limit
        max_chunks_for_context = min(
            len(reordered_results), 
            self.search_config.MAX_CHUNKS_FOR_CONTEXT
        )
        
        for i, result in enumerate(reordered_results[:max_chunks_for_context]):
            chunk_content = result.get('chunk_text', result.get('content', ''))
            document_name = result.get('document_name', f'מסמך {i+1}')
            
            # Estimate tokens (approximately)
            estimated_tokens = len(chunk_content.split()) * 1.3
            
            if total_tokens + estimated_tokens > self.context_config.MAX_CONTEXT_TOKENS:
                logger.info(f"Context token limit reached at chunk {i}")
                break
            
            # Add similarity score information if available
            similarity_info = ""
            if 'similarity_score' in result:
                similarity_info = f" (דומיות: {result['similarity_score']:.3f})"
            elif 'combined_score' in result:
                similarity_info = f" (ציון: {result['combined_score']:.3f})"
            
            context_chunks.append(f"מקור {len(included_chunks)+1} - {document_name}{similarity_info}:\n{chunk_content}")
            citations.append(document_name)
            included_chunks.append(result)  # Save the chunk that was actually included
            total_tokens += estimated_tokens
        
        context = "\n\n".join(context_chunks)
        
        logger.info(f"Built context from {len(context_chunks)} chunks, ~{int(total_tokens)} tokens")
        return context, citations, included_chunks

    def _find_best_chunk_for_display(self, search_results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Find the most relevant chunk for display in UI - smart search with emphasis on exact phrases
        
        DEPRECATED: This function is no longer used. Instead, the model cites the sources it uses
        using _extract_cited_sources and _get_cited_chunks.
        """
        if not search_results:
            return None
        
        query_lower = query.lower()
        
        # First, search for exact phrases from the question
        exact_phrases = []
        if 'מן המניין' in query_lower:
            exact_phrases.append('מן המניין')
        if 'על תנאי' in query_lower:
            exact_phrases.append('על תנאי')
        if 'ועדת מלגות' in query_lower:
            exact_phrases.append('ועדת מלגות')
        
        # If there is an exact phrase, search for it first
        if exact_phrases:
            for chunk in search_results:
                chunk_text = chunk.get('chunk_text', chunk.get('content', ''))
                for phrase in exact_phrases:
                    if phrase in chunk_text:
                        logger.info(f"Found exact phrase '{phrase}' in chunk - selecting it")
                        return chunk
        
        # Topic keywords for different topics
        topic_keywords = {
            'parking': ['חני', 'חנה', 'קנס', 'מגרש', 'רכב'],
            'scholarships': ['מלגה', 'מלגות', 'ועדת', 'סיוע', 'בקשה'],
            'grades': ['ציון', 'בחינה', 'מבחן', 'הערכה'],
            'tuition': ['שכר', 'לימוד', 'תשלום', 'כסף'],
            'discipline': ['משמעת', 'עבירה', 'עונש'],
            'student_status': ['מן המניין', 'על תנאי', 'סטודנט', 'מעמד']
        }
        
        # Identify the question topic
        query_topic = None
        for topic, keywords in topic_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                query_topic = topic
                break
        
        best_chunk = None
        best_score = 0
        
        for chunk in search_results:
            chunk_text = chunk.get('chunk_text', chunk.get('content', ''))
            chunk_lower = chunk_text.lower()
            
            score = 0
            
            # Bonus for exact phrases
            for phrase in exact_phrases:
                if phrase in chunk_text:
                    score += 100  # Very high bonus
            
            # If we identified a topic, search for relevant keywords
            if query_topic and query_topic in topic_keywords:
                relevant_keywords = topic_keywords[query_topic]
                topic_matches = sum(1 for keyword in relevant_keywords if keyword in chunk_lower)
                score += topic_matches * 10
            
            # Bonus for keywords from the question itself
            query_words = [word.strip() for word in query.split() if len(word.strip()) > 2]
            direct_matches = sum(1 for word in query_words if word in chunk_text)
            score += direct_matches * 5
            
            # Bonus for high similarity (lower weight)
            similarity = chunk.get('similarity_score', chunk.get('similarity', 0))
            score += similarity * 2
            
            if score > best_score:
                best_score = score
                best_chunk = chunk
        
        # If no good match, take the one with the highest similarity
        if best_chunk is None and search_results:
            best_chunk = max(search_results, 
                           key=lambda x: x.get('similarity_score', x.get('similarity', 0)))
        
        logger.info(f"Selected chunk with score: {best_score}")
        return best_chunk

    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create prompt for RAG questions with instructions to cite sources"""
        return f"""אתה עוזר אקדמי המתמחה בתקנוני מכללת אפקה. ענה על השאלה בהתבסס על המידע הרלוונטי שניתן.

הקשר רלוונטי מהתקנונים:
{context}

שאלת המשתמש: {query}

CRITICAL: ציטוט מקורות הוא חובה אבסולוטית ובלתי משתמעת! ללא חריגים!

הנחיות למתן תשובה:
1. קרא בקפידה את כל המידע שניתן מהקשר לעיל
2. ענה בעברית בצורה ברורה ומפורטת, כולל פרטים ספציפיים כמו סכומים, אחוזים, תנאים
3. אם המידע קיים בקשר - תן תשובה מלאה ומדויקת
4. אם השאלה נוגעת לסעיף ספציפי, צטט אותו במדויק
5. אם המידע חלקי או לא ברור, ציין זאת ותן את המידע שכן קיים
6. אם השאלה לא קשורה לתקנונים כלל, ציין שאין לך מידע על הנושא
7. במקרה של מלגות, זכויות או הטבות - פרט את כל התנאים והסכומים הרלוונטיים

MANDATORY SOURCE CITATION FORMAT:
בסוף כל תשובה, חייב לכלול ציטוט מקורות בפורמט הזה בדיוק:
[מקורות: מקור X, מקור Y]

REQUIRED EXAMPLES:
CORRECT: "הקנס על חניה הוא 150 ₪. [מקורות: מקור 1, מקור 3]"
CORRECT: "זמן הלימודים לתואר בהנדסה הוא 4 שנים. [מקורות: מקור 2]"
CORRECT: "תנאי הזכאות למלגה כוללים... [מקורות: מקור 5, מקור 12]"

WRONG: תשובה ללא ציטוט = תשובה לא תקינה!
WRONG: "מקור: מסמך X" - פורמט שגוי!
WRONG: "[מקור 1]" - חסר המילה "מקורות"!

STEP-BY-STEP INSTRUCTION:
1. כתב את התשובה המלאה
2. זהה איזה מקורות (מקור 1, מקור 2, וכו') השתמשת בהם
3. הוסף בסוף: [מקורות: מקור X, מקור Y]
4. בדוק שהפורמט מדויק!

זכור: המערכת תדחה כל תשובה ללא ציטוט מקורות במדויק הפורמט הנדרש!

תשובה:"""

    def _extract_cited_sources(self, answer: str) -> List[int]:
        """Extract the sources cited by the model from the answer with strong validation"""
        import re
        
        # Alternative patterns for source identification
        patterns = [
            r'\[מקורות:\s*([^\]]+)\]',  # הפטרן הסטנדרטי
            r'\[מקור:\s*([^\]]+)\]',    # ללא ס' ברבים
            r'מקורות:\s*([^\n\r]+)',   # ללא סוגריים מרובעים
            r'מקור:\s*([^\n\r]+)',     # ללא ס' ברבים וללא סוגריים
            r'\(מקורות:\s*([^\)]+)\)', # עם סוגריים עגולים
        ]
        
        sources_text = None
        pattern_used = None
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, answer, re.IGNORECASE)
            if match:
                sources_text = match.group(1)
                pattern_used = i + 1
                logger.info(f"Sources found with pattern #{pattern_used}: {sources_text}")
                break
        
        if not sources_text:
            # Critical warning - Gemini didn't cite sources
            logger.error("CRITICAL: No sources cited in the answer! Gemini didn't follow the instructions!")
            logger.error(f"Full answer: {answer}")
            return []
        
        # Extract source numbers with advanced validation
        source_numbers = []
        source_pattern = r'מקור\s*(\d+)'
        source_matches = re.findall(source_pattern, sources_text, re.IGNORECASE)
        
        for match in source_matches:
            try:
                source_num = int(match)
                if 1 <= source_num <= 100:  # Reasonable number of sources
                    source_numbers.append(source_num)
                else:
                    logger.warning(f"Invalid source number: {source_num}")
            except ValueError:
                logger.warning(f"Cannot convert to number: {match}")
                continue
        
        if not source_numbers:
            logger.error(f"No valid source numbers found in text: {sources_text}")
        else:
            logger.info(f"Sources cited successfully: {source_numbers}")
        
        return source_numbers

    async def _get_cited_chunks(self, included_chunks: List[Dict[str, Any]], cited_source_numbers: List[int], query: str = "", answer: str = "") -> List[Dict[str, Any]]:
        """Return the chunks that were actually cited by the model from the chunks that were included in the context"""
        if not cited_source_numbers:
            # If no citations, find the most relevant chunk using semantic similarity
            logger.warning("No citations found from the model - find a relevant chunk using semantic similarity")
            return await self._find_best_fallback_chunk_semantic(included_chunks, answer)
        
        # Collect all the chunks that were cited
        cited_chunks = []
        for source_num in cited_source_numbers:
            # Sources start from 1, but the index starts from 0
            index = source_num - 1
            if 0 <= index < len(included_chunks):
                cited_chunks.append(included_chunks[index])
                logger.info(f"Found cited source {source_num} (out of {len(included_chunks)} chunks in context)")
            else:
                logger.warning(f"Source {source_num} not found in context (only {len(included_chunks)} sources)")
        
        if not cited_chunks:
            logger.warning("No valid chunks found from the citations - go to semantic fallback")
            return await self._find_best_fallback_chunk_semantic(included_chunks, answer)
        
        # If there is more than one cited source, choose the most relevant for the answer
        if len(cited_chunks) > 1:
            logger.info(f"Found {len(cited_chunks)} cited sources - choose the most relevant for the answer")
            best_chunk = await self._find_best_among_cited_chunks(cited_chunks, answer)
            return [best_chunk]
        
        return cited_chunks

    async def _find_best_among_cited_chunks(self, cited_chunks: List[Dict[str, Any]], answer: str) -> Dict[str, Any]:
        """Choose the most relevant chunk from the chunks that were cited by the LLM"""
        if not cited_chunks or not answer:
            logger.warning("Cannot select from cited chunks - return first")
            return cited_chunks[0] if cited_chunks else None
        
        if len(cited_chunks) == 1:
            return cited_chunks[0]
            
        try:
            # Create embedding for the answer
            answer_embedding = await self.generate_query_embedding(answer)
            
            # Calculate similarity for each cited chunk + content analysis
            scored_chunks = []
            
            for chunk in cited_chunks:
                chunk_text = chunk.get('chunk_text', chunk.get('content', ''))
                chunk_id = chunk.get('id', 'unknown')
                
                if chunk_text:
                    # Create embedding for the chunk
                    chunk_embedding = await self.generate_query_embedding(chunk_text)
                    
                    # Calculate cosine similarity
                    similarity = np.dot(answer_embedding, chunk_embedding) / (
                        np.linalg.norm(answer_embedding) * np.linalg.norm(chunk_embedding)
                    )
                    
                    # Content analysis for precision enhancement
                    content_score = 0
                    chunk_lower = chunk_text.lower()
                    answer_lower = answer.lower()
                    
                    # Bonus for shared words
                    answer_words = set(answer_lower.split())
                    chunk_words = set(chunk_lower.split())
                    common_words = answer_words.intersection(chunk_words)
                    content_score += len(common_words) * 0.01
                    
                    # Bonus for important keywords
                    key_phrases = {
                        'מן המניין': 0.15,
                        'על תנאי': 0.1,
                        'עומד בתנאי': 0.12,
                        'דרישות': 0.08,
                        'קבלה': 0.08,
                        'תוכנית לימודים': 0.1
                    }
                    
                    for phrase, weight in key_phrases.items():
                        if phrase in chunk_lower and phrase in answer_lower:
                            content_score += weight
                    
                    # Combined score
                    combined_score = similarity + content_score
                    
                    logger.info(f"Cited chunk {chunk_id} - similarity: {similarity:.3f}, content: {content_score:.3f}, combined: {combined_score:.3f}")
                    
                    scored_chunks.append((chunk, combined_score, similarity))
            
            if scored_chunks:
                # Select the best by combined score
                best_chunk, best_combined, best_similarity = max(scored_chunks, key=lambda x: x[1])
                chunk_id = best_chunk.get('id', 'unknown')
                logger.info(f"Selected cited chunk {chunk_id} with combined score {best_combined:.3f} (similarity: {best_similarity:.3f})")
                return best_chunk
            else:
                logger.warning("Cannot calculate scores - return first")
                return cited_chunks[0]
                
        except Exception as e:
            logger.error(f"Error selecting cited chunk: {e}")
            return cited_chunks[0]

    def _extract_relevant_chunk_segment(self, chunk_text: str, query: str, answer: str, max_length: int = 500) -> str:
        """Extract the most relevant segment from the chunk for display in the UI"""
        if not chunk_text or len(chunk_text) <= max_length:
            return chunk_text
        
        try:
            # Split the text into sentences
            sentences = [s.strip() for s in re.split(r'[.!?]\s+', chunk_text) if s.strip()]
            if not sentences:
                return chunk_text[:max_length] + "..."
            
            # Keywords from the question and answer
            query_words = set(re.findall(r'\b\w+\b', query.lower()))
            answer_words = set(re.findall(r'\b\w+\b', answer.lower()))
            key_words = query_words.union(answer_words)
            
            # Important keywords for the domain
            domain_keywords = {
                'מן המניין', 'על תנאי', 'עומד בתנאי', 'דרישות', 'קבלה', 
                'תוכנית לימודים', 'ציון', 'ממוצע', 'סטודנט', 'חניה', 'מלגה',
                'זמן', 'שנים', 'תקופה', 'משך', 'לימודים'
            }
            
            # Score for each sentence
            scored_sentences = []
            for i, sentence in enumerate(sentences):
                sentence_lower = sentence.lower()
                score = 0
                
                # Bonus for words from the question/answer
                word_matches = sum(1 for word in key_words if word in sentence_lower and len(word) > 2)
                score += word_matches * 2
                
                # Bonus for domain keywords
                domain_matches = sum(1 for keyword in domain_keywords if keyword in sentence_lower)
                score += domain_matches * 3
                
                # Bonus for position (first sentences are more important)
                position_bonus = max(0, 3 - i * 0.5)
                score += position_bonus
                
                # Bonus for appropriate length (not too short, not too long)
                length = len(sentence)
                if 50 <= length <= 200:
                    score += 1
                elif length < 20:
                    score -= 2
                
                scored_sentences.append((sentence, score, i))
                logger.debug(f"Sentence {i}: score={score:.2f}, length={length}")
            
            # Sort by score
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            
            # Build the relevant segment
            selected_sentences = []
            current_length = 0
            used_indices = set()
            
            # Add the best sentences up to the maximum length
            for sentence, score, index in scored_sentences:
                if current_length + len(sentence) <= max_length:
                    selected_sentences.append((sentence, index))
                    used_indices.add(index)
                    current_length += len(sentence) + 1  # +1 for space
                    logger.debug(f"Selected sentence {index} with score {score:.2f}")
                
                if current_length >= max_length * 0.8:  # Filled 80% of the space
                    break
            
            if not selected_sentences:
                # If nothing is found, take the first sentence
                return sentences[0][:max_length] + ("..." if len(sentences[0]) > max_length else "")
            
            # Sort by original order in the text
            selected_sentences.sort(key=lambda x: x[1])
            
            # Build the final text
            result = " ".join([sentence for sentence, _ in selected_sentences])
            
            # Verify the text is not cut in the middle of a word
            if len(result) >= max_length:
                result = result[:max_length].rsplit(' ', 1)[0] + "..."
            
            logger.info(f"Extracted relevant segment of {len(result)} characters out of {len(chunk_text)} original characters")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting relevant segment: {e}")
            # In case of error, return the simple truncated text
            return chunk_text[:max_length] + ("..." if len(chunk_text) > max_length else "")

    def _find_best_fallback_chunk(self, included_chunks: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Find the most relevant chunk when there are no explicit citations"""
        if not included_chunks:
            return []
        
        query_lower = query.lower()
        
        # Keywords for identifying topics
        topic_keywords = {
            'time_limits': ['זמן', 'שנים', 'שנה', 'מקסימלי', 'משך', 'תקופה', 'לימודים', 'סיום', 'הנדסה', 'מדעים', 'תוכנית', 'יום', 'ערב', 'שנתיים מעבר', 'מניין שנות'],
            'parking': ['חני', 'חנה', 'קנס', 'רכב', 'מגרש'],
            'scholarships': ['מלגה', 'מלגות', 'ועדה', 'ועדת'],
            'grades': ['ציון', 'ציונים', 'ממוצע', 'גמר'],
            'student_status': ['מן המניין', 'על תנאי', 'סטודנט'],
            'fees': ['תשלום', 'שכר לימוד', 'דמי', 'עלות']
        }
        
        # ✅ Removal of hard-coding! Only smart algorithm
        # No more hard-coded chunk IDs
        
        # Search chunks with relevant keywords
        scored_chunks = []
        for chunk in included_chunks:
            content = chunk.get('chunk_text', chunk.get('content', '')).lower()
            score = 0
            chunk_id = chunk.get('id')
            
            # ✅ Removal of hard-coding! No more importance by ID
            
            # Basic score by similarity
            base_score = chunk.get('similarity_score', chunk.get('combined_score', 0))
            score += base_score * 100
            
            # Bonus for relevant keywords
            for topic, keywords in topic_keywords.items():
                topic_matches = sum(1 for keyword in keywords if keyword in query_lower)
                if topic_matches > 0:
                    content_matches = sum(1 for keyword in keywords if keyword in content)
                    bonus = content_matches * topic_matches * 20
                    
                    # Special bonus for chunks with precise information about the topic
                    if topic == 'time_limits' and any(phrase in content for phrase in ['מניין שנות', 'שנתיים מעבר', 'תוכנית בת', 'זמן מותר', 'משך מקסימלי']):
                        bonus *= 3  # 3x for chunks with precise information about time
                        logger.info(f"Found special chunk for time limits with relevant expressions")
                    
                    score += bonus
            
            # Additional bonus for words from the question that appear in the content
            query_words = [word for word in query_lower.split() if len(word) > 2]
            word_matches = sum(1 for word in query_words if word in content)
            score += word_matches * 10
            
            scored_chunks.append((chunk, score))
        
        # Sort by score and select the best
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        best_chunk = scored_chunks[0][0]
        best_score = scored_chunks[0][1]
        
        logger.info(f"Selected chunk fallback with score {best_score:.1f}")
        
        return [best_chunk]

    async def _find_best_fallback_chunk_semantic(self, included_chunks: List[Dict[str, Any]], answer: str) -> List[Dict[str, Any]]:
        """Find the most similar chunk to the answer using cosine similarity"""
        if not included_chunks or not answer:
            logger.warning("Cannot perform semantic similarity - no chunks or answer")
            return included_chunks[:1] if included_chunks else []
        
        try:
            # Create embedding for the final answer
            logger.info("Creating embedding for the final answer for semantic comparison")
            answer_embedding = await self.generate_query_embedding(answer)
            
            # Calculate cosine similarity for each chunk
            similarities = []
            for chunk in included_chunks:
                chunk_text = chunk.get('chunk_text', chunk.get('content', ''))
                if chunk_text:
                    # Create embedding for the chunk
                    chunk_embedding = await self.generate_query_embedding(chunk_text)
                    
                    # Calculate cosine similarity
                    similarity = np.dot(answer_embedding, chunk_embedding) / (
                        np.linalg.norm(answer_embedding) * np.linalg.norm(chunk_embedding)
                    )
                    similarities.append((chunk, similarity))
                    logger.info(f"Chunk {chunk.get('id', 'unknown')} semantic similarity: {similarity:.3f}")
            
            if not similarities:
                logger.warning("Cannot calculate similarities - return first chunk")
                return included_chunks[:1]
            
            # Select the chunk with the highest similarity
            best_chunk, best_similarity = max(similarities, key=lambda x: x[1])
            logger.info(f"Selected chunk {best_chunk.get('id', 'unknown')} with semantic similarity {best_similarity:.3f}")
            
            return [best_chunk]
            
        except Exception as e:
            logger.error(f"Error in semantic similarity fallback: {e}")
            # In case of error, return the previous method
            return included_chunks[:1] if included_chunks else []

    async def generate_answer(
        self, 
        query: str, 
        search_method: str = 'hybrid',
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a full answer for the query"""
        start_time = time.time()
        
        try:
            logger.info(f"Generating answer for query: {query[:100]}...")
            
            # Identify if this is a specific section question
            section_keywords = ['סעיף', 'בסעיף', 'פרק', 'תקנה']
            is_section_query = any(keyword in query for keyword in section_keywords)
            
            # Perform search based on the requested method
            if is_section_query:
                logger.info("Detected section-specific query, using enhanced search")
                search_results = await self.section_specific_search(query)
            elif search_method == 'semantic':
                search_results = await self.semantic_search(query, document_id)
            elif search_method == 'hybrid':
                search_results = await self.hybrid_search(query, document_id)
            elif search_method == 'contextual':
                search_results = await self.contextual_search(query)
            else:
                raise ValueError(f"Unknown search method: {search_method}")
            
            if not search_results:
                return {
                    "answer": "לא נמצא מידע רלוונטי בתקנונים לשאלה זו. אנא נסה לנסח את השאלה בצורה אחרת או פנה למשרד הסטודנטים.",
                    "sources": [],
                    "chunks_selected": [],
                    "search_results_count": 0,
                    "response_time_ms": int((time.time() - start_time) * 1000),
                    "search_method": search_method,
                    "query": query
                }
            
            # Build the context
            context, citations, included_chunks = self._build_context(search_results)
            
            # Create the prompt
            prompt = self._create_rag_prompt(query, context)
            
            # Debug: log the chunks being used
            logger.info(f"Using {len(search_results)} total chunks, {len(included_chunks)} included in context")
            for i, chunk in enumerate(included_chunks[:5]):  # Log first 5 chunks that were included
                similarity = chunk.get('similarity_score') or chunk.get('similarity', 0)
                chunk_preview = chunk.get('chunk_text', chunk.get('content', ''))[:100]
                logger.info(f"[CONTEXT-CHUNK-{i+1}] Similarity: {similarity:.3f} | Preview: {chunk_preview}")
            
            # Use the new citation system instead of the complex chunk selection algorithm
            
            # Create the answer with retry logic
            answer = await self._generate_with_retry(prompt)
            
            # Extract the sources the model actually used
            cited_source_numbers = self._extract_cited_sources(answer)
            cited_chunks = await self._get_cited_chunks(included_chunks, cited_source_numbers, query, answer)
            
            # Remove the citations from the final answer (optional)
            import re
            clean_answer = re.sub(r'\[מקורות:[^\]]+\]', '', answer).strip()
            
            # Add a relevant segment to each chunk that was selected
            for chunk in cited_chunks:
                chunk_text = chunk.get('chunk_text', chunk.get('content', ''))
                if chunk_text:
                    relevant_segment = self._extract_relevant_chunk_segment(
                        chunk_text, query, clean_answer, max_length=500
                    )
                    chunk['relevant_segment'] = relevant_segment
                    logger.info(f"Added relevant segment to chunk {chunk.get('id', 'unknown')}: {len(relevant_segment)} characters")
            
            response_time = int((time.time() - start_time) * 1000)
            
            result = {
                "answer": clean_answer,
                "sources": citations,
                "chunks_selected": cited_chunks,
                "search_results_count": len(search_results),
                "response_time_ms": response_time,
                "search_method": search_method,
                "query": query,
                "cited_sources": cited_source_numbers,  # Additional information about the sources cited
                "config_used": {
                    "similarity_threshold": self.search_config.SIMILARITY_THRESHOLD,
                    "max_chunks": self.search_config.MAX_CHUNKS_RETRIEVED,
                    "model": self.llm_config.MODEL_NAME,
                    "temperature": self.llm_config.TEMPERATURE
                }
            }
            
            # Check performance
            if response_time > self.performance_config.MAX_GENERATION_TIME_MS:
                logger.warning(f"Generation time {response_time}ms exceeds target "
                             f"{self.performance_config.MAX_GENERATION_TIME_MS}ms")
            
            logger.info(f"Answer generated successfully in {response_time}ms with {len(search_results)} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    async def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Create content with retry logic for rate limiting"""
        for attempt in range(max_retries):
            try:
                # Ensure we're using current key if Key Manager available
                if self.key_manager:
                    available_key = await self.key_manager.get_available_key()
                    if not available_key:
                        raise Exception("No available API keys for generation")
                    
                    # Configure with the available key
                    genai.configure(api_key=available_key['api_key'])
                    
                    # Recreate model with current key
                    self.model = genai.GenerativeModel(
                        self.llm_config.MODEL_NAME,
                        generation_config=genai.types.GenerationConfig(
                            temperature=self.llm_config.TEMPERATURE,
                            max_output_tokens=self.llm_config.MAX_OUTPUT_TOKENS
                        )
                    )
                
                logger.info(f"[RAG-GEN-DEBUG] Generating response for prompt length: {len(prompt)}")
                
                # Debug: Log first part of prompt to check content
                logger.info(f"[PROMPT-DEBUG] First 500 chars: {prompt[:500]}")
                logger.info(f"[PROMPT-DEBUG] Last 200 chars: {prompt[-200:]}")
                
                response = await self.model.generate_content_async(prompt)
                response_text = response.text
                
                logger.info(f"[RESPONSE-DEBUG] Raw response: {response_text[:200]}")
                
                # Track usage  
                await self._track_generation_usage(prompt, response_text, available_key.get('id'))
                
                logger.info(f"[RAG-GEN-DEBUG] Generated response length: {len(response_text)}")
                return response_text
                
            except Exception as e:
                error_str = str(e)
                
                # Check if this is a rate limiting error
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 5  # exponential backoff: 5, 10, 20 seconds
                        logger.warning(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Max retries reached for rate limiting")
                        return "מצטער, המערכת עמוסה כרגע. אנא נסה שוב בעוד כמה דקות."
                else:
                    # Other error - raise immediately
                    raise
    
    async def _log_search_analytics(
        self, 
        query: str, 
        search_type: str, 
        results_count: int,
        top_score: float, 
        response_time_ms: int,
        document_id: Optional[int] = None
    ):
        """Log search analytics to the analytics table"""
        try:
            analytics_data = {
                "query_text": query,
                "search_type": search_type,
                "results_count": results_count,
                "top_score": top_score,
                "response_time_ms": response_time_ms,
                "config_profile": get_current_profile() if 'get_current_profile' in locals() else 'default',
            }

            # The document_id is currently an integer and causes a UUID error in the RPC.
            # Temporarily removing it from the log until the DB schema is fixed.
            # if document_id is not None:
            #     analytics_data["document_id"] = document_id

            response = self.supabase.rpc(
                self.db_config.LOG_ANALYTICS_FUNCTION, 
                analytics_data
            ).execute()
            
            # Check for errors in the response
            if hasattr(response, 'error') and response.error:
                logger.warning(f"Failed to log search analytics: {response.error.message}")
            elif isinstance(response, dict) and response.get('error'):
                 logger.warning(f"Failed to log search analytics: {response.get('error')}")

        except Exception as e:
            # Handle cases where `response` might not be a standard object
            if "postgrest.exceptions.APIError" in str(type(e)):
                 logger.warning(f"Failed to log search analytics: {e.message}")
            else:
                 logger.warning(f"Failed to log search analytics: {e}")
    
    async def get_search_statistics(self, days_back: int = 30) -> Dict[str, Any]:
        """Get search statistics"""
        try:
            # Check if analytics is enabled
            if not self.performance_config.LOG_SEARCH_ANALYTICS:
                return {"error": "Analytics disabled in configuration"}
                
            response = self.supabase.rpc('get_search_statistics', {
                'days_back': days_back
            }).execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Error getting search statistics: {e}")
            return {"error": str(e)}
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        return rag_config.get_config_dict()



_rag_service_instance = None

def get_rag_service() -> RAGService:
    """Provides a singleton instance of the RAGService."""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
