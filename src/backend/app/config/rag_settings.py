"""Minimal RAG system configuration settings for Phase 1"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, Any, List, Optional
import os


class RAGSettings(BaseSettings):
    """Minimal RAG system configuration for Phase 1"""
    
    # === Embedding Configuration ===
    embedding_model: str = Field(
        default="models/embedding-001",
        description="Gemini embedding model name"
    )
    embedding_dimension: int = Field(
        default=768,
        description="Embedding vector dimension"
    )
    
    # === Search Configuration ===
    search_similarity_threshold: float = Field(
        default=0.55,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold for search results"
    )
    search_max_chunks_retrieved: int = Field(
        default=12,
        ge=1,
        le=50,
        description="Maximum number of chunks to retrieve"
    )
    search_max_chunks_for_context: int = Field(
        default=8,
        ge=1,
        le=20,
        description="Maximum chunks to include in LLM context"
    )
    
    # === Document Chunking Configuration ===
    chunk_default_size: int = Field(
        default=2000,
        ge=100,
        le=8000,
        description="Default chunk size in characters"
    )
    chunk_overlap: int = Field(
        default=200,
        ge=0,
        le=1000,
        description="Overlap between consecutive chunks"
    )
    
    # === LLM Configuration ===
    llm_model_name: str = Field(
        default="gemini-2.0-flash",
        description="LLM model for answer generation"
    )
    llm_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="LLM temperature for response generation"
    )
    llm_max_output_tokens: int = Field(
        default=2048,
        ge=100,
        description="Maximum output tokens for LLM response"
    )
    
    # === Performance Configuration ===
    perf_enable_embedding_cache: bool = Field(
        default=True,
        description="Enable embedding result caching"
    )
    perf_log_search_analytics: bool = Field(
        default=True,
        description="Enable search analytics logging"
    )

    class Config:
        env_file = ".env"
        env_prefix = "RAG_"
        case_sensitive = False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for logging/debugging"""
        return {
            "embedding": {
                "model": self.embedding_model,
                "dimension": self.embedding_dimension
            },
            "search": {
                "similarity_threshold": self.search_similarity_threshold,
                "max_chunks": self.search_max_chunks_retrieved
            },
            "chunking": {
                "default_size": self.chunk_default_size,
                "overlap": self.chunk_overlap
            },
            "llm": {
                "model": self.llm_model_name,
                "temperature": self.llm_temperature,
                "max_tokens": self.llm_max_output_tokens
            }
        }


# Factory function for creating RAG settings
def create_rag_settings() -> RAGSettings:
    """Create RAG settings"""
    return RAGSettings()


# Global instance for easy access
try:
    rag_settings = create_rag_settings()
except Exception:
    # Create with defaults if environment loading fails
    rag_settings = RAGSettings() 