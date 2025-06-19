#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG System Configuration
========================

Central configuration file for the RAG system.
Modifying values here will affect the entire system uniformly.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class SearchConfig:
    """Search configuration for RAG system"""
    
    # 🔥 AGGRESSIVE TUNING - Much lower thresholds for more results
    SIMILARITY_THRESHOLD: float = 0.15  # ⬇️ Much lower for more matches
    HIGH_QUALITY_THRESHOLD: float = 0.85
    LOW_QUALITY_THRESHOLD: float = 0.40  # ⬇️ Lower to catch more results
    SECTION_SEARCH_THRESHOLD: float = 0.08  # ⬇️ Very aggressive for sections
    
    # 🔥 AGGRESSIVE TUNING - More chunks for better coverage
    MAX_CHUNKS_RETRIEVED: int = 70  # ⬆️ Much more content
    MAX_CHUNKS_FOR_CONTEXT: int = 12  # ⬆️ More context
    MAX_RESULTS_EXTENDED: int = 50  # ⬆️ More extended results
    
    # 🔥 AGGRESSIVE TUNING - Favor keyword search over semantic
    HYBRID_SEMANTIC_WEIGHT: float = 0.2  # ⬇️ Less semantic
    HYBRID_KEYWORD_WEIGHT: float = 0.8  # ⬆️ Strong keyword focus
    
    SEARCH_TIMEOUT_SECONDS: int = 30
    EMBEDDING_TIMEOUT_SECONDS: int = 15
    
    # 🔥 AGGRESSIVE TUNING - Higher bonuses for exact matches
    EXACT_PHRASE_BONUS: float = 500.0  # ⬆️ Huge bonus for exact phrases
    TOPIC_MATCH_BONUS: float = 25.0  # ⬆️ Better topic matching
    DIRECT_MATCH_BONUS: float = 15.0  # ⬆️ Better direct matching
    SIMILARITY_WEIGHT_FACTOR: float = 1.0  # ⬇️ Less emphasis on similarity
    POSITION_BONUS_BASE: float = 5.0  # ⬆️ Better position bonus
    POSITION_BONUS_DECAY: float = 0.3  # ⬇️ Slower decay


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
    
    # Default similarity thresholds for document processor
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
class ContextConfig:
    """Context building configuration for LLM"""
    
    MAX_CONTEXT_TOKENS: int = 6000
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
    MAIN_CONTENT_RATIO: float = 0.6  # Main content can take up to 60% of available space
    BACKGROUND_RATIO: float = 0.6    # Background info can take up to 60% of remaining space
    ADDITIONAL_INFO_RATIO: float = 0.4  # Additional info ratio
    
    # Relevance extraction parameters
    RELEVANT_SEGMENT_MAX_LENGTH: int = 500
    SEGMENT_CONTEXT_WINDOW: int = 50  # Characters around relevant text


@dataclass
class LLMConfig:
    """Language model configuration"""
    
    MODEL_NAME: str = "gemini-2.0-flash"
    TEMPERATURE: float = 0.1
    MAX_OUTPUT_TOKENS: int = 2048
    
    SAFETY_SETTINGS: Dict[str, str] = field(default_factory=lambda: {
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE", 
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
    })
    
    GENERATION_TIMEOUT_SECONDS: int = 45


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
    
    # Token estimation parameters
    TOKEN_ESTIMATION_MULTIPLIER: float = 1.3  # Multiplier for converting words to tokens
    HEBREW_TOKEN_RATIO: float = 0.75  # Hebrew words to tokens ratio
    
    # Context processing parameters
    CONTEXT_TRIM_THRESHOLD: float = 0.8  # When to start trimming context (80% full)
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_BASE: int = 5  # Base seconds for exponential backoff


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
        """Returns all configuration as dictionary for saving or debugging"""
        return {
            "search": self.search.__dict__,
            "embedding": self.embedding.__dict__,
            "chunk": self.chunk.__dict__,
            "context": {
                **self.context.__dict__,
                "available_context_tokens": self.context.AVAILABLE_CONTEXT_TOKENS
            },
            "llm": self.llm.__dict__,
            "database": self.database.__dict__,
            "performance": self.performance.__dict__,
            "optimization": self.optimization.__dict__
        }
    
    def validate_config(self) -> List[str]:
        """Validates configuration settings"""
        errors = []
        
        if not 0.0 <= self.search.SIMILARITY_THRESHOLD <= 1.0:
            errors.append("SIMILARITY_THRESHOLD must be between 0.0 and 1.0")
        
        if not 0.0 <= self.search.SECTION_SEARCH_THRESHOLD <= 1.0:
            errors.append("SECTION_SEARCH_THRESHOLD must be between 0.0 and 1.0")
        
        if self.search.HYBRID_SEMANTIC_WEIGHT + self.search.HYBRID_KEYWORD_WEIGHT != 1.0:
            errors.append("HYBRID_SEMANTIC_WEIGHT + HYBRID_KEYWORD_WEIGHT must equal 1.0")
        
        if self.chunk.MIN_CHUNK_SIZE > self.chunk.MAX_CHUNK_SIZE:
            errors.append("MIN_CHUNK_SIZE cannot be greater than MAX_CHUNK_SIZE")
        
        if self.performance.TOKEN_ESTIMATION_MULTIPLIER <= 0:
            errors.append("TOKEN_ESTIMATION_MULTIPLIER must be positive")
        
        if self.performance.HEBREW_TOKEN_RATIO <= 0:
            errors.append("HEBREW_TOKEN_RATIO must be positive")
        
        if self.chunk.MIN_CHUNK_SIZE >= self.chunk.MAX_CHUNK_SIZE:
            errors.append("MIN_CHUNK_SIZE must be less than MAX_CHUNK_SIZE")
        
        if self.context.AVAILABLE_CONTEXT_TOKENS <= 0:
            errors.append("AVAILABLE_CONTEXT_TOKENS must be positive")
        
        total_weight = self.search.HYBRID_SEMANTIC_WEIGHT + self.search.HYBRID_KEYWORD_WEIGHT
        if abs(total_weight - 1.0) > 0.01:
            errors.append("Hybrid search weights must sum to 1.0")
        
        return errors


rag_config = RAGConfig()

config_errors = rag_config.validate_config()
if config_errors:
    print("⚠️ RAG Configuration Errors:")
    for error in config_errors:
        print(f"  - {error}")
    print("Please fix the configuration in rag_config.py")


def get_search_config() -> SearchConfig:
    """Returns search configuration"""
    return rag_config.search

def get_embedding_config() -> EmbeddingConfig:
    """Returns embedding configuration"""
    return rag_config.embedding

def get_chunk_config() -> ChunkConfig:
    """Returns chunk configuration"""
    return rag_config.chunk

def get_context_config() -> ContextConfig:
    """Returns context configuration"""
    return rag_config.context

def get_llm_config() -> LLMConfig:
    """Returns LLM configuration"""
    return rag_config.llm

def get_database_config() -> DatabaseConfig:
    """Returns database configuration"""
    return rag_config.database

def get_performance_config() -> PerformanceConfig:
    """Returns performance configuration"""
    return rag_config.performance

def get_optimization_config() -> OptimizationConfig:
    """Returns optimization configuration"""
    return rag_config.optimization


if __name__ == "__main__":
    print("🔧 RAG System Configuration:")
    print("=" * 50)
    
    config_dict = rag_config.get_config_dict()
    for section, settings in config_dict.items():
        print(f"\n📋 {section.upper()}:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    
    print(f"\n✅ Configuration valid: {len(config_errors) == 0}")