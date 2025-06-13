import os
import asyncio
import logging
import time
import re
from typing import List, Dict, Any, Optional, Tuple
import json

import google.generativeai as genai
from supabase import create_client, Client
import numpy as np

from ..config.current_profile import get_current_profile
from ..config.rag_config_profiles import get_profile

# ייבוא קובץ ההגדרות החדש
from ..config.rag_config import (
    rag_config,
    get_search_config,
    get_embedding_config,
    get_context_config,
    get_llm_config,
    get_database_config,
    get_performance_config
)

# בייבוא החדש
from src.ai.core.database_key_manager import DatabaseKeyManager

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, config_profile: Optional[str] = None):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        )
        
        # 🆕 החלף ל-Database Key Manager עם חיבור ישיר ל-Supabase
        self.key_manager = DatabaseKeyManager(use_direct_supabase=True)
        logger.info("🔑 RAG Service using Database Key Manager with direct Supabase connection")
        
        # 🎯 טעינת פרופיל מהמערכת המרכזית
        if config_profile is None:
            try:
                from ..config.current_profile import get_current_profile
                config_profile = get_current_profile()
                logger.info(f"🎯 Loaded central profile: {config_profile}")
            except ImportError:
                logger.warning("Central profile system not found, using manual profile selection")
        
        # טעינת הגדרות לפי פרופיל או ברירת מחדל
        if config_profile:
            try:
                from ..config.rag_config_profiles import get_profile
                profile_config = get_profile(config_profile)
                self.search_config = profile_config.search
                self.embedding_config = profile_config.embedding
                self.context_config = profile_config.context
                self.llm_config = profile_config.llm
                self.db_config = profile_config.database
                self.performance_config = profile_config.performance
                logger.info(f"✅ Using config profile: {config_profile}")
            except Exception as e:
                logger.warning(f"Failed to load profile '{config_profile}': {e}. Using default config.")
                # חזרה להגדרות ברירת מחדל
                self.search_config = get_search_config()
                self.embedding_config = get_embedding_config()
                self.context_config = get_context_config()
                self.llm_config = get_llm_config()
                self.db_config = get_database_config()
                self.performance_config = get_performance_config()
        else:
            # קבלת הגדרות מהconfig החדש
            self.search_config = get_search_config()
            self.embedding_config = get_embedding_config()
            self.context_config = get_context_config()
            self.llm_config = get_llm_config()
            self.db_config = get_database_config()
            self.performance_config = get_performance_config()
        
        # 🔥 הגדר Key Manager - נטען מפתחות בצורה lazy
        # Note: Keys will be loaded when first needed in ensure_available_key()
        logger.info("🔑 Database Key Manager configured - keys will be loaded on first use")
        
        # 🔥 יצירת מודל Gemini - יש fallback לסביבה
        # Try to get key from environment first (safe init approach)
        fallback_key = os.getenv("GEMINI_API_KEY")
        if fallback_key:
            genai.configure(api_key=fallback_key)
            logger.info("🔑 Using GEMINI_API_KEY from environment for initialization")
        else:
            # Try to use Key Manager for initialization (keys loaded lazily) 
            try:
                if self.key_manager:
                    # Just configure with environment key for now, database keys will be loaded lazily
                    logger.info("🔑 Database Key Manager configured - will use environment key for init")
                    # Will switch to database keys when needed
                else:
                    raise Exception("No API keys available from Database or environment")
            except Exception as e:
                logger.error(f"❌ Key initialization failed: {e}")
                raise Exception("No API keys available")
        
        # יצירת מודל Gemini עם הגדרות מהconfig
        self.model = genai.GenerativeModel(
            self.llm_config.MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                temperature=self.llm_config.TEMPERATURE,
                max_output_tokens=self.llm_config.MAX_OUTPUT_TOKENS
            )
        )
        
        logger.info(f"🚀 RAG Service initialized with profile '{config_profile or 'default'}' - "
                   f"Similarity threshold: {self.search_config.SIMILARITY_THRESHOLD}, "
                   f"Max chunks: {self.search_config.MAX_CHUNKS_RETRIEVED}, "
                   f"Model: {self.llm_config.MODEL_NAME}")
    
    def _track_embedding_usage(self, text: str, key_id: int = None):
        """Track token usage for embedding generation"""
        # Estimate tokens for embedding (much smaller than generation)
        estimated_tokens = len(text) // 8  # Embeddings use fewer tokens
        logger.info(f"🔢 [RAG-EMBED-TRACK] Estimated {estimated_tokens} tokens for embedding")
        # Note: Key tracking can be implemented later async

    def _track_generation_usage(self, prompt: str, response: str, key_id: int = None):
        """Track token usage for text generation"""
        input_tokens = len(prompt) // 4
        output_tokens = len(response) // 4
        total_tokens = input_tokens + output_tokens
        logger.info(f"🔢 [RAG-GEN-TRACK] Estimated {total_tokens} tokens ({input_tokens} input + {output_tokens} output)")
        # Note: Key tracking can be implemented later async
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """יוצר embedding עבור שאילתה"""
        try:
            # 🔥 Ensure we're using current key if Key Manager available
            key_id = None
            if self.key_manager:
                available_key = await self.key_manager.get_available_key()
                if not available_key:
                    raise Exception("No available API keys for embedding")
                
                # Configure with the available key
                genai.configure(api_key=available_key['api_key'])
                key_id = available_key.get('id')
                logger.info(f"🔑 Using key {available_key.get('key_name', 'unknown')} for embedding")
            
            embedding_model = genai.embed_content(
                model=self.embedding_config.MODEL_NAME,
                content=query,
                task_type=self.embedding_config.TASK_TYPE_QUERY
            )
            
            # 🔥 Track usage
            self._track_embedding_usage(query, key_id)
            
            return embedding_model['embedding']
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    async def semantic_search(
        self, 
        query: str, 
        document_id: Optional[int] = None,
        max_results: int = None
    ) -> List[Dict[str, Any]]:
        """חיפוש סמנטי במסמכים"""
        start_time = time.time()
        
        try:
            # יצירת embedding עבור השאילתה
            query_embedding = await self.generate_query_embedding(query)
            
            # ביצוע חיפוש באמצעות RPC
            max_results = max_results or self.search_config.MAX_CHUNKS_RETRIEVED
            
            response = self.supabase.rpc(self.db_config.SEMANTIC_SEARCH_FUNCTION, {
                'query_embedding': query_embedding,
                'match_threshold': self.search_config.SIMILARITY_THRESHOLD,
                'match_count': max_results,
                'target_document_id': document_id
            }).execute()
            
            results = response.data or []
            response_time = int((time.time() - start_time) * 1000)
            
            # רישום analytics
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
        """חיפוש היברידי (סמנטי + מילות מפתח)"""
        start_time = time.time()
        
        try:
            query_embedding = await self.generate_query_embedding(query)
            
            # שימוש במשקלים מהconfig אם לא סופקו
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
        """חיפוש מותנה לפי הקשר"""
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
        """חיפוש מיוחד למספרי סעיפים ספציפיים"""
        try:
            start_time = time.time()
            
            # זיהוי מספר סעיף בשאלה
            section_patterns = [
                r'סעיף\s+(\d+(?:\.\d+)*)',
                r'בסעיף\s+(\d+(?:\.\d+)*)',
                r'מה\s+(?:אומר|כתוב|נאמר)\s+(?:ב)?סעיף\s+(\d+(?:\.\d+)*)',
                r'(\d+(?:\.\d+)+)(?:\s|$)',  # מספרי סעיפים כמו 1.5.1
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
                # חיפוש מיוחד לסעיפים עם pattern matching
                query_embedding = await self.generate_query_embedding(query)
                
                response = self.supabase.rpc(self.db_config.SECTION_SEARCH_FUNCTION, {
                    'query_embedding': query_embedding,
                    'section_number': extracted_section,
                    'similarity_threshold': 0.3,  # סף נמוך יותר לחיפוש סעיפים
                    'max_results': self.search_config.MAX_CHUNKS_FOR_CONTEXT
                }).execute()
                
                section_results = response.data or []
                
                # אם לא נמצא דבר, חפש גם חיפוש היברידי רגיל
                if not section_results:
                    logger.info(f"No section-specific results found for {extracted_section}, falling back to hybrid search")
                    section_results = await self.hybrid_search(query)
                
                response_time = int((time.time() - start_time) * 1000)
                logger.info(f"Section search completed: {len(section_results)} results in {response_time}ms")
                
                return section_results
            else:
                # אם לא נמצא מספר סעיף, חזור לחיפוש רגיל
                logger.info("No section number detected, falling back to hybrid search")
                return await self.hybrid_search(query)
                
        except Exception as e:
            logger.error(f"Error in section specific search: {e}")
            # חזרה לחיפוש רגיל במקרה של שגיאה
            return await self.hybrid_search(query)

    def _build_context(self, search_results: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
        """בונה קונטקסט מתוצאות החיפוש"""
        context_chunks = []
        citations = []
        total_tokens = 0
        
        # מגביל למספר chunks מקסימלי ולגבול tokens
        max_chunks_for_context = min(
            len(search_results), 
            self.search_config.MAX_CHUNKS_FOR_CONTEXT
        )
        
        for i, result in enumerate(search_results[:max_chunks_for_context]):
            chunk_content = result.get('chunk_text', result.get('content', ''))
            document_name = result.get('document_name', f'מסמך {i+1}')
            
            # הערכת tokens (בקירוב)
            estimated_tokens = len(chunk_content.split()) * 1.3
            
            if total_tokens + estimated_tokens > self.context_config.MAX_CONTEXT_TOKENS:
                logger.info(f"Context token limit reached at chunk {i}")
                break
            
            # הוספת מידע על הציון דומיות אם זמין
            similarity_info = ""
            if 'similarity_score' in result:
                similarity_info = f" (דומיות: {result['similarity_score']:.3f})"
            elif 'combined_score' in result:
                similarity_info = f" (ציון: {result['combined_score']:.3f})"
            
            context_chunks.append(f"מקור {i+1} - {document_name}{similarity_info}:\n{chunk_content}")
            citations.append(document_name)
            total_tokens += estimated_tokens
        
        context = "\n\n".join(context_chunks)
        
        logger.info(f"Built context from {len(context_chunks)} chunks, ~{int(total_tokens)} tokens")
        return context, citations

    def _create_rag_prompt(self, query: str, context: str) -> str:
        """יוצר prompt מותאם לשאלות תקנונים"""
        return f"""אתה עוזר אקדמי המתמחה בתקנוני מכללת אפקה. ענה על השאלה בהתבסס על המידע הרלוונטי שניתן.

הקשר רלוונטי מהתקנונים:
{context}

שאלת המשתמש: {query}

הנחיות למתן תשובה:
1. ענה בעברית בצורה ברורה ומדויקת
2. השתמש במידע מהקשר שניתן בלבד
3. אם השאלה נוגעת לסעיף ספציפי, צטט אותו במדויק
4. אם המידע חלקי או לא ברור, ציין זאת
5. אם השאלה לא קשורה לתקנונים, ציין שאין לך מידע על הנושא

תשובה:"""

    async def generate_answer(
        self, 
        query: str, 
        search_method: str = 'hybrid',
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """יוצר תשובה מלאה לשאילתה"""
        start_time = time.time()
        
        try:
            logger.info(f"Generating answer for query: {query[:100]}...")
            
            # זיהוי אם זו שאלה על סעיף ספציפי
            section_keywords = ['סעיף', 'בסעיף', 'פרק', 'תקנה']
            is_section_query = any(keyword in query for keyword in section_keywords)
            
            # ביצוע חיפוש לפי השיטה המבוקשת
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
            
            # בניית הקשר
            context, citations = self._build_context(search_results)
            
            # יצירת prompt
            prompt = self._create_rag_prompt(query, context)
            
            # יצירת תשובה עם retry logic
            answer = await self._generate_with_retry(prompt)
            
            response_time = int((time.time() - start_time) * 1000)
            
            result = {
                "answer": answer,
                "sources": citations,
                "chunks_selected": search_results,
                "search_results_count": len(search_results),
                "response_time_ms": response_time,
                "search_method": search_method,
                "query": query,
                "config_used": {
                    "similarity_threshold": self.search_config.SIMILARITY_THRESHOLD,
                    "max_chunks": self.search_config.MAX_CHUNKS_RETRIEVED,
                    "model": self.llm_config.MODEL_NAME,
                    "temperature": self.llm_config.TEMPERATURE
                }
            }
            
            # בדיקת ביצועים
            if response_time > self.performance_config.MAX_GENERATION_TIME_MS:
                logger.warning(f"Generation time {response_time}ms exceeds target "
                             f"{self.performance_config.MAX_GENERATION_TIME_MS}ms")
            
            logger.info(f"Answer generated successfully in {response_time}ms with {len(search_results)} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    async def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """יוצר תוכן עם retry logic למקרה של rate limiting"""
        for attempt in range(max_retries):
            try:
                # 🔥 Ensure we're using current key if Key Manager available
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
                
                logger.info(f"🔢 [RAG-GEN-DEBUG] Generating response for prompt length: {len(prompt)}")
                response = await self.model.generate_content_async(prompt)
                response_text = response.text
                
                # 🔥 Track usage
                self._track_generation_usage(prompt, response_text)
                
                logger.info(f"🔢 [RAG-GEN-DEBUG] Generated response length: {len(response_text)}")
                return response_text
                
            except Exception as e:
                error_str = str(e)
                
                # בדיקה אם זה rate limiting error
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
                    # שגיאה אחרת - העלה מיד
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
        """רושם נתוני חיפוש לטבלת analytics"""
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
        """מחזיר סטטיסטיקות חיפוש"""
        try:
            # בדיקה אם analytics מופעל
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
        """מחזיר את ההגדרות הנוכחיות"""
        return rag_config.get_config_dict()


# --- Dependency Injection (if using Flask-Injector or similar) ---
# You might use a framework for dependency injection, or a simple factory
_rag_service_instance = None

def get_rag_service() -> RAGService:
    """Provides a singleton instance of the RAGService."""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
