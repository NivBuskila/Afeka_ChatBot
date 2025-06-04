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

# ייבוא קובץ ההגדרות החדש
from config.rag_config import (
    rag_config,
    get_search_config,
    get_embedding_config,
    get_context_config,
    get_llm_config,
    get_database_config,
    get_performance_config
)

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, config_profile: Optional[str] = None):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        )
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
            
        genai.configure(api_key=api_key)
        
        # 🎯 טעינת פרופיל מהמערכת המרכזית
        if config_profile is None:
            try:
                from config.current_profile import get_current_profile
                config_profile = get_current_profile()
                logger.info(f"🎯 Loaded central profile: {config_profile}")
            except ImportError:
                logger.warning("Central profile system not found, using manual profile selection")
        
        # טעינת הגדרות לפי פרופיל או ברירת מחדל
        if config_profile:
            try:
                from config.rag_config_profiles import get_profile
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
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """יוצר embedding עבור שאילתה"""
        try:
            embedding_model = genai.embed_content(
                model=self.embedding_config.MODEL_NAME,
                content=query,
                task_type=self.embedding_config.TASK_TYPE_QUERY
            )
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
                'similarity_threshold': self.search_config.SIMILARITY_THRESHOLD,
                'max_results': max_results,
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
                    response_time
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
                'similarity_threshold': self.search_config.SIMILARITY_THRESHOLD,
                'max_results': self.search_config.MAX_CHUNKS_RETRIEVED,
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
                    response_time
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
                        break
            
            if not extracted_section:
                # אם לא נמצא מספר סעיף ספציפי, נחזור לחיפוש רגיל
                return await self.hybrid_search(query)
            
            logger.info(f"Section-specific search for section: {extracted_section}")
            
            # חיפוש היברידי רגיל
            query_embedding = await self.generate_query_embedding(query)
            
            # חיפוש עם דגש על מספר הסעיף
            section_enhanced_query = f"סעיף {extracted_section} {query}"
            section_embedding = await self.generate_query_embedding(section_enhanced_query)
            
            # משקל כפול לsection
            combined_embedding = [
                (e1 * 0.4 + e2 * 0.6) for e1, e2 in zip(query_embedding, section_embedding)
            ]
            
            # חיפוש עם סף נמוך יותר לסעיפים ספציפיים
            response = self.supabase.rpc(self.db_config.HYBRID_SEARCH_FUNCTION, {
                'query_text': section_enhanced_query,
                'query_embedding': combined_embedding,
                'semantic_weight': 0.9,  # דגש על חיפוש סמנטי
                'keyword_weight': 0.1,
                'similarity_threshold': 0.25,  # סף נמוך מאוד לסעיפים
                'max_results': self.search_config.MAX_RESULTS_EXTENDED
            }).execute()
            
            results = response.data or []
            
            # סינון נוסף - העדפה לתוצאות שמכילות את מספר הסעיף
            section_results = []
            other_results = []
            
            for result in results:
                chunk_text = result.get('chunk_text', '') or ''
                chunk_header = result.get('chunk_header', '') or ''
                metadata = result.get('metadata', {}) or {}
                
                # בדיקה אם מספר הסעיף מופיע בטקסט או במטאדטה
                metadata_str = str(metadata) if metadata else ''
                if (extracted_section in chunk_text or 
                    extracted_section in chunk_header or 
                    extracted_section in metadata_str):
                    section_results.append(result)
                else:
                    other_results.append(result)
            
            # עדיפות לתוצאות עם מספר הסעיף, אבל נכלול גם אחרות
            final_results = section_results + other_results[:self.search_config.MAX_CHUNKS_RETRIEVED]
            final_results = final_results[:self.search_config.MAX_CHUNKS_RETRIEVED]
            
            search_time = int((time.time() - start_time) * 1000)
            
            # רישום analytics
            if self.performance_config.LOG_SEARCH_ANALYTICS:
                await self._log_search_analytics(
                    query, 'section_specific', len(final_results),
                    final_results[0]['similarity_score'] if final_results else 0.0,
                    search_time
                )
            
            logger.info(f"Section-specific search completed: {len(section_results)} exact + {len(other_results[:self.search_config.MAX_CHUNKS_RETRIEVED-len(section_results)])} related results in {search_time}ms")
            return final_results
            
        except Exception as e:
            logger.error(f"Error in section-specific search: {e}")
            raise
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
        """בונה הקשר מהתוצאות"""
        context_parts = []
        citations = []
        current_tokens = 0
        max_tokens = self.context_config.AVAILABLE_CONTEXT_TOKENS
        
        # מגביל מספר צ'אנקים לפי ההגדרות
        max_chunks_for_context = min(
            self.search_config.MAX_CHUNKS_FOR_CONTEXT,
            len(search_results)
        )
        
        for i, result in enumerate(search_results[:max_chunks_for_context]):
            chunk_text = result['chunk_text']
            chunk_tokens = result.get('token_count', len(chunk_text.split()) * 1.3)  # הערכה
            
            if current_tokens + chunk_tokens > max_tokens:
                logger.info(f"Context token limit reached: {current_tokens + chunk_tokens} > {max_tokens}")
                break
                
            # בניית ציטוט
            doc_name = result.get('document_name', 'מסמך')
            
            citation_parts = [doc_name]
            
            # הוספת פרטים לפי ההגדרות
            if self.context_config.INCLUDE_CHUNK_HEADERS:
                section = result.get('section') or result.get('chunk_header')
                if section:
                    citation_parts.append(f"סעיף: {section}")
            
            if self.context_config.INCLUDE_PAGE_NUMBERS:
                page = result.get('page_number')
                if page:
                    citation_parts.append(f"עמוד {page}")
            
            citation = self.context_config.CITATION_SEPARATOR.join(citation_parts)
            
            if self.context_config.INCLUDE_CITATIONS:
                citations.append(citation)
            
            # הוספת הקונטקסט
            context_part = f"[מקור {i+1}: {citation}]\n{chunk_text}"
            context_parts.append(context_part)
            current_tokens += chunk_tokens
        
        context = self.context_config.CHUNK_SEPARATOR.join(context_parts)
        return context, citations
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """יוצר prompt מותאם לRAG"""
        return f"""אתה מומחה תקנונים משפטי של מכללת אפקה. תפקידך לענות על שאלות בהתבסס בדיוק על התקנונים שסופקו.

עקרונות מנחים:
1. ענה רק על סמך המידע שסופק בהקשר
2. אם אין מידע מספיק - אמר זאת בבירור
3. צטט את המקורות הרלוונטיים בתשובתך
4. השתמש בשפה ברורה ומקצועית
5. אם יש מספר סעיפים רלוונטיים - הזכר את כולם
6. הדגש חובות וזכויות בבירור

הקשר רלוונטי מהתקנונים:
{context}

שאלה: {query}

תשובה מקצועית מבוססת תקנונים:"""
    
    async def generate_answer(
        self, 
        query: str, 
        search_method: str = 'hybrid',
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """יוצר תשובה מלאה כולל חיפוש וייצור תשובה"""
        start_time = time.time()
        
        try:
            logger.info(f"Generating answer for query: '{query[:50]}...' using {search_method} search")
            
            # זיהוי אם השאלה מתייחסת לסעיף ספציפי
            section_query_patterns = [
                r'סעיף\s+\d+(?:\.\d+)*',
                r'בסעיף\s+\d+(?:\.\d+)*',
                r'מה\s+(?:אומר|כתוב|נאמר)\s+(?:ב)?סעיף\s+\d+(?:\.\d+)*'
            ]
            
            is_section_query = False
            try:
                is_section_query = any(re.search(pattern, query or "") for pattern in section_query_patterns)
            except Exception as e:
                logger.warning(f"Error in section pattern matching: {e}")
                is_section_query = False
            
            # בחירת שיטת חיפוש
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
                response = await self.model.generate_content_async(prompt)
                return response.text
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
        response_time_ms: int
    ):
        """רושם analytics של חיפוש"""
        try:
            # רק אם analytics מופעל בconfig
            if not self.performance_config.LOG_SEARCH_ANALYTICS:
                return
                
            self.supabase.rpc(self.db_config.ANALYTICS_FUNCTION, {
                'query_text': query,
                'search_type': search_type,
                'results_found': results_count,
                'top_result_score': top_score,
                'user_id_param': None,  # נוסיף user tracking מאוחר יותר
                'response_time_ms': response_time_ms
            }).execute()
        except Exception as e:
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
