"""
מודול חיפוש מתקדם (Advanced Retrieval) לתקנוני מכללה
מממש את השלב השלישי בתוכנית האסטרטגית: Multi-Stage Retrieval עם Re-ranking
"""

import re
import logging
import asyncio
from typing import List, Dict, Any, Tuple, Optional, Union
from dataclasses import dataclass
import numpy as np
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

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """תוצאת חיפוש מורחבת"""
    chunk_id: int
    chunk_text: str
    section_number: str
    section_title: str
    hierarchical_path: str
    content_type: str
    keywords: List[str]
    cross_references: List[str]
    similarity_score: float
    exact_match_bonus: float
    hierarchy_relevance: float
    recency_factor: float
    final_score: float
    search_stage: str  # exact, semantic, hierarchical, keyword

@dataclass
class ContextBundle:
    """חבילת קונטקסט מלא למענה"""
    main_result: SearchResult
    hierarchical_context: List[SearchResult]
    related_subsections: List[SearchResult]
    cross_referenced_content: List[SearchResult]
    definition_context: List[SearchResult]
    total_context_length: int

class AdvancedRetriever:
    """מחלק מתקדם לחיפוש רב-שלבי עם re-ranking חכם"""
    
    def __init__(self):
        self.supabase = get_supabase_client() if has_supabase else None
        self.embedding_service = EmbeddingService() if has_supabase else None
        
        # משקלים לחישוב הציון הסופי
        self.scoring_weights = {
            'semantic_similarity': 0.4,
            'exact_match_bonus': 0.3,
            'hierarchy_relevance': 0.2,
            'recency_factor': 0.1
        }
        
        # דפוסי זיהוי שאלות על מספרי סעיפים
        self.section_query_patterns = [
            r'סעיף\s+(\d+(?:\.\d+)*)',
            r'(\d+(?:\.\d+)*)\s*(?:\.|\-|\s)',
            r'פרק\s+(\d+)',
            r'תקנה\s+(\d+(?:\.\d+)*)'
        ]
        
        # מילות מפתח לזיהוי סוג השאלה
        self.query_type_keywords = {
            'temporal': ['מתי', 'מועד', 'תאריך', 'זמן', 'שנה', 'סמסטר'],
            'procedural': ['איך', 'כיצד', 'תהליך', 'הליך', 'בקשה'],
            'definitional': ['מה זה', 'הגדרה', 'משמעות', 'פירוש'],
            'comparative': ['הבדל', 'השוואה', 'בין', 'לעומת'],
            'conditional': ['אם', 'במקרה', 'תנאי', 'כאשר']
        }

    async def multi_stage_search(self, 
                                query: str, 
                                max_results: int = 10,
                                semantic_threshold: float = 0.8) -> List[SearchResult]:
        """חיפוש רב-שלבי מתקדם"""
        
        logger.info(f"מתחיל חיפוש רב-שלבי עבור: '{query}'")
        
        all_results = []
        
        # Stage 1: Exact Match - חיפוש ישיר על מספרי סעיפים
        exact_results = await self._exact_match_search(query)
        all_results.extend(exact_results)
        logger.info(f"Stage 1 (Exact): {len(exact_results)} תוצאות")
        
        # Stage 2: Semantic Search - חיפוש סמנטי
        if len(all_results) < max_results:
            semantic_results = await self._semantic_search(query, semantic_threshold, max_results - len(all_results))
            all_results.extend(semantic_results)
            logger.info(f"Stage 2 (Semantic): {len(semantic_results)} תוצאות")
        
        # Stage 3: Hierarchical Expansion - הרחבה היררכית
        if len(all_results) < max_results and exact_results:
            hierarchical_results = await self._hierarchical_expansion(exact_results, max_results - len(all_results))
            all_results.extend(hierarchical_results)
            logger.info(f"Stage 3 (Hierarchical): {len(hierarchical_results)} תוצאות")
        
        # Stage 4: Keyword Fallback - חיפוש מילות מפתח
        if len(all_results) < max_results:
            keyword_results = await self._keyword_fallback(query, max_results - len(all_results))
            all_results.extend(keyword_results)
            logger.info(f"Stage 4 (Keyword): {len(keyword_results)} תוצאות")
        
        # Re-ranking - דירוג מחדש
        ranked_results = self._rerank_results(all_results, query)
        
        # הסרת כפילויות והחזרת התוצאות הטובות ביותר
        unique_results = self._remove_duplicates(ranked_results)
        final_results = unique_results[:max_results]
        
        logger.info(f"סיים חיפוש רב-שלבי: {len(final_results)} תוצאות סופיות")
        return final_results

    async def _exact_match_search(self, query: str) -> List[SearchResult]:
        """חיפוש ישיר על מספרי סעיפים"""
        if not self.supabase:
            return []
        
        results = []
        
        # זיהוי מספרי סעיפים בשאלה
        for pattern in self.section_query_patterns:
            matches = re.findall(pattern, query, re.UNICODE)
            for section_number in matches:
                try:
                    # חיפוש ישיר במסד הנתונים
                    response = self.supabase.rpc(
                        'find_section_number',
                        {'query': section_number}
                    ).execute()
                    
                    if response.data:
                        for row in response.data:
                            chunk_data = await self._get_chunk_details(row['chunk_id'])
                            if chunk_data:
                                result = SearchResult(
                                    chunk_id=row['chunk_id'],
                                    chunk_text=chunk_data['chunk_text'],
                                    section_number=chunk_data['section_number'] or '',
                                    section_title=chunk_data['section_title'] or '',
                                    hierarchical_path=chunk_data['hierarchical_path'] or '',
                                    content_type=chunk_data['content_type'],
                                    keywords=chunk_data['keywords'] or [],
                                    cross_references=chunk_data['cross_references'] or [],
                                    similarity_score=row['similarity'],
                                    exact_match_bonus=1.0,
                                    hierarchy_relevance=0.5,
                                    recency_factor=0.5,
                                    final_score=0.0,  # יחושב ב-rerank
                                    search_stage='exact'
                                )
                                results.append(result)
                except Exception as e:
                    logger.error(f"שגיאה בחיפוש ישיר: {e}")
        
        return results

    async def _semantic_search(self, query: str, threshold: float, limit: int) -> List[SearchResult]:
        """חיפוש סמנטי באמצעות embeddings"""
        if not self.supabase or not self.embedding_service:
            return []
        
        try:
            # יצירת embedding לשאלה
            query_embedding = await self.embedding_service.create_embedding(query)
            
            # חיפוש סמנטי במסד הנתונים
            response = self.supabase.rpc(
                'semantic_search_advanced',
                {
                    'query_embedding': query_embedding,
                    'similarity_threshold': threshold,
                    'max_results': limit
                }
            ).execute()
            
            results = []
            if response.data:
                for row in response.data:
                    result = SearchResult(
                        chunk_id=row['chunk_id'],
                        chunk_text=row['chunk_text'],
                        section_number=row['section_number'] or '',
                        section_title=row['section_title'] or '',
                        hierarchical_path=row['hierarchical_path'] or '',
                        content_type=row['content_type'],
                        keywords=row['keywords'] or [],
                        cross_references=row['cross_references'] or [],
                        similarity_score=row['similarity_score'],
                        exact_match_bonus=0.0,
                        hierarchy_relevance=0.5,
                        recency_factor=0.5,
                        final_score=0.0,
                        search_stage='semantic'
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"שגיאה בחיפוש סמנטי: {e}")
            return []

    async def _hierarchical_expansion(self, base_results: List[SearchResult], limit: int) -> List[SearchResult]:
        """הרחבה היררכית - הבאת סעיפים קשורים"""
        if not self.supabase or not base_results:
            return []
        
        results = []
        
        for base_result in base_results[:3]:  # רק 3 התוצאות הטובות ביותר
            try:
                # חיפוש סעיפים באותו פרק או בהיררכיה דומה
                if base_result.hierarchical_path:
                    path_parts = base_result.hierarchical_path.split(' > ')
                    if len(path_parts) > 1:
                        parent_path = ' > '.join(path_parts[:-1])
                        
                        response = self.supabase.table('advanced_document_chunks')\
                            .select('*')\
                            .ilike('hierarchical_path', f'{parent_path}%')\
                            .limit(5)\
                            .execute()
                        
                        if response.data:
                            for row in response.data:
                                if row['id'] != base_result.chunk_id:  # לא לכלול את הresult המקורי
                                    result = SearchResult(
                                        chunk_id=row['id'],
                                        chunk_text=row['chunk_text'],
                                        section_number=row['section_number'] or '',
                                        section_title=row['section_title'] or '',
                                        hierarchical_path=row['hierarchical_path'] or '',
                                        content_type=row['content_type'],
                                        keywords=row['keywords'] or [],
                                        cross_references=row['cross_references'] or [],
                                        similarity_score=0.6,  # ציון בינוני
                                        exact_match_bonus=0.0,
                                        hierarchy_relevance=1.0,  # ציון גבוה לרלוונטיות היררכית
                                        recency_factor=0.5,
                                        final_score=0.0,
                                        search_stage='hierarchical'
                                    )
                                    results.append(result)
                
                # חיפוש סעיפים המופיעים בהפניות צולבות
                if base_result.cross_references:
                    for cross_ref in base_result.cross_references[:3]:
                        response = self.supabase.table('advanced_document_chunks')\
                            .select('*')\
                            .eq('section_number', cross_ref)\
                            .limit(2)\
                            .execute()
                        
                        if response.data:
                            for row in response.data:
                                result = SearchResult(
                                    chunk_id=row['id'],
                                    chunk_text=row['chunk_text'],
                                    section_number=row['section_number'] or '',
                                    section_title=row['section_title'] or '',
                                    hierarchical_path=row['hierarchical_path'] or '',
                                    content_type=row['content_type'],
                                    keywords=row['keywords'] or [],
                                    cross_references=row['cross_references'] or [],
                                    similarity_score=0.7,
                                    exact_match_bonus=0.0,
                                    hierarchy_relevance=0.8,
                                    recency_factor=0.5,
                                    final_score=0.0,
                                    search_stage='hierarchical'
                                )
                                results.append(result)
                
            except Exception as e:
                logger.error(f"שגיאה בהרחבה היררכית: {e}")
        
        return results[:limit]

    async def _keyword_fallback(self, query: str, limit: int) -> List[SearchResult]:
        """חיפוש fallback על מילות מפתח"""
        if not self.supabase:
            return []
        
        try:
            # ניקוי השאלה וחילוץ מילות מפתח
            clean_query = re.sub(r'[^\u05D0-\u05EA\u0590-\u05FF0-9a-zA-Z\s]', ' ', query)
            keywords = [word for word in clean_query.split() if len(word) > 2]
            
            results = []
            
            for keyword in keywords[:5]:  # מקסימום 5 מילות מפתח
                response = self.supabase.table('advanced_document_chunks')\
                    .select('*')\
                    .or_(f'chunk_text.ilike.%{keyword}%,keywords.cs.{{{keyword}}}')\
                    .limit(3)\
                    .execute()
                
                if response.data:
                    for row in response.data:
                        result = SearchResult(
                            chunk_id=row['id'],
                            chunk_text=row['chunk_text'],
                            section_number=row['section_number'] or '',
                            section_title=row['section_title'] or '',
                            hierarchical_path=row['hierarchical_path'] or '',
                            content_type=row['content_type'],
                            keywords=row['keywords'] or [],
                            cross_references=row['cross_references'] or [],
                            similarity_score=0.4,
                            exact_match_bonus=0.0,
                            hierarchy_relevance=0.3,
                            recency_factor=0.5,
                            final_score=0.0,
                            search_stage='keyword'
                        )
                        results.append(result)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"שגיאה בחיפוש מילות מפתח: {e}")
            return []

    def _rerank_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """דירוג מחדש של התוצאות עם חישוב ציון סופי"""
        
        query_type = self._classify_query_type(query)
        
        for result in results:
            # התאמת משקלים לפי סוג השאלה
            weights = self.scoring_weights.copy()
            
            if query_type == 'temporal' and result.content_type == 'temporal':
                weights['semantic_similarity'] = 0.5
                weights['hierarchy_relevance'] = 0.1
            elif query_type == 'procedural' and result.content_type == 'procedure':
                weights['semantic_similarity'] = 0.5
                weights['hierarchy_relevance'] = 0.1
            elif query_type == 'definitional' and result.content_type == 'definition':
                weights['semantic_similarity'] = 0.6
                weights['exact_match_bonus'] = 0.2
            
            # חישוב ציון סופי
            result.final_score = (
                result.similarity_score * weights['semantic_similarity'] +
                result.exact_match_bonus * weights['exact_match_bonus'] +
                result.hierarchy_relevance * weights['hierarchy_relevance'] +
                result.recency_factor * weights['recency_factor']
            )
        
        # מיון לפי ציון סופי
        return sorted(results, key=lambda x: x.final_score, reverse=True)

    def _classify_query_type(self, query: str) -> str:
        """סיווג סוג השאלה"""
        query_lower = query.lower()
        
        for query_type, keywords in self.query_type_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return query_type
        
        return 'general'

    def _remove_duplicates(self, results: List[SearchResult]) -> List[SearchResult]:
        """הסרת כפילויות לפי chunk_id"""
        seen_ids = set()
        unique_results = []
        
        for result in results:
            if result.chunk_id not in seen_ids:
                seen_ids.add(result.chunk_id)
                unique_results.append(result)
        
        return unique_results

    async def _get_chunk_details(self, chunk_id: int) -> Optional[Dict]:
        """קבלת פרטים מלאים של chunk"""
        if not self.supabase:
            return None
        
        try:
            response = self.supabase.table('advanced_document_chunks')\
                .select('*')\
                .eq('id', chunk_id)\
                .single()\
                .execute()
            
            return response.data if response.data else None
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת פרטי chunk: {e}")
            return None

    async def build_context_bundle(self, main_result: SearchResult, query: str) -> ContextBundle:
        """בניית חבילת קונטקסט מלא למענה"""
        
        logger.info(f"בונה חבילת קונטקסט עבור chunk {main_result.chunk_id}")
        
        hierarchical_context = []
        related_subsections = []
        cross_referenced_content = []
        definition_context = []
        
        try:
            # 1. Hierarchical Context - הקשר היררכי
            if main_result.hierarchical_path:
                path_parts = main_result.hierarchical_path.split(' > ')
                if len(path_parts) > 1:
                    parent_path = ' > '.join(path_parts[:-1])
                    
                    response = self.supabase.table('advanced_document_chunks')\
                        .select('*')\
                        .eq('hierarchical_path', parent_path)\
                        .limit(2)\
                        .execute()
                    
                    if response.data:
                        for row in response.data:
                            if row['id'] != main_result.chunk_id:
                                context_result = self._row_to_search_result(row, 'context')
                                hierarchical_context.append(context_result)
            
            # 2. Related Subsections - תתי-סעיפים קשורים
            if main_result.section_number:
                section_pattern = main_result.section_number + "."
                
                response = self.supabase.table('advanced_document_chunks')\
                    .select('*')\
                    .like('section_number', f'{section_pattern}%')\
                    .limit(3)\
                    .execute()
                
                if response.data:
                    for row in response.data:
                        if row['id'] != main_result.chunk_id:
                            subsection_result = self._row_to_search_result(row, 'subsection')
                            related_subsections.append(subsection_result)
            
            # 3. Cross-Referenced Content - תוכן מהפניות צולבות
            if main_result.cross_references:
                for cross_ref in main_result.cross_references[:3]:
                    response = self.supabase.table('advanced_document_chunks')\
                        .select('*')\
                        .eq('section_number', cross_ref)\
                        .limit(2)\
                        .execute()
                    
                    if response.data:
                        for row in response.data:
                            cross_ref_result = self._row_to_search_result(row, 'cross_reference')
                            cross_referenced_content.append(cross_ref_result)
            
            # 4. Definition Context - הגדרות רלוונטיות
            response = self.supabase.table('advanced_document_chunks')\
                .select('*')\
                .eq('content_type', 'definition')\
                .limit(3)\
                .execute()
            
            if response.data:
                for row in response.data:
                    definition_result = self._row_to_search_result(row, 'definition')
                    definition_context.append(definition_result)
            
        except Exception as e:
            logger.error(f"שגיאה בבניית חבילת קונטקסט: {e}")
        
        # חישוב אורך קונטקסט כולל
        total_length = (
            len(main_result.chunk_text) +
            sum(len(r.chunk_text) for r in hierarchical_context) +
            sum(len(r.chunk_text) for r in related_subsections) +
            sum(len(r.chunk_text) for r in cross_referenced_content) +
            sum(len(r.chunk_text) for r in definition_context)
        )
        
        context_bundle = ContextBundle(
            main_result=main_result,
            hierarchical_context=hierarchical_context,
            related_subsections=related_subsections,
            cross_referenced_content=cross_referenced_content,
            definition_context=definition_context,
            total_context_length=total_length
        )
        
        logger.info(f"חבילת קונטקסט נבנתה: {total_length} תווים כולל")
        return context_bundle

    def _row_to_search_result(self, row: Dict, stage: str) -> SearchResult:
        """המרת שורה ממסד הנתונים ל-SearchResult"""
        return SearchResult(
            chunk_id=row['id'],
            chunk_text=row['chunk_text'],
            section_number=row['section_number'] or '',
            section_title=row['section_title'] or '',
            hierarchical_path=row['hierarchical_path'] or '',
            content_type=row['content_type'],
            keywords=row['keywords'] or [],
            cross_references=row['cross_references'] or [],
            similarity_score=0.5,
            exact_match_bonus=0.0,
            hierarchy_relevance=0.8,
            recency_factor=0.5,
            final_score=0.6,
            search_stage=stage
        ) 