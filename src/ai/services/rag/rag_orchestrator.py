"""
RAG Orchestrator - Main coordinator for RAG operations
Coordinates all RAG services and maintains backwards compatibility
"""

import os
import time
import re
import logging
from typing import Dict, Any, Optional, List
from supabase import create_client, Client
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (4 levels up from this file)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
if not env_path.exists():
    # Try alternative path if not found
    env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
load_dotenv(env_path)

from .embedding_service import EmbeddingService
from .search_services import SearchService
from .context_builder import ContextBuilder
from .answer_generator import AnswerGenerator
from .search_analytics import SearchAnalytics

logger = logging.getLogger(__name__)

class RAGOrchestrator:
    """Main orchestrator for RAG operations"""
    
    def __init__(self, config_profile: Optional[str] = None, test_mode: bool = False):
        """Initialize RAG Orchestrator with all sub-services"""
        
        # Check for test mode
        self.test_mode = test_mode or os.getenv("RAG_TEST_MODE", "").lower() == "true"
        
        if self.test_mode:
            logger.warning("🧪 RAG Orchestrator running in TEST MODE - some features disabled")
            self.supabase = None
        else:
            # Initialize Supabase connection
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
            
            if not supabase_url or not supabase_key:
                raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
            
            self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Load configuration
        self.profile_name = config_profile or "balanced"
        self._load_configuration()
        
        # Initialize services based on mode
        if self.test_mode:
            # Test mode - minimal initialization
            self.key_manager = None
            self.embedding_service = None
            self.search_service = None
            self.context_builder = None
            self.answer_generator = None
            self.analytics = None
            logger.info("🧪 Test mode: Services not initialized")
        else:
            # Initialize Database Key Manager
            try:
                from ...core.database_key_manager import DatabaseKeyManager
            except ImportError:
                from src.ai.core.database_key_manager import DatabaseKeyManager
            
            self.key_manager = DatabaseKeyManager(use_direct_supabase=True)
            
            # Initialize sub-services
            self.embedding_service = EmbeddingService(self.key_manager)
            self.search_service = SearchService(self.supabase, self.embedding_service)
            self.context_builder = ContextBuilder()
            self.answer_generator = AnswerGenerator(self.key_manager)
            self.analytics = SearchAnalytics(self.supabase)
        
        logger.info(f"🚀 RAGOrchestrator initialized with profile '{self.profile_name}'")
    
    def _load_configuration(self):
        """Load configuration for the specified profile"""
        try:
            from ...config.rag_config_profiles import get_profile, PROFILES
            from ...config.rag_config import (
                get_search_config, get_embedding_config, get_context_config,
                get_llm_config, get_database_config, get_performance_config
            )
        except ImportError:
            from src.ai.config.rag_config_profiles import get_profile, PROFILES
            from src.ai.config.rag_config import (
                get_search_config, get_embedding_config, get_context_config,
                get_llm_config, get_database_config, get_performance_config
            )
        
        try:
            if self.profile_name and self.profile_name in PROFILES:
                profile_config = get_profile(self.profile_name)
                self.search_config = profile_config.search
                self.embedding_config = profile_config.embedding
                self.context_config = profile_config.context
                self.llm_config = profile_config.llm
                self.db_config = profile_config.database
                self.performance_config = profile_config.performance
            else:
                self.search_config = get_search_config()
                self.embedding_config = get_embedding_config()
                self.context_config = get_context_config()
                self.llm_config = get_llm_config()
                self.db_config = get_database_config()
                self.performance_config = get_performance_config()
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")

    # Backwards compatibility methods
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query"""
        return await self.embedding_service.generate_query_embedding(query)
    
    async def semantic_search(self, query: str, document_id=None, max_results=None):
        """Semantic search"""
        return await self.search_service.semantic_search(query, document_id, max_results)
    
    async def hybrid_search(self, query: str, document_id=None, semantic_weight=None, keyword_weight=None):
        """Hybrid search"""
        return await self.search_service.hybrid_search(query, document_id, semantic_weight, keyword_weight)
    
    async def contextual_search(self, query: str, section_filter=None, content_type_filter=None):
        """Contextual search"""
        return await self.search_service.contextual_search(query, section_filter, content_type_filter)
    
    async def section_specific_search(self, query: str, target_section=None):
        """Section-specific search"""
        return await self.search_service.section_specific_search(query, target_section)

    async def generate_answer(self, query: str, search_method: str = 'hybrid', document_id=None):
        """Main method for generating complete RAG answers"""
        start_time = time.time()
        
        # Test mode response
        if self.test_mode:
            return {
                "answer": f"🧪 Test mode response for: {query}",
                "sources": ["Test source"],
                "chunks_selected": [],
                "search_results_count": 1,
                "response_time_ms": 100,
                "search_method": search_method,
                "query": query,
                "test_mode": True
            }
        
        try:
            # Determine search strategy
            section_keywords = ['סעיף', 'בסעיף', 'פרק', 'תקנה']
            is_section_query = any(keyword in query for keyword in section_keywords)
            
            # Execute search
            if is_section_query:
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
                    "answer": "לא נמצא מידע רלוונטי בתקנונים לשאלה זו.",
                    "sources": [],
                    "chunks_selected": [],
                    "search_results_count": 0,
                    "response_time_ms": int((time.time() - start_time) * 1000),
                    "search_method": search_method,
                    "query": query
                }
            
            # Build context
            context, citations, included_chunks = self.context_builder.build_context(search_results)
            
            # Create prompt
            prompt = self.context_builder.create_rag_prompt(query, context)
            
            # Generate answer
            answer = await self.answer_generator.generate_answer(prompt)
            
            # Process citations
            cited_source_numbers = self.context_builder.extract_cited_sources(answer)
            cited_chunks = self.context_builder.get_cited_chunks(included_chunks, cited_source_numbers)
            
            # Clean answer
            clean_answer = re.sub(r'\[מקורות:[^\]]+\]', '', answer).strip()
            
            # Add relevant segments
            for chunk in cited_chunks:
                chunk_text = chunk.get('chunk_text', chunk.get('content', ''))
                if chunk_text:
                    relevant_segment = self.context_builder.extract_relevant_chunk_segment(
                        chunk_text, query, clean_answer, max_length=500
                    )
                    chunk['relevant_segment'] = relevant_segment
            
            response_time = int((time.time() - start_time) * 1000)
            
            # Log analytics
            if self.analytics.is_analytics_enabled():
                await self.analytics.log_search_analytics(
                    query, search_method, len(search_results),
                    search_results[0].get('similarity_score', search_results[0].get('combined_score', 0.0)) if search_results else 0.0,
                    response_time, document_id
                )
            
            result = {
                "answer": clean_answer,
                "sources": citations,
                "chunks_selected": cited_chunks,
                "search_results_count": len(search_results),
                "response_time_ms": response_time,
                "search_method": search_method,
                "query": query,
                "cited_sources": cited_source_numbers
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating answer: {e}")
            raise

    async def get_search_statistics(self, days_back: int = 30):
        """Get search statistics"""
        return await self.analytics.get_search_statistics(days_back)
    
    def get_current_config(self):
        """Get current configuration"""
        return {"profile": self.profile_name}


# Factory function for backwards compatibility
def get_rag_service() -> RAGOrchestrator:
    """Factory function for RAG service"""
    global _rag_service_instance
    if '_rag_service_instance' not in globals():
        globals()['_rag_service_instance'] = RAGOrchestrator()
    return globals()['_rag_service_instance'] 