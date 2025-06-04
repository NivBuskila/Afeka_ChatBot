#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration profiles for RAG system optimization
=================================================

This file contains different configuration profiles for optimization and A/B testing.
Each profile is tailored for different types of usage or performance.
"""

from dataclasses import dataclass, replace
from typing import Dict, Any
import sys
import os

# הוספת נתיב לטעינת config
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from rag_config import rag_config, RAGConfig
except ImportError:
    # ניסיון יחסי
    from .rag_config import rag_config, RAGConfig


# Profile 1: Maximum quality (for high accuracy)
def get_high_quality_profile() -> RAGConfig:
    """Profile for maximum quality - high accuracy, lower speed"""
    config = RAGConfig()
    
    # Quality search settings
    config.search.SIMILARITY_THRESHOLD = 0.70  # Higher thresholds
    config.search.HIGH_QUALITY_THRESHOLD = 0.85
    config.search.MAX_CHUNKS_RETRIEVED = 15  # More results
    config.search.MAX_CHUNKS_FOR_CONTEXT = 10  # More context
    config.search.HYBRID_SEMANTIC_WEIGHT = 0.8  # Semantic emphasis
    config.search.HYBRID_KEYWORD_WEIGHT = 0.2
    
    # Smaller chunks for accuracy
    config.chunk.DEFAULT_CHUNK_SIZE = 1500
    config.chunk.DEFAULT_CHUNK_OVERLAP = 300
    config.chunk.TARGET_TOKENS_PER_CHUNK = 300
    
    # More context
    config.context.MAX_CONTEXT_TOKENS = 8000
    config.context.RESERVED_TOKENS_FOR_RESPONSE = 2000
    
    # Quality LLM
    config.llm.TEMPERATURE = 0.05  # Very low for consistency
    config.llm.MAX_OUTPUT_TOKENS = 3000  # Longer responses
    
    return config


# Profile 2: Maximum speed (for performance)
def get_fast_profile() -> RAGConfig:
    """Profile for maximum speed - good performance, reasonable quality"""
    config = RAGConfig()
    
    # Fast search settings
    config.search.SIMILARITY_THRESHOLD = 0.45  # Lower thresholds
    config.search.MAX_CHUNKS_RETRIEVED = 8  # Fewer results
    config.search.MAX_CHUNKS_FOR_CONTEXT = 5  # Less context
    config.search.HYBRID_SEMANTIC_WEIGHT = 0.6  # Balance
    config.search.HYBRID_KEYWORD_WEIGHT = 0.4
    
    # Larger chunks
    config.chunk.DEFAULT_CHUNK_SIZE = 2500
    config.chunk.DEFAULT_CHUNK_OVERLAP = 150
    config.chunk.TARGET_TOKENS_PER_CHUNK = 400
    
    # Less context
    config.context.MAX_CONTEXT_TOKENS = 4000
    config.context.RESERVED_TOKENS_FOR_RESPONSE = 1000
    
    # Fast LLM
    config.llm.TEMPERATURE = 0.2  # Slightly more flexibility
    config.llm.MAX_OUTPUT_TOKENS = 1500  # Shorter responses
    
    # Fast performance
    config.performance.TARGET_SEARCH_TIME_MS = 1000  # 1 second target
    config.performance.TARGET_GENERATION_TIME_MS = 2000  # 2 seconds
    
    return config


# Profile 3: Balanced (improved default)
def get_balanced_profile() -> RAGConfig:
    """Balanced profile - good balance between quality and speed"""
    config = RAGConfig()
    
    # Improved settings based on analysis
    config.search.SIMILARITY_THRESHOLD = 0.4  # ⬇️ Lowered from 0.55
    config.search.MAX_CHUNKS_RETRIEVED = 20   # ⬆️ Increased from 12
    config.search.MAX_CHUNKS_FOR_CONTEXT = 12 # ⬆️ Increased from 8
    
    # Smaller chunks for better section detection
    config.chunk.DEFAULT_CHUNK_SIZE = 1500   # ⬇️ Smaller chunks
    config.chunk.DEFAULT_CHUNK_OVERLAP = 300 # ⬆️ More overlap
    
    config.llm.TEMPERATURE = 0.1
    
    return config


# Profile 4: Improved (based on manual analysis)
def get_improved_profile() -> RAGConfig:
    """Profile based on manual testing analysis - optimized for missing sections"""
    config = RAGConfig()
    
    # Very low threshold to catch more sections
    config.search.SIMILARITY_THRESHOLD = 0.3  # Very low to catch all sections
    config.search.HIGH_QUALITY_THRESHOLD = 0.6
    config.search.MAX_CHUNKS_RETRIEVED = 25   # More chunks to analyze
    config.search.MAX_CHUNKS_FOR_CONTEXT = 15 # More context
    
    # Emphasis on semantic search for section numbers
    config.search.HYBRID_SEMANTIC_WEIGHT = 0.9  # Heavy semantic focus
    config.search.HYBRID_KEYWORD_WEIGHT = 0.1   # Less keyword weight
    
    # Small chunks for precise section detection
    config.chunk.DEFAULT_CHUNK_SIZE = 1000   # Very small chunks
    config.chunk.DEFAULT_CHUNK_OVERLAP = 400 # High overlap
    config.chunk.TARGET_TOKENS_PER_CHUNK = 200  # Small token chunks
    
    # More context for complete answers
    config.context.MAX_CONTEXT_TOKENS = 10000
    config.context.RESERVED_TOKENS_FOR_RESPONSE = 3000
    
    # Conservative temperature
    config.llm.TEMPERATURE = 0.05
    config.llm.MAX_OUTPUT_TOKENS = 3000
    
    return config


# Profile 5: Debug and development
def get_debug_profile() -> RAGConfig:
    """Profile for testing and development - detailed logs, low thresholds"""
    config = RAGConfig()
    
    # Low thresholds for testing
    config.search.SIMILARITY_THRESHOLD = 0.30
    config.search.MAX_CHUNKS_RETRIEVED = 20  # Many results for testing
    config.search.MAX_CHUNKS_FOR_CONTEXT = 10
    
    # Detailed logging settings
    config.optimization.ENABLE_DETAILED_LOGGING = True
    config.performance.LOG_SEARCH_ANALYTICS = True
    config.performance.LOG_PERFORMANCE_METRICS = True
    
    # Long timeouts for debugging
    config.search.SEARCH_TIMEOUT_SECONDS = 60
    config.llm.GENERATION_TIMEOUT_SECONDS = 120
    
    return config


# Dictionary of all profiles
PROFILES = {
    "high_quality": get_high_quality_profile,
    "fast": get_fast_profile,
    "balanced": get_balanced_profile,
    "improved": get_improved_profile,
    "debug": get_debug_profile,
}


def get_profile(profile_name: str) -> RAGConfig:
    """Returns profile by name"""
    if profile_name not in PROFILES:
        available = ", ".join(PROFILES.keys())
        raise ValueError(f"Profile '{profile_name}' does not exist. Available profiles: {available}")
    
    return PROFILES[profile_name]()


def list_profiles() -> Dict[str, str]:
    """Returns list of profiles with descriptions"""
    return {
        "high_quality": "Maximum quality - high accuracy, lower speed",
        "fast": "Maximum speed - good performance, reasonable quality",
        "balanced": "Balanced - improved settings based on analysis",
        "improved": "Optimized for missing sections - very low threshold, small chunks",
        "debug": "Debug and development - detailed logs, low thresholds",
    }


def compare_profiles(profile1_name: str, profile2_name: str) -> Dict[str, Any]:
    """Compares two profiles"""
    profile1 = get_profile(profile1_name)
    profile2 = get_profile(profile2_name)
    
    comparison = {
        "similarity_threshold": {
            profile1_name: profile1.search.SIMILARITY_THRESHOLD,
            profile2_name: profile2.search.SIMILARITY_THRESHOLD
        },
        "max_chunks": {
            profile1_name: profile1.search.MAX_CHUNKS_RETRIEVED,
            profile2_name: profile2.search.MAX_CHUNKS_RETRIEVED
        },
        "context_tokens": {
            profile1_name: profile1.context.MAX_CONTEXT_TOKENS,
            profile2_name: profile2.context.MAX_CONTEXT_TOKENS
        },
        "temperature": {
            profile1_name: profile1.llm.TEMPERATURE,
            profile2_name: profile2.llm.TEMPERATURE
        },
        "semantic_weight": {
            profile1_name: profile1.search.HYBRID_SEMANTIC_WEIGHT,
            profile2_name: profile2.search.HYBRID_SEMANTIC_WEIGHT
        }
    }
    
    return comparison


if __name__ == "__main__":
    print("🔧 RAG Configuration Profiles")
    print("=" * 50)
    
    # Display all profiles
    profiles_info = list_profiles()
    for name, description in profiles_info.items():
        print(f"\n📋 {name.upper()}:")
        print(f"   {description}")
        
        # Display key settings
        profile = get_profile(name)
        print(f"   📊 Key settings:")
        print(f"      Similarity threshold: {profile.search.SIMILARITY_THRESHOLD}")
        print(f"      Max chunks: {profile.search.MAX_CHUNKS_RETRIEVED}")
        print(f"      Context tokens: {profile.context.MAX_CONTEXT_TOKENS}")
        print(f"      Temperature: {profile.llm.TEMPERATURE}")
        print(f"      Semantic/Keyword weights: {profile.search.HYBRID_SEMANTIC_WEIGHT}/{profile.search.HYBRID_KEYWORD_WEIGHT}")
    
    print(f"\n📈 Comparison: fast vs high_quality")
    comparison = compare_profiles("fast", "high_quality")
    for metric, values in comparison.items():
        print(f"   {metric}: {values}")
