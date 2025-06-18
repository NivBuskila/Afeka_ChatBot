#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supabase-Based Configuration profiles for RAG system optimization
================================================================

This file contains different configuration profiles for optimization and A/B testing.
Each profile is tailored for different types of usage or performance.
Now using Supabase database for storage instead of JSON files.
"""

from dataclasses import dataclass, replace
from typing import Dict, Any, List
import sys
import os
import logging
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the Supabase profile manager
try:
    from supabase_profile_manager import get_supabase_profile_manager
except ImportError:
    try:
        from .supabase_profile_manager import get_supabase_profile_manager
    except ImportError:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "supabase_profile_manager",
            os.path.join(os.path.dirname(__file__), "supabase_profile_manager.py")
        )
        supabase_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(supabase_module)
        get_supabase_profile_manager = supabase_module.get_supabase_profile_manager

try:
    from rag_config import rag_config, RAGConfig
except ImportError:
    from .rag_config import rag_config, RAGConfig

logger = logging.getLogger(__name__)

def load_dynamic_profiles() -> Dict[str, Any]:
    """Load all profiles from Supabase database"""
    try:
        manager = get_supabase_profile_manager()
        profiles = manager.get_all_profiles()
        logger.info(f"📥 Loaded {len(profiles)} profiles from Supabase")
        return profiles
    except Exception as e:
        logger.error(f"❌ Error loading profiles from Supabase: {e}")
        # Return minimal fallback profiles
        return {
            "maximum_accuracy": {
                "id": "maximum_accuracy",
                "name": "Maximum Accuracy",
                "description": "Maximum Accuracy - No performance limits (Target: 98-100%)",
                "config": {
                    "similarityThreshold": 0.65,
                    "maxChunks": 25,
                    "temperature": 0.1,
                    "modelName": "gemini-2.0-flash",
                    "chunkSize": 1500,
                    "chunkOverlap": 200,
                    "maxContextTokens": 8000,
                    "targetTokensPerChunk": 300,
                    "hybridSemanticWeight": 0.7,
                    "hybridKeywordWeight": 0.3
                },
                "characteristics": {
                    "focus": "Maximum accuracy and comprehensive results",
                    "expectedSpeed": "Slow",
                    "expectedQuality": "Highest",
                    "bestFor": "Critical questions requiring highest accuracy",
                    "tradeoffs": "Slower response time for maximum accuracy"
                },
                "isActive": True,
                "isCustom": True
            }
        }

def save_dynamic_profiles(profiles_data: Dict[str, Any]) -> None:
    """Save all profiles to Supabase database"""
    try:
        manager = get_supabase_profile_manager()
        
        saved_count = 0
        for profile_key, profile_data in profiles_data.items():
            if manager.save_profile(profile_key, profile_data):
                saved_count += 1
            else:
                logger.warning(f"⚠️ Failed to save profile: {profile_key}")
        
        logger.info(f"💾 Saved {saved_count}/{len(profiles_data)} profiles to Supabase")
        
    except Exception as e:
        logger.error(f"❌ Error saving profiles to Supabase: {e}")

def load_hidden_profiles() -> List[str]:
    """Get the list of hidden profiles from Supabase"""
    try:
        manager = get_supabase_profile_manager()
        hidden = manager.get_hidden_profiles()
        logger.info(f"🔒 Retrieved {len(hidden)} hidden profiles from Supabase")
        return hidden
    except Exception as e:
        logger.error(f"❌ Error getting hidden profiles from Supabase: {e}")
        # Return fallback hidden profiles
        return ["fast", "improved"]  # Default hidden profiles

def save_hidden_profiles(hidden_list: List[str]) -> None:
    """Save the list of hidden profiles to Supabase"""
    try:
        manager = get_supabase_profile_manager()
        
        # First, set all profiles as visible
        all_profiles = manager.get_all_profiles()
        for profile_key in all_profiles.keys():
            manager.set_profile_hidden(profile_key, False)
        
        # Then set specified profiles as hidden
        hidden_count = 0
        for profile_key in hidden_list:
            if manager.set_profile_hidden(profile_key, True):
                hidden_count += 1
            else:
                logger.warning(f"⚠️ Failed to hide profile: {profile_key}")
        
        logger.info(f"🔒 Set {hidden_count}/{len(hidden_list)} profiles as hidden in Supabase")
        
    except Exception as e:
        logger.error(f"❌ Error saving hidden profiles to Supabase: {e}")

def hide_builtin_profile(profile_id: str) -> bool:
    """Hides a built-in profile from the available list"""
    try:
        built_in_profiles = {"high_quality", "fast", "balanced", "improved", "debug", 
                            "enhanced_testing", "optimized_testing", "maximum_accuracy"}
        
        if profile_id not in built_in_profiles:
            return False
        
        hidden_profiles = load_hidden_profiles()
        
        if profile_id not in hidden_profiles:
            hidden_profiles.append(profile_id)
            save_hidden_profiles(hidden_profiles)
        
        return True
    except Exception as e:
        print(f"Error hiding built-in profile {profile_id}: {e}")
        return False

def restore_builtin_profile(profile_id: str) -> bool:
    """Restores a hidden built-in profile"""
    try:
        hidden_profiles = load_hidden_profiles()
        
        if profile_id in hidden_profiles:
            hidden_profiles.remove(profile_id)
            save_hidden_profiles(hidden_profiles)
            return True
        
        return False
    except Exception as e:
        print(f"Error restoring built-in profile {profile_id}: {e}")
        return False

def create_profile_from_data(profile_data: Dict[str, Any]) -> RAGConfig:
    """Creates RAGConfig from saved profile data"""
    config = RAGConfig()
    
    config_data = profile_data.get('config', {})
    
    config.search.SIMILARITY_THRESHOLD = float(config_data.get("similarityThreshold", 0.4))
    config.search.MAX_CHUNKS_RETRIEVED = int(config_data.get("maxChunks", 15))
    config.search.MAX_CHUNKS_FOR_CONTEXT = int(config_data.get("maxChunks", 15))
    config.llm.TEMPERATURE = float(config_data.get("temperature", 0.1))
    config.llm.MODEL_NAME = config_data.get("modelName", "gemini-2.0-flash")
    
    if "chunkSize" in config_data:
        config.chunk.DEFAULT_CHUNK_SIZE = int(config_data["chunkSize"])
    if "chunkOverlap" in config_data:
        config.chunk.DEFAULT_CHUNK_OVERLAP = int(config_data["chunkOverlap"])
    if "maxContextTokens" in config_data:
        config.context.MAX_CONTEXT_TOKENS = int(config_data["maxContextTokens"])
    if "targetTokensPerChunk" in config_data:
        config.chunk.TARGET_TOKENS_PER_CHUNK = int(config_data["targetTokensPerChunk"])
    if "hybridSemanticWeight" in config_data:
        config.search.HYBRID_SEMANTIC_WEIGHT = float(config_data["hybridSemanticWeight"])
    if "hybridKeywordWeight" in config_data:
        config.search.HYBRID_KEYWORD_WEIGHT = float(config_data["hybridKeywordWeight"])
    
    return config

dynamic_profiles_data = load_dynamic_profiles()

def get_high_quality_profile() -> RAGConfig:
    """Profile for maximum quality - high accuracy, lower speed"""
    config = RAGConfig()
    
    config.search.SIMILARITY_THRESHOLD = 0.70  
    config.search.HIGH_QUALITY_THRESHOLD = 0.85
    config.search.MAX_CHUNKS_RETRIEVED = 15  
    config.search.MAX_CHUNKS_FOR_CONTEXT = 10  
    config.search.HYBRID_SEMANTIC_WEIGHT = 0.8  
    config.search.HYBRID_KEYWORD_WEIGHT = 0.2
    
    config.chunk.DEFAULT_CHUNK_SIZE = 1500
    config.chunk.DEFAULT_CHUNK_OVERLAP = 300
    config.chunk.TARGET_TOKENS_PER_CHUNK = 300
    
    config.context.MAX_CONTEXT_TOKENS = 8000
    config.context.RESERVED_TOKENS_FOR_RESPONSE = 2000
    
    config.llm.TEMPERATURE = 0.05  
    config.llm.MAX_OUTPUT_TOKENS = 3000 
    
    return config

def get_fast_profile() -> RAGConfig:
    """Profile for maximum speed - good performance, reasonable quality"""
    config = RAGConfig()
    
    config.search.SIMILARITY_THRESHOLD = 0.45
    config.search.MAX_CHUNKS_RETRIEVED = 8
    config.search.MAX_CHUNKS_FOR_CONTEXT = 5
    config.search.HYBRID_SEMANTIC_WEIGHT = 0.6
    config.search.HYBRID_KEYWORD_WEIGHT = 0.4
    
    config.chunk.DEFAULT_CHUNK_SIZE = 2500
    config.chunk.DEFAULT_CHUNK_OVERLAP = 150
    config.chunk.TARGET_TOKENS_PER_CHUNK = 400
    
    config.context.MAX_CONTEXT_TOKENS = 4000
    config.context.RESERVED_TOKENS_FOR_RESPONSE = 1000
    
    config.llm.TEMPERATURE = 0.2  
    config.llm.MAX_OUTPUT_TOKENS = 1500  
    
    config.performance.TARGET_SEARCH_TIME_MS = 1000 
    config.performance.TARGET_GENERATION_TIME_MS = 2000
    
    return config

def get_balanced_profile() -> RAGConfig:
    """Balanced profile - good balance between quality and speed"""
    config = RAGConfig()
    
    config.search.SIMILARITY_THRESHOLD = 0.4  
    config.search.MAX_CHUNKS_RETRIEVED = 20   
    config.search.MAX_CHUNKS_FOR_CONTEXT = 12 
    
    config.chunk.DEFAULT_CHUNK_SIZE = 1500   
    config.chunk.DEFAULT_CHUNK_OVERLAP = 300 
    
    config.llm.TEMPERATURE = 0.1
    
    return config

def get_improved_profile() -> RAGConfig:
    """Profile based on manual testing analysis - optimized for missing sections"""
    config = RAGConfig()
    
    config.search.SIMILARITY_THRESHOLD = 0.3  
    config.search.HIGH_QUALITY_THRESHOLD = 0.6
    config.search.MAX_CHUNKS_RETRIEVED = 25   
    config.search.MAX_CHUNKS_FOR_CONTEXT = 15 
    
    config.search.HYBRID_SEMANTIC_WEIGHT = 0.9  
    config.search.HYBRID_KEYWORD_WEIGHT = 0.1   
    
    config.chunk.DEFAULT_CHUNK_SIZE = 1000   
    config.chunk.DEFAULT_CHUNK_OVERLAP = 400 
    config.chunk.TARGET_TOKENS_PER_CHUNK = 200 
    
    config.context.MAX_CONTEXT_TOKENS = 10000
    config.context.RESERVED_TOKENS_FOR_RESPONSE = 3000
    
    config.llm.TEMPERATURE = 0.05
    config.llm.MAX_OUTPUT_TOKENS = 3000
    
    return config

def get_debug_profile() -> RAGConfig:
    """Profile for testing and development - detailed logs, low thresholds"""
    config = RAGConfig()
    
    config.search.SIMILARITY_THRESHOLD = 0.30
    config.search.MAX_CHUNKS_RETRIEVED = 20  
    config.search.MAX_CHUNKS_FOR_CONTEXT = 10
    
    config.optimization.ENABLE_DETAILED_LOGGING = True
    config.performance.LOG_SEARCH_ANALYTICS = True
    config.performance.LOG_PERFORMANCE_METRICS = True
    
    config.search.SEARCH_TIMEOUT_SECONDS = 60
    config.llm.GENERATION_TIMEOUT_SECONDS = 120
    
    return config

def get_enhanced_testing_profile() -> RAGConfig:
    """Enhanced aggressive testing profile based on findings analysis"""
    config = RAGConfig()
    
    config.search.SIMILARITY_THRESHOLD = 0.15  
    config.search.HIGH_QUALITY_THRESHOLD = 0.5 
    config.search.MAX_CHUNKS_RETRIEVED = 40   
    config.search.MAX_CHUNKS_FOR_CONTEXT = 25 
    
    config.chunk.DEFAULT_CHUNK_SIZE = 600     
    config.chunk.DEFAULT_CHUNK_OVERLAP = 300  
    config.chunk.TARGET_TOKENS_PER_CHUNK = 120  
    
    config.search.HYBRID_SEMANTIC_WEIGHT = 0.7   
    config.search.HYBRID_KEYWORD_WEIGHT = 0.3    
    
    config.context.MAX_CONTEXT_TOKENS = 15000    
    config.context.RESERVED_TOKENS_FOR_RESPONSE = 4000  
    config.context.CONTEXT_OVERLAP_TOKENS = 200  
    
    config.llm.TEMPERATURE = 0.02  
    config.llm.MAX_OUTPUT_TOKENS = 5000  
    
    config.optimization.ENABLE_DETAILED_LOGGING = True
    config.performance.LOG_SEARCH_ANALYTICS = True
    config.performance.LOG_PERFORMANCE_METRICS = True
    config.performance.TARGET_SEARCH_TIME_MS = 5000  
    config.performance.TARGET_GENERATION_TIME_MS = 8000
    
    config.search.SEARCH_TIMEOUT_SECONDS = 120 
    config.llm.GENERATION_TIMEOUT_SECONDS = 240
    
    config.search.USE_QUERY_EXPANSION = True
    config.search.ENABLE_FUZZY_MATCHING = True
    config.optimization.ENABLE_CHUNK_RERANKING = True
    
    return config

def get_optimized_testing_profile() -> RAGConfig:
    """Optimized profile based on comprehensive error analysis and manual testing"""
    config = RAGConfig()
    
    config.search.SIMILARITY_THRESHOLD = 0.12
    config.search.HIGH_QUALITY_THRESHOLD = 0.6
    config.search.MAX_CHUNKS_RETRIEVED = 25
    config.search.MAX_CHUNKS_FOR_CONTEXT = 20
    
    config.chunk.DEFAULT_CHUNK_SIZE = 700
    config.chunk.DEFAULT_CHUNK_OVERLAP = 350
    config.chunk.TARGET_TOKENS_PER_CHUNK = 140
    
    config.search.HYBRID_SEMANTIC_WEIGHT = 0.65
    config.search.HYBRID_KEYWORD_WEIGHT = 0.35
    
    config.context.MAX_CONTEXT_TOKENS = 12000
    config.context.RESERVED_TOKENS_FOR_RESPONSE = 3500
    config.context.CONTEXT_OVERLAP_TOKENS = 250
    
    config.llm.TEMPERATURE = 0.03
    config.llm.MAX_OUTPUT_TOKENS = 4000
    
    config.performance.TARGET_SEARCH_TIME_MS = 2000
    config.performance.TARGET_GENERATION_TIME_MS = 4000
    
    config.optimization.ENABLE_DETAILED_LOGGING = True
    config.performance.LOG_SEARCH_ANALYTICS = True
    config.performance.LOG_PERFORMANCE_METRICS = True
    
    config.search.SEARCH_TIMEOUT_SECONDS = 15
    config.llm.GENERATION_TIMEOUT_SECONDS = 30
    
    return config

def get_maximum_accuracy_profile() -> RAGConfig:
    """Maximum accuracy profile without performance considerations"""
    config = RAGConfig()
    
    config.search.SIMILARITY_THRESHOLD = 0.08
    config.search.HIGH_QUALITY_THRESHOLD = 0.85
    config.search.MAX_CHUNKS_RETRIEVED = 60
    config.search.MAX_CHUNKS_FOR_CONTEXT = 50
    
    config.chunk.DEFAULT_CHUNK_SIZE = 800
    config.chunk.DEFAULT_CHUNK_OVERLAP = 400
    config.chunk.TARGET_TOKENS_PER_CHUNK = 160
    
    config.search.HYBRID_SEMANTIC_WEIGHT = 0.75
    config.search.HYBRID_KEYWORD_WEIGHT = 0.25
    
    config.context.MAX_CONTEXT_TOKENS = 20000
    config.context.RESERVED_TOKENS_FOR_RESPONSE = 6000
    config.context.CONTEXT_OVERLAP_TOKENS = 500
    
    config.llm.TEMPERATURE = 0.01
    config.llm.MAX_OUTPUT_TOKENS = 6000
    config.llm.TOP_P = 0.9
    
    config.performance.TARGET_SEARCH_TIME_MS = 10000
    config.performance.TARGET_GENERATION_TIME_MS = 15000
    
    config.optimization.ENABLE_DETAILED_LOGGING = True
    config.performance.LOG_SEARCH_ANALYTICS = True
    config.performance.LOG_PERFORMANCE_METRICS = True
    config.optimization.ENABLE_CHUNK_RERANKING = True
    
    config.search.SEARCH_TIMEOUT_SECONDS = 300
    config.llm.GENERATION_TIMEOUT_SECONDS = 600
    
    config.search.USE_QUERY_EXPANSION = True
    config.search.ENABLE_FUZZY_MATCHING = True
    config.context.ENABLE_CONTEXT_RERANKING = True
    
    return config

PROFILES = {
    "high_quality": get_high_quality_profile,
    "fast": get_fast_profile,
    "balanced": get_balanced_profile,
    "improved": get_improved_profile,
    "debug": get_debug_profile,
    "enhanced_testing": get_enhanced_testing_profile,
    "optimized_testing": get_optimized_testing_profile,
    "maximum_accuracy": get_maximum_accuracy_profile,
}

# Load dynamic profiles from Supabase
try:
    dynamic_profiles_data = load_dynamic_profiles()
    for profile_id, profile_data in dynamic_profiles_data.items():
        if profile_id not in PROFILES:
            PROFILES[profile_id] = lambda data=profile_data: create_profile_from_data(data)
            logger.info(f"📥 Loaded dynamic profile from Supabase: {profile_id}")
except Exception as e:
    logger.error(f"❌ Error loading dynamic profiles: {e}")
    dynamic_profiles_data = {}

def save_new_profile(profile_id: str, profile_data: Dict[str, Any]) -> bool:
    """Save a new profile to Supabase"""
    try:
        manager = get_supabase_profile_manager()
        success = manager.save_profile(profile_id, profile_data)
        
        if success:
            # Update in-memory profiles
            PROFILES[profile_id] = lambda: create_profile_from_data(profile_data)
            logger.info(f"💾 Saved new profile '{profile_id}' to Supabase")
            return True
        else:
            logger.error(f"❌ Failed to save new profile '{profile_id}' to Supabase")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error saving new profile '{profile_id}' to Supabase: {e}")
        return False

def delete_profile(profile_id: str) -> bool:
    """Delete a profile from Supabase (soft delete)"""
    try:
        # Don't allow deletion of built-in profiles
        built_in_profiles = {"high_quality", "fast", "balanced", "improved", "debug", 
                            "enhanced_testing", "optimized_testing", "maximum_accuracy"}
        
        if profile_id in built_in_profiles:
            logger.warning(f"⚠️ Cannot delete built-in profile: {profile_id}")
            return False
        
        manager = get_supabase_profile_manager()
        success = manager.delete_profile(profile_id)
        
        if success:
            # Remove from in-memory profiles
            if profile_id in PROFILES:
                del PROFILES[profile_id]
            logger.info(f"🗑️ Deleted profile '{profile_id}' from Supabase")
            return True
        else:
            logger.error(f"❌ Failed to delete profile '{profile_id}' from Supabase")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error deleting profile '{profile_id}' from Supabase: {e}")
        return False

def update_dynamic_profile_description(profile_id: str, description: str) -> None:
    """Update the description for a dynamically created profile"""
    global DYNAMIC_PROFILE_DESCRIPTIONS
    DYNAMIC_PROFILE_DESCRIPTIONS[profile_id] = description

def get_profile(profile_name: str) -> RAGConfig:
    """Returns profile by name"""
    if profile_name not in PROFILES:
        available = ", ".join(PROFILES.keys())
        raise ValueError(f"Profile '{profile_name}' does not exist. Available profiles: {available}")
    
    return PROFILES[profile_name]()

def list_profiles() -> Dict[str, str]:
    """Returns list of profiles with descriptions (excluding hidden profiles) from Supabase"""
    try:
        manager = get_supabase_profile_manager()
        profiles = manager.list_available_profiles()
        logger.info(f"📋 Listed {len(profiles)} available profiles from Supabase")
        return profiles
    except Exception as e:
        logger.error(f"❌ Error listing profiles from Supabase: {e}")
        # Fallback to static profiles only
        static_profiles = {
            "high_quality": "Maximum quality - high accuracy, lower speed",
            "fast": "Maximum speed - good performance, reasonable quality",
            "balanced": "Balanced - improved settings based on analysis",
            "improved": "Optimized for missing sections - very low threshold, small chunks",
            "debug": "Debug and development - detailed logs, low thresholds",
            "enhanced_testing": "Enhanced Testing (AGGRESSIVE) - Based on 66.7% failure analysis",
            "optimized_testing": "Optimized Testing - Balanced performance & accuracy (73.3% analysis)",
            "maximum_accuracy": "Maximum Accuracy - No performance limits (Target: 98-100%)",
        }
        return static_profiles

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
    
    profiles_info = list_profiles()
    for name, description in profiles_info.items():
        print(f"\n📋 {name.upper()}:")
        print(f"   {description}")
        
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