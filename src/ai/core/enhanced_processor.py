"""
מעבד מסמכים משודרג לתקנוני מכללה
משלב את כל רכיבי התוכנית האסטרטגית: Smart Chunking + Advanced Retrieval + Context Assembly
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import sys

# הוספת הנתיב לתיקיית backend
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.core.database import get_supabase_client
    from services.embedding_service import EmbeddingService
    has_supabase = True
except ImportError as e:
    logging.warning(f"Could not import Supabase modules: {e}")
    has_supabase = False

from .smart_chunker import SmartChunker, ProcessedChunk
from .retrieval import AdvancedRetriever, SearchResult, ContextBundle
from .context_assembly import ContextBuilder, PromptTemplate

logger = logging.getLogger(__name__)

class EnhancedDocumentProcessor:
    """מעבד מסמכים משודרג עם יכולות RAG מתקדמות"""
    
    def __init__(self):
        self.supabase = get_supabase_client() if has_supabase else None
        self.embedding_service = EmbeddingService() if has_supabase else None
        self.smart_chunker = SmartChunker()
        self.retriever = AdvancedRetriever()
        self.context_builder = ContextBuilder()
        
        logger.info("Enhanced Document Processor initialized")

    async def enhanced_search_and_answer(self, 
                                       query: str,
                                       max_results: int = 10,
                                       include_context: bool = True) -> Dict[str, Any]:
        """חיפוש ומענה משודרג"""
        
        logger.info(f"מתחיל חיפוש משודרג עבור: '{query}'")
        
        try:
            # שלב 1: חיפוש רב-שלבי
            search_results = await self.retriever.multi_stage_search(
                query=query,
                max_results=max_results,
                semantic_threshold=0.78
            )
            
            if not search_results:
                return {
                    'status': 'no_results',
                    'message': 'לא נמצאו תוצאות רלוונטיות',
                    'results': []
                }
            
            # הכנת התוצאות למענה
            formatted_results = []
            for result in search_results[:5]:  # רק 5 התוצאות הטובות ביותר
                formatted_results.append({
                    'chunk_id': result.chunk_id,
                    'section_number': result.section_number,
                    'section_title': result.section_title,
                    'content': result.chunk_text[:500] + "..." if len(result.chunk_text) > 500 else result.chunk_text,
                    'content_type': result.content_type,
                    'final_score': round(result.final_score, 3),
                    'search_stage': result.search_stage
                })
            
            query_type = self.retriever._classify_query_type(query)
            
            result = {
                'status': 'success',
                'query': query,
                'query_type': query_type,
                'total_results': len(search_results),
                'results': formatted_results,
                'best_result': {
                    'section_number': search_results[0].section_number,
                    'section_title': search_results[0].section_title,
                    'content': search_results[0].chunk_text,
                    'hierarchical_path': search_results[0].hierarchical_path
                }
            }
            
            logger.info(f"חיפוש הושלם: {len(search_results)} תוצאות")
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בחיפוש משודרג: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'results': []
            } 