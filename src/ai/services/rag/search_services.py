"""
Search Services - Handles different search strategies
Extracted from RAGService to reduce coupling and improve maintainability
"""

from __future__ import annotations

import re
import logging
from typing import TYPE_CHECKING, Protocol, TypeVar, cast as type_cast, TypedDict

if TYPE_CHECKING:
    from supabase import Client
else:
    # Runtime import to avoid circular dependency issues if not type checking
    from supabase import Client  # type: ignore

from .embedding_service import EmbeddingService

try:
    from ...config.rag_config import get_search_config, get_database_config
except ImportError:
    from src.ai.config.rag_config import get_search_config, get_database_config  # type: ignore

logger = logging.getLogger(__name__)

# --- Type definitions ---

T = TypeVar("T")

class SearchResult(TypedDict, total=False):
    """More specific type for search results from RPC calls."""
    id: int
    content: str
    metadata: dict[str, object]
    similarity: float
    relevance_score: float
    document_id: int
    chunk_index: int

SearchParams = dict[str, str | int | float | list[float]]

class ConfigProtocol(Protocol):
    """Protocol for configuration objects to ensure type safety."""
    SIMILARITY_THRESHOLD: float
    MAX_CHUNKS_RETRIEVED: int
    SEMANTIC_WEIGHT: float
    KEYWORD_WEIGHT: float
    SEMANTIC_SEARCH_FUNCTION: str
    HYBRID_SEARCH_FUNCTION: str
    CONTEXTUAL_SEARCH_FUNCTION: str
    SECTION_SEARCH_FUNCTION: str

# --- Service Class ---

class SearchService:
    """
    Service for handling different search strategies
    Separated from main RAG service for better modularity
    """
    
    supabase: Client
    embedding_service: EmbeddingService
    search_config: ConfigProtocol
    db_config: ConfigProtocol
    
    def __init__(self, supabase: Client, embedding_service: EmbeddingService) -> None:
        """Initialize search service"""
        self.supabase = supabase
        self.embedding_service = embedding_service
        self.search_config = type_cast(ConfigProtocol, type_cast(object, get_search_config()))
        self.db_config = type_cast(ConfigProtocol, type_cast(object, get_database_config()))
        logger.info("🔍 SearchService initialized")
    
    def _get_config_value(self, config: ConfigProtocol, key: str, default: T) -> T:
        """Safely get configuration value with type preservation."""
        return getattr(config, key, default)
    
    def _execute_rpc(self, function_name: str, params: SearchParams) -> list[SearchResult]:
        """Execute RPC call and safely handle response"""
        try:
            # The supabase-py library has incomplete typings for `rpc`.
            # We cast the result to `object` and ignore the specific member
            # type error to satisfy the strict type checker.
            response = type_cast(object, self.supabase.rpc(function_name, params).execute())  # pyright: ignore [reportUnknownMemberType]
            data = getattr(response, "data", None)

            if data is not None and isinstance(data, list):
                return type_cast(list[SearchResult], data)

            return []

        except Exception as e:
            logger.error(
                f"RPC execution error in '{function_name}': {e}", exc_info=True
            )
            return []
    
    async def semantic_search(
        self, 
        query: str, 
        document_id: int | None = None,
        max_results: int | None = None
    ) -> list[SearchResult]:
        """Performs a semantic search using embeddings."""
        try:
            logger.info(f"Starting semantic search for: {query[:50]}...")
            
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            
            match_threshold = self._get_config_value(self.search_config, 'SIMILARITY_THRESHOLD', 0.7)
            max_chunks = self._get_config_value(self.search_config, 'MAX_CHUNKS_RETRIEVED', 10)
            match_count = max_results if max_results is not None else max_chunks
            
            function_name = self._get_config_value(self.db_config, 'SEMANTIC_SEARCH_FUNCTION', 'match_documents_semantic')
            
            search_params: SearchParams = {
                'query_embedding': query_embedding,
                'match_threshold': match_threshold,
                'match_count': match_count
            }
            
            if document_id is not None:
                search_params['document_id'] = document_id
            
            results = self._execute_rpc(function_name, search_params)
            
            if results:
                logger.info(f"Found {len(results)} semantic matches")
            else:
                logger.warning("No semantic search results found")
                
            return results
                
        except Exception as e:
            logger.error(f"Error in semantic search: {e}", exc_info=True)
            return []
    
    async def hybrid_search(
        self, 
        query: str, 
        document_id: int | None = None,
        semantic_weight: float | None = None,
        keyword_weight: float | None = None
    ) -> list[SearchResult]:
        """Performs a hybrid search combining semantic and keyword search."""
        try:
            logger.info(f"Starting hybrid search for: {query[:50]}...")
            
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            
            sem_weight = semantic_weight if semantic_weight is not None else self._get_config_value(self.search_config, 'SEMANTIC_WEIGHT', 0.7)
            key_weight = keyword_weight if keyword_weight is not None else self._get_config_value(self.search_config, 'KEYWORD_WEIGHT', 0.3)
            match_threshold = self._get_config_value(self.search_config, 'SIMILARITY_THRESHOLD', 0.7)
            match_count = self._get_config_value(self.search_config, 'MAX_CHUNKS_RETRIEVED', 10)
            
            function_name = self._get_config_value(self.db_config, 'HYBRID_SEARCH_FUNCTION', 'hybrid_search_documents')
            
            search_params: SearchParams = {
                'query_embedding': query_embedding,
                'query_text': query,
                'match_threshold': match_threshold,
                'match_count': match_count,
                'semantic_weight': sem_weight,
                'keyword_weight': key_weight
            }
            
            if document_id is not None:
                search_params['document_id'] = document_id
            
            results = self._execute_rpc(function_name, search_params)
            
            if results:
                logger.info(f"Found {len(results)} hybrid matches")
            else:
                logger.warning("No hybrid search results found")
                
            return results
                
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}", exc_info=True)
            return []
    
    async def contextual_search(
        self,
        query: str,
        section_filter: str | None = None,
        content_type_filter: str | None = None
    ) -> list[SearchResult]:
        """Performs a contextual search with filtering."""
        try:
            logger.info(f"Starting contextual search for: {query[:50]}...")
            
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            
            match_threshold = self._get_config_value(self.search_config, 'SIMILARITY_THRESHOLD', 0.7)
            match_count = self._get_config_value(self.search_config, 'MAX_CHUNKS_RETRIEVED', 10)
            function_name = self._get_config_value(self.db_config, 'CONTEXTUAL_SEARCH_FUNCTION', 'contextual_search')
            
            search_params: SearchParams = {
                'query_embedding': query_embedding,
                'query_text': query,
                'match_threshold': match_threshold,
                'match_count': match_count
            }
            
            if section_filter is not None:
                search_params['section_filter'] = section_filter
                
            if content_type_filter is not None:
                search_params['content_type_filter'] = content_type_filter
            
            results = self._execute_rpc(function_name, search_params)
            
            if results:
                logger.info(f"Found {len(results)} contextual matches")
            else:
                logger.warning("No contextual search results found")
                
            return results
                
        except Exception as e:
            logger.error(f"Error in contextual search: {e}", exc_info=True)
            return []

    async def section_specific_search(
        self,
        query: str,
        target_section: str | None = None
    ) -> list[SearchResult]:
        """Performs a search targeted at a specific section."""
        try:
            logger.info(f"Starting section-specific search for: {query[:50]}...")
            
            if not target_section:
                section_pattern = r"סעיף\s*(\d+(?:\.\d+)*)"
                match = re.search(section_pattern, query)
                if match:
                    target_section = match.group(1)
                    logger.info(f"Detected section: {target_section}")
            
            query_embedding = await self.embedding_service.generate_query_embedding(query)
            
            match_threshold = self._get_config_value(self.search_config, 'SIMILARITY_THRESHOLD', 0.6)
            match_count = self._get_config_value(self.search_config, 'MAX_CHUNKS_RETRIEVED', 15)
            function_name = self._get_config_value(self.db_config, 'SECTION_SEARCH_FUNCTION', 'section_specific_search')
            
            search_params: SearchParams = {
                'query_embedding': query_embedding,
                'query_text': query,
                'match_threshold': match_threshold,
                'match_count': match_count
            }
            
            if target_section is not None:
                search_params['target_section'] = target_section
            
            results = self._execute_rpc(function_name, search_params)
            
            if results:
                logger.info(f"Found {len(results)} section-specific matches")
            else:
                logger.warning("No section-specific search results found")
                
            return results
                
        except Exception as e:
            logger.error(
                f"Error in section-specific search: {e}", exc_info=True
            )
            return []
    
    def get_search_config(self) -> dict[str, object]:
        """Returns the current search configuration."""
        return {
            "similarity_threshold": self._get_config_value(
                self.search_config, "SIMILARITY_THRESHOLD", 0.7
            ),
            "max_chunks_retrieved": self._get_config_value(self.search_config, 'MAX_CHUNKS_RETRIEVED', 10),
            "semantic_weight": self._get_config_value(self.search_config, 'SEMANTIC_WEIGHT', 0.7),
            "keyword_weight": self._get_config_value(self.search_config, 'KEYWORD_WEIGHT', 0.3),
            "functions": {
                "semantic_search": self._get_config_value(self.db_config, 'SEMANTIC_SEARCH_FUNCTION', 'match_documents_semantic'),
                "hybrid_search": self._get_config_value(self.db_config, 'HYBRID_SEARCH_FUNCTION', 'hybrid_search_documents'),
                "contextual_search": self._get_config_value(self.db_config, 'CONTEXTUAL_SEARCH_FUNCTION', 'contextual_search'),
                "section_search": self._get_config_value(self.db_config, 'SECTION_SEARCH_FUNCTION', 'section_specific_search')
            }
        } 