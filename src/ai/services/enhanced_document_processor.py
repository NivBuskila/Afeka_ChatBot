"""
מעבד מסמכים משודרג לתקנוני מכללה
משלב את כל רכיבי התוכנית האסטרטגית: Smart Chunking + Advanced Retrieval + Context Assembly
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import sys
import os

# הוספת הנתיב לתיקיית backend
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.core.database import get_supabase_client
    import google.generativeai as genai
    from supabase import create_client, Client
    has_supabase = True
except ImportError as e:
    logging.warning(f"Could not import Supabase modules: {e}")
    has_supabase = False

from .smart_chunker import SmartChunker, ProcessedChunk
from .retrieval import AdvancedRetriever, SearchResult, ContextBundle
from .context_assembly import ContextBuilder, PromptTemplate

# Import vector utilities
from ..utils.vector_utils import ensure_768_dimensions, log_vector_info

logger = logging.getLogger(__name__)

class EnhancedDocumentProcessor:
    """מעבד מסמכים משודרג עם יכולות RAG מתקדמות"""
    
    def __init__(self):
        self.supabase = get_supabase_client() if has_supabase else None
        self.smart_chunker = SmartChunker()
        self.retriever = AdvancedRetriever()
        self.context_builder = ContextBuilder()
        
        # Configure Gemini API
        if has_supabase:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
        
        logger.info("Enhanced Document Processor initialized")

    async def process_and_store_document(self, 
                                       document_text: str,
                                       document_name: str,
                                       document_version: str = "",
                                       document_id: Optional[int] = None) -> Dict[str, Any]:
        """עיבוד ושמירה מתקדמת של מסמך"""
        
        logger.info(f"מתחיל עיבוד מתקדם של מסמך: {document_name}")
        
        try:
            # שלב 1: חלוקה חכמה לחלקים
            processed_chunks = self.smart_chunker.process_document(
                document_text=document_text,
                document_name=document_name,
                document_version=document_version
            )
            
            logger.info(f"נוצרו {len(processed_chunks)} chunks מעובדים")
            
            # שלב 2: יצירת embeddings ושמירה במסד הנתונים
            stored_chunks = []
            failed_chunks = []
            
            for chunk in processed_chunks:
                try:
                    stored_chunk_id = await self._store_advanced_chunk(chunk, document_id)
                    if stored_chunk_id:
                        stored_chunks.append({
                            'chunk_id': stored_chunk_id,
                            'section_number': chunk.metadata.section_number,
                            'content_type': chunk.metadata.content_type,
                            'size': chunk.size
                        })
                    else:
                        failed_chunks.append(chunk.metadata.section_number or 'unknown')
                        
                except Exception as e:
                    logger.error(f"שגיאה בשמירת chunk: {e}")
                    failed_chunks.append(chunk.metadata.section_number or 'unknown')
            
            # שלב 3: עיבוד הפניות צולבות
            await self._process_cross_references(stored_chunks)
            
            # שלב 4: עדכון statistics
            await self._update_document_statistics(document_id, len(stored_chunks))
            
            result = {
                'status': 'success',
                'total_chunks': len(processed_chunks),
                'stored_chunks': len(stored_chunks),
                'failed_chunks': len(failed_chunks),
                'chunks_info': stored_chunks,
                'failed_sections': failed_chunks
            }
            
            logger.info(f"סיים עיבוד מסמך {document_name}: {len(stored_chunks)} chunks נשמרו")
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בעיבוד מסמך {document_name}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'total_chunks': 0,
                'stored_chunks': 0
            }

    async def _store_advanced_chunk(self, chunk: ProcessedChunk, document_id: Optional[int]) -> Optional[int]:
        """שמירת chunk מתקדם במסד הנתונים"""
        
        if not self.supabase:
            return None
        
        try:
            # יצירת embedding באמצעות Gemini
            embedding = await self._generate_embedding(chunk.text)
            
            # הכנת הנתונים לשמירה
            chunk_data = {
                'document_id': document_id,
                'chunk_text': chunk.text,
                'chunk_type': chunk.metadata.chunk_type,
                'section_number': chunk.metadata.section_number,
                'section_title': chunk.metadata.section_title,
                'hierarchical_path': chunk.metadata.hierarchical_path,
                'chapter_name': chunk.metadata.chapter,
                'parent_context': chunk.metadata.parent_context,
                'content_type': chunk.metadata.content_type,
                'is_definition': chunk.metadata.content_type == 'definition',
                'is_procedure': chunk.metadata.content_type == 'procedure',
                'is_temporal': chunk.metadata.is_temporal,
                'keywords': chunk.metadata.keywords,
                'cross_references': chunk.metadata.cross_references,
                'embedding': embedding,
                'chunk_size': chunk.size,
                'overlap_with_previous': chunk.overlap_with_previous,
                'token_count': chunk.token_count
            }
            
            # שמירה במסד הנתונים
            response = self.supabase.table('advanced_document_chunks')\
                .insert(chunk_data)\
                .execute()
            
            if response.data:
                return response.data[0]['id']
            
            return None
            
        except Exception as e:
            logger.error(f"שגיאה בשמירת chunk: {e}")
            return None

    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """יצירת embedding לטקסט"""
        if not text or not text.strip():
            return None
        
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            
            raw_embedding = result["embedding"] if result and 'embedding' in result else None
            if not raw_embedding:
                logger.error("No embedding returned from API")
                return None
            
            # וידוא שה-vector הוא בדיוק 768 dimensions
            embedding = ensure_768_dimensions(raw_embedding)
            
            # רישום מידע לdebug אם יש בעיה עם גודל הvector
            if len(raw_embedding) != 768:
                logger.warning(f"Enhanced processor embedding dimension adjusted from {len(raw_embedding)} to 768")
                log_vector_info(raw_embedding, "Original enhanced embedding")
                log_vector_info(embedding, "Adjusted enhanced embedding")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    async def _process_cross_references(self, stored_chunks: List[Dict]) -> None:
        """עיבוד והכנסת הפניות צולבות"""
        
        if not self.supabase:
            return
        
        try:
            for chunk_info in stored_chunks:
                chunk_id = chunk_info['chunk_id']
                
                # קבלת הפניות צולבות מהמסד הנתונים
                response = self.supabase.table('advanced_document_chunks')\
                    .select('cross_references')\
                    .eq('id', chunk_id)\
                    .single()\
                    .execute()
                
                if response.data and response.data['cross_references']:
                    cross_refs = response.data['cross_references']
                    
                    # הכנסת כל הפניה צולבת לטבלה נפרדת
                    for cross_ref in cross_refs:
                        cross_ref_data = {
                            'from_chunk_id': chunk_id,
                            'to_section_number': cross_ref,
                            'reference_type': 'general',
                            'confidence_score': 1.0
                        }
                        
                        self.supabase.table('cross_references')\
                            .insert(cross_ref_data)\
                            .execute()
                            
        except Exception as e:
            logger.error(f"שגיאה בעיבוד הפניות צולבות: {e}")

    async def _update_document_statistics(self, document_id: Optional[int], chunks_count: int) -> None:
        """עדכון סטטיסטיקות המסמך"""
        
        if not self.supabase or not document_id:
            return
        
        try:
            self.supabase.table('documents')\
                .update({
                    'chunks_count': chunks_count,
                    'processed': True,
                    'processed_at': 'now()',
                    'processing_status': 'completed'
                })\
                .eq('id', document_id)\
                .execute()
                
        except Exception as e:
            logger.error(f"שגיאה בעדכון סטטיסטיקות: {e}")

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
            
            # שלב 2: בניית קונטקסט מתקדם (אם נדרש)
            context_bundle = None
            formatted_prompt = None
            
            if include_context and search_results:
                # זיהוי סוג השאלה
                query_type = self.retriever._classify_query_type(query)
                
                # בניית חבילת קונטקסט לתוצאה הטובה ביותר
                context_bundle = await self._build_context_for_result(search_results[0], query)
                
                # בניית prompt מתקדם
                prompt_template = self.context_builder.build_advanced_context(
                    context_bundle=context_bundle,
                    query=query,
                    query_type=query_type
                )
                
                formatted_prompt = self.context_builder.format_final_prompt(prompt_template)
            
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
            
            result = {
                'status': 'success',
                'query': query,
                'query_type': query_type if include_context else 'unknown',
                'total_results': len(search_results),
                'results': formatted_results,
                'best_result': {
                    'section_number': search_results[0].section_number,
                    'section_title': search_results[0].section_title,
                    'content': search_results[0].chunk_text,
                    'hierarchical_path': search_results[0].hierarchical_path
                }
            }
            
            # הוספת קונטקסט אם נבנה
            if formatted_prompt:
                result['formatted_prompt'] = formatted_prompt
                result['context_info'] = {
                    'total_context_length': context_bundle.total_context_length,
                    'hierarchical_context_count': len(context_bundle.hierarchical_context),
                    'related_subsections_count': len(context_bundle.related_subsections),
                    'cross_references_count': len(context_bundle.cross_referenced_content)
                }
            
            # שמירת סטטיסטיקות חיפוש
            await self._save_search_analytics(query, len(search_results), search_results[0].final_score)
            
            logger.info(f"חיפוש הושלם: {len(search_results)} תוצאות")
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בחיפוש משודרג: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'results': []
            }

    async def _build_context_for_result(self, main_result: SearchResult, query: str) -> ContextBundle:
        """בניית חבילת קונטקסט עבור תוצאה מסוימת"""
        
        # פשוט יצירת context bundle בסיסי
        return ContextBundle(
            main_result=main_result,
            hierarchical_context=[],
            related_subsections=[],
            cross_referenced_content=[],
            definition_context=[],
            total_context_length=len(main_result.chunk_text)
        )

    async def _save_search_analytics(self, query: str, results_count: int, top_score: float) -> None:
        """שמירת סטטיסטיקות חיפוש"""
        
        if not self.supabase:
            return
        
        try:
            analytics_data = {
                'query_text': query,
                'search_type': 'enhanced',
                'results_found': results_count,
                'top_result_score': top_score,
                'response_time_ms': 0  # יחושב במקום אחר
            }
            
            self.supabase.table('search_analytics')\
                .insert(analytics_data)\
                .execute()
                
        except Exception as e:
            logger.error(f"שגיאה בשמירת אנליטיקס: {e}")

    async def get_enhanced_stats(self) -> Dict[str, Any]:
        """סטטיסטיקות מתקדמות של המערכת"""
        
        if not self.supabase:
            return {'error': 'Database not available'}
        
        try:
            # ספירת chunks מתקדמים
            chunks_response = self.supabase.table('advanced_document_chunks')\
                .select('*', count='exact')\
                .execute()
            
            total_advanced_chunks = chunks_response.count if hasattr(chunks_response, 'count') else 0
            
            # ספירת לפי סוג תוכן
            content_type_stats = {}
            for content_type in ['rule', 'procedure', 'definition', 'penalty', 'temporal']:
                type_response = self.supabase.table('advanced_document_chunks')\
                    .select('*', count='exact')\
                    .eq('content_type', content_type)\
                    .execute()
                content_type_stats[content_type] = type_response.count if hasattr(type_response, 'count') else 0
            
            # ספירת הפניות צולבות
            cross_refs_response = self.supabase.table('cross_references')\
                .select('*', count='exact')\
                .execute()
            
            total_cross_refs = cross_refs_response.count if hasattr(cross_refs_response, 'count') else 0
            
            # סטטיסטיקות חיפוש אחרונות
            recent_searches = self.supabase.table('search_analytics')\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(10)\
                .execute()
            
            return {
                'status': 'success',
                'total_advanced_chunks': total_advanced_chunks,
                'content_type_distribution': content_type_stats,
                'total_cross_references': total_cross_refs,
                'recent_searches': recent_searches.data if recent_searches.data else [],
                'system_status': 'Enhanced RAG Active'
            }
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת סטטיסטיקות: {e}")
            return {
                'status': 'error',
                'error': str(e)
            } 