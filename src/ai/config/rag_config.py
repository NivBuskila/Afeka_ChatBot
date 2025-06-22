#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG System Configuration
========================

Central configuration file for the RAG system.
All values are configurable through profiles - NO MAGIC NUMBERS!
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class SearchConfig:
    """Search configuration for RAG system - All values configurable by profiles"""
    
    # Core search thresholds
    SIMILARITY_THRESHOLD: float = 0.3  # Will be overridden by profiles
    HIGH_QUALITY_THRESHOLD: float = 0.85
    LOW_QUALITY_THRESHOLD: float = 0.40
    SECTION_SEARCH_THRESHOLD: float = 0.25
    
    # Result limits
    MAX_CHUNKS_RETRIEVED: int = 15  # Will be overridden by profiles
    MAX_CHUNKS_FOR_CONTEXT: int = 8
    MAX_RESULTS_EXTENDED: int = 25
    
    # Hybrid search weights
    HYBRID_SEMANTIC_WEIGHT: float = 0.6  # Will be overridden by profiles
    HYBRID_KEYWORD_WEIGHT: float = 0.4   # Will be overridden by profiles
    
    # Timeouts
    SEARCH_TIMEOUT_SECONDS: int = 30
    EMBEDDING_TIMEOUT_SECONDS: int = 15
    
    # Scoring bonuses
    EXACT_PHRASE_BONUS: float = 50.0
    TOPIC_MATCH_BONUS: float = 10.0
    DIRECT_MATCH_BONUS: float = 5.0
    SIMILARITY_WEIGHT_FACTOR: float = 2.0
    POSITION_BONUS_BASE: float = 2.0
    POSITION_BONUS_DECAY: float = 0.5


@dataclass
class LLMConfig:
    """Language model configuration"""
    
    MODEL_NAME: str = "gemini-2.0-flash"
    TEMPERATURE: float = 0.1  # Will be overridden by profiles
    MAX_OUTPUT_TOKENS: int = 2048  # Will be overridden by profiles
    
    # 🆕 System Instructions Support - Now using centralized prompts
    USE_SYSTEM_INSTRUCTION: bool = True
    
    SAFETY_SETTINGS: Dict[str, str] = field(default_factory=lambda: {
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE", 
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
    })
    
    GENERATION_TIMEOUT_SECONDS: int = 45
    
    def get_system_instruction(self, context_vars: Optional[Dict[str, Any]] = None) -> str:
        """יוצר system instruction מותאם לפרופיל עם משתנים דינמיים - now using centralized prompts"""
        if not self.USE_SYSTEM_INSTRUCTION:
            return ""
        
        try:
            # Try multiple import paths
            try:
                from .system_prompts import get_main_system_prompt
            except ImportError:
                from src.ai.config.system_prompts import get_main_system_prompt
            
            return get_main_system_prompt()
        except Exception as e:
            print(f"⚠️ Failed to import centralized system prompt: {e}")
            # Import error - return fallback
            return "You are an expert academic assistant for Afeka College of Engineering in Tel Aviv."


@dataclass
class ContextConfig:
    """Context building configuration for LLM"""
    
    MAX_CONTEXT_TOKENS: int = 6000  # Will be overridden by profiles
    RESERVED_TOKENS_FOR_QUERY: int = 500
    RESERVED_TOKENS_FOR_RESPONSE: int = 1500
    
    @property
    def AVAILABLE_CONTEXT_TOKENS(self) -> int:
        return (self.MAX_CONTEXT_TOKENS - 
                self.RESERVED_TOKENS_FOR_QUERY - 
                self.RESERVED_TOKENS_FOR_RESPONSE)
    
    INCLUDE_CITATIONS: bool = True
    INCLUDE_CHUNK_HEADERS: bool = True
    INCLUDE_PAGE_NUMBERS: bool = True
    
    CHUNK_SEPARATOR: str = "\n\n---\n\n"
    CITATION_SEPARATOR: str = " | "
    
    # Context assembly ratios
    MAIN_CONTENT_RATIO: float = 0.6
    BACKGROUND_RATIO: float = 0.6
    ADDITIONAL_INFO_RATIO: float = 0.4
    
    # Relevance extraction parameters
    RELEVANT_SEGMENT_MAX_LENGTH: int = 500
    SEGMENT_CONTEXT_WINDOW: int = 50


@dataclass
class EmbeddingConfig:
    """Embedding generation configuration"""
    
    MODEL_NAME: str = "models/embedding-001"
    TASK_TYPE_DOCUMENT: str = "retrieval_document"
    TASK_TYPE_QUERY: str = "retrieval_query"
    
    EMBEDDING_DIMENSION: int = 768
    BATCH_SIZE: int = 10
    MAX_INPUT_LENGTH: int = 8192
    
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: float = 1.0
    
    DEFAULT_SIMILARITY_THRESHOLD: float = 0.78
    DEFAULT_HYBRID_THRESHOLD: float = 0.78


@dataclass
class ChunkConfig:
    """Document chunking configuration"""
    
    DEFAULT_CHUNK_SIZE: int = 2000
    MIN_CHUNK_SIZE: int = 100
    MAX_CHUNK_SIZE: int = 4000
    
    DEFAULT_CHUNK_OVERLAP: int = 200
    MIN_CHUNK_OVERLAP: int = 50
    MAX_CHUNK_OVERLAP: int = 500
    
    MAX_CHUNKS_PER_DOCUMENT: int = 500
    MIN_CHUNKS_PER_DOCUMENT: int = 1
    
    MAX_TOKENS_PER_CHUNK: int = 512
    TARGET_TOKENS_PER_CHUNK: int = 350
    MIN_TOKENS_PER_CHUNK: int = 50


@dataclass
class DatabaseConfig:
    """Database configuration"""
    
    DOCUMENTS_TABLE: str = "documents"
    CHUNKS_TABLE: str = "document_chunks"
    ANALYTICS_TABLE: str = "search_analytics"
    
    SEMANTIC_SEARCH_FUNCTION: str = "match_documents_semantic"
    HYBRID_SEARCH_FUNCTION: str = "hybrid_search_documents"
    CONTEXTUAL_SEARCH_FUNCTION: str = "contextual_search"
    ANALYTICS_FUNCTION: str = "log_search_analytics"
    LOG_ANALYTICS_FUNCTION: str = "log_search_analytics"
    
    MAX_CONNECTIONS: int = 20
    CONNECTION_TIMEOUT: int = 30


@dataclass
class PerformanceConfig:
    """Performance configuration"""
    
    MAX_SEARCH_TIME_MS: int = 5000
    MAX_EMBEDDING_TIME_MS: int = 3000
    MAX_GENERATION_TIME_MS: int = 8000
    
    TARGET_SEARCH_TIME_MS: int = 2000
    TARGET_EMBEDDING_TIME_MS: int = 1000
    TARGET_GENERATION_TIME_MS: int = 4000
    
    ENABLE_EMBEDDING_CACHE: bool = True
    EMBEDDING_CACHE_SIZE: int = 1000
    EMBEDDING_CACHE_TTL_SECONDS: int = 3600
    
    LOG_SEARCH_ANALYTICS: bool = True
    LOG_PERFORMANCE_METRICS: bool = True
    
    TOKEN_ESTIMATION_MULTIPLIER: float = 1.3
    HEBREW_TOKEN_RATIO: float = 0.75
    
    CONTEXT_TRIM_THRESHOLD: float = 0.8
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_BASE: int = 5


@dataclass
class OptimizationConfig:
    """Optimization configuration"""
    
    ENABLE_AB_TESTING: bool = False
    AB_TEST_SPLIT_RATIO: float = 0.5
    
    ENABLE_DETAILED_LOGGING: bool = True
    LOG_SEARCH_ANALYTICS: bool = True
    LOG_PERFORMANCE_METRICS: bool = True
    
    AUTO_ADJUST_THRESHOLDS: bool = False
    MIN_SEARCH_RESULTS_FOR_ADJUSTMENT: int = 100


class RAGConfig:
    """Main RAG configuration class"""
    
    def __init__(self):
        self.search = SearchConfig()
        self.embedding = EmbeddingConfig()
        self.chunk = ChunkConfig()
        self.context = ContextConfig()
        self.llm = LLMConfig()
        self.database = DatabaseConfig()
        self.performance = PerformanceConfig()
        self.optimization = OptimizationConfig()

    def get_config_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the current configuration"""
        config_dict = {}
        
        # Add all dataclass configs
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, '__dataclass_fields__'):
                config_dict[attr_name] = {
                    field.name: getattr(attr, field.name) 
                    for field in attr.__dataclass_fields__.values()
                }
        
        return config_dict

    def validate_config(self) -> List[str]:
        """Validate the configuration and return any issues"""
        issues = []
        
        # Validate search config
        if self.search.SIMILARITY_THRESHOLD < 0 or self.search.SIMILARITY_THRESHOLD > 1:
            issues.append("SIMILARITY_THRESHOLD must be between 0 and 1")
        
        if self.search.MAX_CHUNKS_RETRIEVED <= 0:
            issues.append("MAX_CHUNKS_RETRIEVED must be positive")
        
        # Validate LLM config
        if self.llm.TEMPERATURE < 0 or self.llm.TEMPERATURE > 2:
            issues.append("TEMPERATURE must be between 0 and 2")
            
        if self.llm.MAX_OUTPUT_TOKENS <= 0:
            issues.append("MAX_OUTPUT_TOKENS must be positive")
        
        # Validate context config
        if self.context.MAX_CONTEXT_TOKENS <= 0:
            issues.append("MAX_CONTEXT_TOKENS must be positive")
        
        return issues


# Global instances
rag_config = RAGConfig()

def get_search_config() -> SearchConfig:
    return rag_config.search

def get_embedding_config() -> EmbeddingConfig:
    return rag_config.embedding

def get_chunk_config() -> ChunkConfig:
    return rag_config.chunk

def get_context_config() -> ContextConfig:
    return rag_config.context

def get_llm_config() -> LLMConfig:
    return rag_config.llm

def get_database_config() -> DatabaseConfig:
    return rag_config.database

def get_performance_config() -> PerformanceConfig:
    return rag_config.performance

def get_optimization_config() -> OptimizationConfig:
    return rag_config.optimization


if __name__ == "__main__":
    print("🔧 RAG System Configuration:")
    print("=" * 50)
    
    config_dict = rag_config.get_config_dict()
    for section, settings in config_dict.items():
        print(f"\n📋 {section.upper()}:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    
    print(f"\n✅ Configuration valid: {len(rag_config.validate_config()) == 0}")