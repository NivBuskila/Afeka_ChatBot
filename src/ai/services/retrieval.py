"""
מודול חיפוש מתקדם (Advanced Retrieval) לתקנוני מכללה
מממש את השלב השלישי בתוכנית האסטרטגית: Multi-Stage Retrieval עם Re-ranking
"""

import re
import logging
import asyncio
from typing import List, Dict, Any, Tuple, Optional, Union
from dataclasses import dataclass

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
        
        # Re-ranking - דירוג מחדש
        ranked_results = self._rerank_results(all_results, query)
        
        # הסרת כפילויות והחזרת התוצאות הטובות ביותר
        unique_results = self._remove_duplicates(ranked_results)
        final_results = unique_results[:max_results]
        
        logger.info(f"סיים חיפוש רב-שלבי: {len(final_results)} תוצאות סופיות")
        return final_results

    async def _exact_match_search(self, query: str) -> List[SearchResult]:
        """חיפוש ישיר על מספרי סעיפים"""
        results = []
        # מימוש בסיסי - יורחב בהמשך
        return results

    async def _semantic_search(self, query: str, threshold: float, limit: int) -> List[SearchResult]:
        """חיפוש סמנטי באמצעות embeddings"""
        results = []
        # מימוש בסיסי - יורחב בהמשך
        return results

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