"""
Search Services - Handles different search strategies
Extracted from RAGService to reduce coupling and improve maintainability
"""

import time
import re
import logging
from typing import List, Dict, Any, Optional
from supabase import Client

from .embedding_service import EmbeddingService

try:
    from ...config.rag_config import get_search_config, get_database_config
except ImportError:
    from src.ai.config.rag_config import get_search_config, get_database_config

logger = logging.getLogger(__name__)

class SearchService:
    """
    Service for handling different search strategies
    Separated from main RAG service for better modularity
    """
    
    def __init__(self, supabase: Client, embedding_service: EmbeddingService):
        """Initialize search service"""
        self.supabase = supabase
        self.embedding_service = embedding_service
        # Import here to avoid circular imports
        self.search_config = get_search_config()
        self.db_config = get_database_config()
        logger.info("🔍 SearchService initialized")
    
    async def semantic_search(
        self, 
        query: str, 
        document_id: Optional[int] = None,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """בצע חיפוש סמנטי מבוסס embeddings"""
        try:
            logger.info(f"🔍 Starting semantic search for: {query[:50]}...")
            
            # יצירת embedding לשאילתה
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            
            # הגדרת פרמטרים - תיקון שמות הפרמטרים
            match_threshold = getattr(self.search_config, 'SIMILARITY_THRESHOLD', 0.7)
            match_count = max_results or getattr(self.search_config, 'MAX_CHUNKS_RETRIEVED', 10)
            
            # בניית query עם או בלי סינון לפי document_id
            function_name = getattr(self.db_config, 'SEMANTIC_SEARCH_FUNCTION', 'match_documents_semantic')
            
            # תיקון שמות הפרמטרים כדי שיתאימו לפונקציה
            search_params = {
                'query_embedding': query_embedding,
                'match_threshold': match_threshold,    # תוקן מ-similarity_threshold
                'match_count': match_count            # תוקן מ-max_results
            }
            
            if document_id is not None:
                search_params['document_id'] = document_id
                
            response = self.supabase.rpc(function_name, search_params).execute()
            
            if response.data:
                results = response.data
                logger.info(f"✅ Found {len(results)} semantic matches")
                return results
            else:
                logger.warning("⚠️ No semantic search results found")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error in semantic search: {e}")
            return []
    
    async def hybrid_search(
        self, 
        query: str, 
        document_id: Optional[int] = None,
        semantic_weight: Optional[float] = None,
        keyword_weight: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """בצע חיפוש היברידי המשלב חיפוש סמנטי וחיפוש מילות מפתח"""
        try:
            logger.info(f"🔍 Starting hybrid search for: {query[:50]}...")
            
            # יצירת embedding לשאילתה
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            
            # הגדרת משקלים
            sem_weight = semantic_weight or getattr(self.search_config, 'SEMANTIC_WEIGHT', 0.7)
            key_weight = keyword_weight or getattr(self.search_config, 'KEYWORD_WEIGHT', 0.3)
            
            # הגדרת פרמטרים נוספים - תיקון שמות הפרמטרים
            match_threshold = getattr(self.search_config, 'SIMILARITY_THRESHOLD', 0.7)
            match_count = getattr(self.search_config, 'MAX_CHUNKS_RETRIEVED', 10)
            
            # תיקון שם הפונקציה
            function_name = getattr(self.db_config, 'HYBRID_SEARCH_FUNCTION', 'hybrid_search_documents')
            
            # תיקון שמות הפרמטרים כדי שיתאימו לפונקציה
            search_params = {
                'query_embedding': query_embedding,
                'query_text': query,
                'match_threshold': match_threshold,  # תוקן מ-similarity_threshold
                'match_count': match_count,          # תוקן מ-max_results
                'semantic_weight': sem_weight,
                'keyword_weight': key_weight
            }
            
            if document_id is not None:
                search_params['document_id'] = document_id
                
            response = self.supabase.rpc(function_name, search_params).execute()
            
            if response.data:
                results = response.data
                logger.info(f"✅ Found {len(results)} hybrid matches")
                return results
            else:
                logger.warning("⚠️ No hybrid search results found")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error in hybrid search: {e}")
            return []
    
    async def contextual_search(
        self,
        query: str,
        section_filter: Optional[str] = None,
        content_type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """חיפוש קונטקסטואלי עם סינון לפי סעיפים או סוג תוכן"""
        try:
            logger.info(f"🔍 Starting contextual search for: {query[:50]}...")
            
            # יצירת embedding לשאילתה
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            
            # הגדרת פרמטרים - תיקון שמות הפרמטרים
            match_threshold = getattr(self.search_config, 'SIMILARITY_THRESHOLD', 0.7)
            match_count = getattr(self.search_config, 'MAX_CHUNKS_RETRIEVED', 10)
            
            function_name = getattr(self.db_config, 'CONTEXTUAL_SEARCH_FUNCTION', 'contextual_search')
            
            # תיקון שמות הפרמטרים כדי שיתאימו לפונקציה
            search_params = {
                'query_embedding': query_embedding,
                'query_text': query,
                'match_threshold': match_threshold,    # תוקן מ-similarity_threshold
                'match_count': match_count            # תוקן מ-max_results
            }
            
            if section_filter:
                search_params['section_filter'] = section_filter
                
            if content_type_filter:
                search_params['content_type_filter'] = content_type_filter
                
            response = self.supabase.rpc(function_name, search_params).execute()
            
            if response.data:
                results = response.data
                logger.info(f"✅ Found {len(results)} contextual matches")
                return results
            else:
                logger.warning("⚠️ No contextual search results found")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error in contextual search: {e}")
            return []

    async def section_specific_search(
        self,
        query: str,
        target_section: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """חיפוש מותאם לסעיפים ספציפיים"""
        try:
            logger.info(f"🔍 Starting section-specific search for: {query[:50]}...")
            
            # זיהוי סעיף בשאילתה אם לא סופק
            if not target_section:
                section_pattern = r"סעיף\s*(\d+(?:\.\d+)*)"
                match = re.search(section_pattern, query)
                if match:
                    target_section = match.group(1)
                    logger.info(f"🎯 Detected section: {target_section}")
            
            # יצירת embedding לשאילתה
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            
            # הגדרת פרמטרים - תיקון שמות הפרמטרים
            match_threshold = getattr(self.search_config, 'SIMILARITY_THRESHOLD', 0.6)  # נמוך יותר לחיפוש סעיפים
            match_count = getattr(self.search_config, 'MAX_CHUNKS_RETRIEVED', 15)  # יותר תוצאות לחיפוש סעיפים
            
            function_name = getattr(self.db_config, 'SECTION_SEARCH_FUNCTION', 'section_specific_search')
            
            # תיקון שמות הפרמטרים כדי שיתאימו לפונקציה
            search_params = {
                'query_embedding': query_embedding,
                'query_text': query,
                'match_threshold': match_threshold,    # תוקן מ-similarity_threshold
                'match_count': match_count            # תוקן מ-max_results
            }
            
            if target_section:
                search_params['target_section'] = target_section
                
            response = self.supabase.rpc(function_name, search_params).execute()
            
            if response.data:
                results = response.data
                logger.info(f"✅ Found {len(results)} section-specific matches")
                return results
            else:
                logger.warning("⚠️ No section-specific search results found")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error in section-specific search: {e}")
            return []
    
    def get_search_config(self) -> Dict[str, Any]:
        """מחזיר הגדרות החיפוש הנוכחיות"""
        return {
            "similarity_threshold": getattr(self.search_config, 'SIMILARITY_THRESHOLD', 0.7),
            "max_chunks_retrieved": getattr(self.search_config, 'MAX_CHUNKS_RETRIEVED', 10),
            "semantic_weight": getattr(self.search_config, 'SEMANTIC_WEIGHT', 0.7),
            "keyword_weight": getattr(self.search_config, 'KEYWORD_WEIGHT', 0.3),
            "functions": {
                "semantic_search": getattr(self.db_config, 'SEMANTIC_SEARCH_FUNCTION', 'match_documents_semantic'),
                "hybrid_search": getattr(self.db_config, 'HYBRID_SEARCH_FUNCTION', 'hybrid_search_documents'),
                "contextual_search": getattr(self.db_config, 'CONTEXTUAL_SEARCH_FUNCTION', 'contextual_search'),
                "section_search": getattr(self.db_config, 'SECTION_SEARCH_FUNCTION', 'section_specific_search')
            }
        } 