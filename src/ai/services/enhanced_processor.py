"""
מעבד מסמכים משודרג לתקנוני מכללה
משלב את כל רכיבי התוכנית האסטרטגית: Smart Chunking + Advanced Retrieval + Context Assembly
"""

import logging
import asyncio
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import sys

import google.generativeai as genai
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class EnhancedProcessor:
    """מעבד מסמכים משודרג פשוט"""
    
    def __init__(self):
        # ✅ This direct client creation works fine and is what's actually being used
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        )
        
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        
        logger.info("Enhanced Processor initialized")

    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """חיפוש מתקדם במסמכים"""
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query, is_query=True)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            # Search in advanced_document_chunks table
            response = self.supabase.rpc(
                "advanced_semantic_search",
                {
                    "query_embedding": query_embedding,
                    "similarity_threshold": 0.75,
                    "match_count": max_results,
                },
            ).execute()
            
            if response.data:
                logger.info(f"Found {len(response.data)} results")
                return response.data
            
            logger.info("No results found")
            return []
            
        except Exception as e:
            logger.error(f"Error in enhanced search: {e}")
            return []

    async def search_and_answer(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """חיפוש והפקת תשובה מלאה"""
        try:
            # Get search results
            search_results = await self.search(query, max_results)
            
            if not search_results:
                return {
                    "answer": "לא מצאתי מידע רלוונטי לשאלתך במסמכי המכללה.",
                    "sources": [],
                    "query": query
                }
            
            # Build context from results
            context_parts = []
            sources = []
            
            for i, result in enumerate(search_results[:3]):  # Use top 3 results
                content = result.get('content', '')
                section_number = result.get('section_number', '')
                hierarchical_path = result.get('hierarchical_path', '')
                
                context_parts.append(f"מידע {i+1}: {content}")
                sources.append({
                    "section_number": section_number,
                    "hierarchical_path": hierarchical_path,
                    "content_preview": content[:150] + "..." if len(content) > 150 else content,
                    "similarity": result.get('similarity', 0)
                })
            
            # Generate answer using Gemini
            context = "\n\n".join(context_parts)
            prompt = f"""בהתבסס על המידע הבא מתקנוני המכללה:

{context}

השב על השאלה הבאה בצורה מדויקת ומפורטת:
{query}

הנחיות:
- השב בעברית בלבד
- השתמש רק במידע שמופיע בהקשר
- אם המידע חלקי, ציין זאת
- הוסף הפניות לסעיפים רלוונטיים כשרלוונטי"""

            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(prompt)
                answer = response.text
            except Exception as e:
                logger.error(f"Error generating answer: {e}")
                answer = f"נמצא מידע רלוונטי אך אירעה שגיאה ביצירת התשובה. מידע זמין: {context[:300]}..."
            
            return {
                "answer": answer,
                "sources": sources,
                "query": query,
                "context_used": len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Error in search_and_answer: {e}")
            return {
                "answer": "אירעה שגיאה בעת חיפוש המידע. אנא נסה שוב.",
                "sources": [],
                "query": query,
                "error": str(e)
            }

    async def _generate_embedding(self, text: str, is_query: bool = False) -> Optional[List[float]]:
        """יצירת embedding לטקסט"""
        task_type = "retrieval_query" if is_query else "retrieval_document"
        
        if not text or not text.strip():
            return None
        
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type=task_type
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

# Keep the old class for compatibility
class EnhancedDocumentProcessor:
    """מעבד מסמכים משודרג עם יכולות RAG מתקדמות"""
    
    def __init__(self):
        logger.warning("EnhancedDocumentProcessor is deprecated, use EnhancedProcessor instead")
        self.enhanced_processor = EnhancedProcessor()

    async def enhanced_search_and_answer(self, 
                                       query: str,
                                       max_results: int = 10,
                                       include_context: bool = True) -> Dict[str, Any]:
        """חיפוש ומענה משודרג"""
        return await self.enhanced_processor.search_and_answer(query, max_results) 