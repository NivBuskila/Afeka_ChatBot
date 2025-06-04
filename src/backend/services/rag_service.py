import os
import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
import json

import google.generativeai as genai
from supabase import create_client, Client
import numpy as np

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        )
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # הגדרות RAG
        self.max_context_tokens = 6000  # השארת מקום לשאלה ותשובה
        self.similarity_threshold = 0.65  # threshold נמוך יותר לעברית
        self.max_chunks = 8
        
        logger.info("RAG Service initialized successfully")
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """יוצר embedding עבור שאילתה"""
        try:
            embedding_model = genai.embed_content(
                model="models/embedding-001",
                content=query,
                task_type="retrieval_query"
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
            max_results = max_results or self.max_chunks
            
            response = self.supabase.rpc('advanced_semantic_search', {
                'query_embedding': query_embedding,
                'similarity_threshold': self.similarity_threshold,
                'max_results': max_results,
                'target_document_id': document_id
            }).execute()
            
            results = response.data or []
            response_time = int((time.time() - start_time) * 1000)
            
            # רישום analytics
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
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """חיפוש היברידי (סמנטי + מילות מפתח)"""
        start_time = time.time()
        
        try:
            query_embedding = await self.generate_query_embedding(query)
            
            response = self.supabase.rpc('hybrid_search', {
                'query_text': query,
                'query_embedding': query_embedding,
                'similarity_threshold': self.similarity_threshold,
                'max_results': self.max_chunks,
                'target_document_id': document_id,
                'semantic_weight': semantic_weight,
                'keyword_weight': keyword_weight
            }).execute()
            
            results = response.data or []
            response_time = int((time.time() - start_time) * 1000)
            
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
            
            response = self.supabase.rpc('contextual_search', {
                'query_embedding': query_embedding,
                'section_filter': section_filter,
                'content_type_filter': content_type_filter,
                'similarity_threshold': self.similarity_threshold,
                'max_results': self.max_chunks + 5  # יותר תוצאות לסינון
            }).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error in contextual search: {e}")
            raise
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
        """בונה הקשר מהתוצאות"""
        context_parts = []
        citations = []
        current_tokens = 0
        
        for i, result in enumerate(search_results):
            chunk_text = result['chunk_text']
            chunk_tokens = result.get('token_count', len(chunk_text.split()) * 1.3)  # הערכה
            
            if current_tokens + chunk_tokens > self.max_context_tokens:
                break
                
            # בניית ציטוט
            doc_name = result.get('document_name', 'מסמך')
            section = result.get('section') or result.get('chunk_header')
            page = result.get('page_number')
            
            citation_parts = [doc_name]
            if section:
                citation_parts.append(f"סעיף: {section}")
            if page:
                citation_parts.append(f"עמוד {page}")
            
            citation = " | ".join(citation_parts)
            citations.append(citation)
            
            # הוספת הקונטקסט
            context_part = f"[מקור {i+1}: {citation}]\n{chunk_text}"
            context_parts.append(context_part)
            current_tokens += chunk_tokens
        
        context = "\n\n---\n\n".join(context_parts)
        return context, citations
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """יוצר prompt מותאם לRAG"""
        return f"""אתה מומחה תקנונים משפטי של מכללת אפקה. תפקידך לענות על שאלות בהתבסס בדיוק על התקנונים שסופקו.

עקרונות מנחים:
1. ענה רקרק על סמך המידע שסופק בהקשר
2. אם אין מידע מספיק - אמר זאת בבירור
3. צטט את המקורות הרלוונטיים בתשובתך
4. השתמש בשפה ברורה ומקצועית
5. אם יש מספר סעיפים רלוונטיים - הזכר את כולם
6. הדגש חובות וזכויות בבירור

הקשר מהתקנונים:
{context}

שאלת המשתמש: {query}

תשובה מפורטת:"""
    
    async def generate_answer(
        self, 
        query: str, 
        search_method: str = 'hybrid',
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """יוצר תשובה מבוססת RAG"""
        start_time = time.time()
        
        try:
            # ביצוע חיפוש לפי השיטה הנבחרת
            if search_method == 'semantic':
                search_results = await self.semantic_search(query, document_id)
            elif search_method == 'contextual':
                search_results = await self.contextual_search(query)
            else:  # hybrid (default)
                search_results = await self.hybrid_search(query, document_id)
            
            if not search_results:
                return {
                    "answer": "לא נמצא מידע רלוונטי בתקנונים לשאלה זו. אנא נסה לנסח את השאלה בצורה אחרת או פנה למשרד הסטודנטים.",
                    "sources": [],
                    "search_results_count": 0,
                    "response_time_ms": int((time.time() - start_time) * 1000),
                    "search_method": search_method
                }
            
            # בניית הקשר וציטוטים
            context, citations = self._build_context(search_results)
            
            # יצירת prompt וגנרציה
            prompt = self._create_rag_prompt(query, context)
            
            response = await asyncio.to_thread(
                self.model.generate_content, 
                prompt,
                generation_config={
                    'temperature': 0.1,  # תשובות יציבות יותר
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 1000,
                }
            )
            
            answer = response.text if response.text else "מצטער, לא הצלחתי לייצר תשובה מתאימה."
            
            response_time = int((time.time() - start_time) * 1000)
            
            result = {
                "answer": answer,
                "sources": citations,
                "search_results_count": len(search_results),
                "response_time_ms": response_time,
                "search_method": search_method,
                "query": query
            }
            
            logger.info(f"RAG answer generated in {response_time}ms with {len(citations)} sources")
            return result
            
        except Exception as e:
            logger.error(f"Error generating RAG answer: {e}")
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
            self.supabase.rpc('log_search_analytics', {
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
            response = self.supabase.rpc('get_search_statistics', {
                'days_back': days_back
            }).execute()
            
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error getting search statistics: {e}")
            return {}