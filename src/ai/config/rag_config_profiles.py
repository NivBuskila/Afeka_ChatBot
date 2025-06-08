#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration profiles for RAG system optimization
=================================================

This file contains different configuration profiles for optimization and A/B testing.
Each profile is tailored for different types of usage or performance.
"""

from dataclasses import dataclass, replace
from typing import Dict, Any, List
import sys
import os
import json
from pathlib import Path

# הוספת נתיב לטעינת config
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from rag_config import rag_config, RAGConfig
except ImportError:
    # ניסיון יחסי
    from .rag_config import rag_config, RAGConfig

# נתיב לקובץ הפרופילים הדינמיים
DYNAMIC_PROFILES_FILE = Path(current_dir) / "dynamic_profiles.json"

# Global dictionary to store descriptions for dynamically created profiles
DYNAMIC_PROFILE_DESCRIPTIONS = {}

def load_dynamic_profiles() -> Dict[str, Any]:
    """טוען פרופילים דינמיים מקובץ JSON"""
    if not DYNAMIC_PROFILES_FILE.exists():
        return {}
    
    try:
        with open(DYNAMIC_PROFILES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading dynamic profiles: {e}")
        return {}

def save_dynamic_profiles(profiles_data: Dict[str, Any]) -> None:
    """שומר פרופילים דינמיים לקובץ JSON"""
    try:
        with open(DYNAMIC_PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(profiles_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving dynamic profiles: {e}")

def load_hidden_profiles() -> List[str]:
    """טוען רשימת פרופילים מובנים מוסתרים"""
    hidden_file = Path(current_dir) / "hidden_profiles.json"
    try:
        if hidden_file.exists():
            with open(hidden_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('hidden_profiles', [])
        return []
    except Exception as e:
        print(f"Error loading hidden profiles: {e}")
        return []

def save_hidden_profiles(hidden_list: List[str]) -> None:
    """שומר רשימת פרופילים מובנים מוסתרים"""
    hidden_file = Path(current_dir) / "hidden_profiles.json"
    try:
        data = {'hidden_profiles': hidden_list}
        with open(hidden_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving hidden profiles: {e}")

def hide_builtin_profile(profile_id: str) -> bool:
    """מסתיר פרופיל מובנה מהרשימה הזמינה"""
    try:
        # וודא שזה פרופיל מובנה
        built_in_profiles = {"high_quality", "fast", "balanced", "improved", "debug", 
                            "enhanced_testing", "optimized_testing", "maximum_accuracy"}
        
        if profile_id not in built_in_profiles:
            return False  # לא פרופיל מובנה
        
        # טען רשימת מוסתרים נוכחית
        hidden_profiles = load_hidden_profiles()
        
        # הוסף לרשימה אם לא קיים
        if profile_id not in hidden_profiles:
            hidden_profiles.append(profile_id)
            save_hidden_profiles(hidden_profiles)
        
        return True
    except Exception as e:
        print(f"Error hiding built-in profile {profile_id}: {e}")
        return False

def restore_builtin_profile(profile_id: str) -> bool:
    """משחזר פרופיל מובנה מוסתר"""
    try:
        hidden_profiles = load_hidden_profiles()
        
        if profile_id in hidden_profiles:
            hidden_profiles.remove(profile_id)
            save_hidden_profiles(hidden_profiles)
            return True
        
        return False  # לא היה מוסתר
    except Exception as e:
        print(f"Error restoring built-in profile {profile_id}: {e}")
        return False

def create_profile_from_data(profile_data: Dict[str, Any]) -> RAGConfig:
    """יוצר RAGConfig מנתוני פרופיל שמורים"""
    config = RAGConfig()
    
    # Apply configuration from saved data
    config_data = profile_data.get('config', {})
    
    config.search.SIMILARITY_THRESHOLD = float(config_data.get("similarityThreshold", 0.4))
    config.search.MAX_CHUNKS_RETRIEVED = int(config_data.get("maxChunks", 15))
    config.search.MAX_CHUNKS_FOR_CONTEXT = int(config_data.get("maxChunks", 15))
    config.llm.TEMPERATURE = float(config_data.get("temperature", 0.1))
    config.llm.MODEL_NAME = config_data.get("modelName", "gemini-2.0-flash")
    
    # Optional advanced configurations
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

# טען פרופילים דינמיים בעת האתחול
dynamic_profiles_data = load_dynamic_profiles()

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


# Profile 6: Enhanced Testing - Based on chunking analysis (AGGRESSIVE)
def get_enhanced_testing_profile() -> RAGConfig:
    """
    פרופיל משופר אגרסיבי לבדיקה בהתבסס על ניתוח ממצאים
    מתקן בעיות chunking strategy ושיפור זיהוי סעיפים קשורים
    ** UPDATED BASED ON 66.7% FAILURE ANALYSIS **
    """
    config = RAGConfig()
    
    # 🚨 פרמטרים אגרסיביים מהניתוח החדש
    config.search.SIMILARITY_THRESHOLD = 0.15  # הנמכה דרמטית מ-0.2 ל-0.15!
    config.search.HIGH_QUALITY_THRESHOLD = 0.5  # הנמכה גם כאן
    config.search.MAX_CHUNKS_RETRIEVED = 40   # הגדלה מ-30 ל-40 לפי הממצאים
    config.search.MAX_CHUNKS_FOR_CONTEXT = 25 # הגדלה מ-20 ל-25 לטיפול בסעיפים מפוצלים
    
    # 🔧 שיפור אגרסיבי של Chunking Strategy
    config.chunk.DEFAULT_CHUNK_SIZE = 600     # קטן יותר מ-800 לזיהוי סעיפים בודדים
    config.chunk.DEFAULT_CHUNK_OVERLAP = 300  # overlap גבוה מאוד מ-200 ל-300
    config.chunk.TARGET_TOKENS_PER_CHUNK = 120  # פחות טוקנים מ-160 ל-120
    
    # 🎯 שיפור חיפוש semantic עם דגש על keyword
    config.search.HYBRID_SEMANTIC_WEIGHT = 0.7   # הנמכה מ-0.85 ל-0.7
    config.search.HYBRID_KEYWORD_WEIGHT = 0.3    # הגדלה מ-0.15 ל-0.3 לזיהוי מספרי סעיפים
    
    # 📊 הגדלת קונטקסט מקסימלית
    config.context.MAX_CONTEXT_TOKENS = 15000    # הגדלה מ-12000 ל-15000
    config.context.RESERVED_TOKENS_FOR_RESPONSE = 4000  # מ-3000 ל-4000
    config.context.CONTEXT_OVERLAP_TOKENS = 200  # הגדלה מ-100 ל-200
    
    # 🎯 הגדרות LLM מותאמות לדיוק מקסימלי
    config.llm.TEMPERATURE = 0.02  # הנמכה מ-0.05 ל-0.02
    config.llm.MAX_OUTPUT_TOKENS = 5000  # הגדלה מ-4000 ל-5000
    
    # 🔍 הגדרות ביצועים עם זמנים גמישים יותר
    config.optimization.ENABLE_DETAILED_LOGGING = True
    config.performance.LOG_SEARCH_ANALYTICS = True
    config.performance.LOG_PERFORMANCE_METRICS = True
    config.performance.TARGET_SEARCH_TIME_MS = 5000  # הגדלה מ-3000 ל-5000
    config.performance.TARGET_GENERATION_TIME_MS = 8000  # הגדלה מ-5000 ל-8000
    
    # ⏱️ timeouts מותאמים לעיבוד מורכב מאוד
    config.search.SEARCH_TIMEOUT_SECONDS = 120  # הגדלה מ-90 ל-120
    config.llm.GENERATION_TIMEOUT_SECONDS = 240  # הגדלה מ-180 ל-240
    
    # 🎛️ הגדרות נוספות לשיפור חיפוש
    config.search.USE_QUERY_EXPANSION = True  # הוספה
    config.search.ENABLE_FUZZY_MATCHING = True  # הוספה
    config.optimization.ENABLE_CHUNK_RERANKING = True  # הוספה
    
    return config


# Profile 7: Optimized Testing - Based on comprehensive bug analysis
def get_optimized_testing_profile() -> RAGConfig:
    """
    פרופיל מותאם על בסיס ניתוח שגיאות מקיף ובדיקה ידנית
    מתקן בעיות טכניות ומשפר ביצועים לקבלת 90%+ דיוק
    ** CREATED BASED ON DETAILED 73.3% ANALYSIS **
    """
    config = RAGConfig()
    
    # 🎯 הגדרות חיפוש מותאמות לניתוח החדש
    config.search.SIMILARITY_THRESHOLD = 0.12   # נמוך מאוד לתפוס גם סעיפים קשים
    config.search.HIGH_QUALITY_THRESHOLD = 0.6   # סף איכות סביר
    config.search.MAX_CHUNKS_RETRIEVED = 25      # הורדה מ-40 ל-25 לשיפור מהירות
    config.search.MAX_CHUNKS_FOR_CONTEXT = 20    # הורדה מ-25 ל-20 לאיזון
    
    # 🔧 תיקון chunking לזיהוי סעיפים חסרים (6.2.8, 32.1, 16.1)
    config.chunk.DEFAULT_CHUNK_SIZE = 700        # גדלות אופטימלית
    config.chunk.DEFAULT_CHUNK_OVERLAP = 350     # overlap גבוה מאוד (50%)
    config.chunk.TARGET_TOKENS_PER_CHUNK = 140   # טוקנים מותאמים
    
    # 📈 שיפור איזון semantic/keyword לחיפוש מספרי סעיפים
    config.search.HYBRID_SEMANTIC_WEIGHT = 0.65  # פחות semantic
    config.search.HYBRID_KEYWORD_WEIGHT = 0.35   # יותר keyword לסעיפים
    
    # 📊 קונטקסט מאוזן לביצועים וגמישות
    config.context.MAX_CONTEXT_TOKENS = 12000    # הורדה מ-15000 לשיפור מהירות
    config.context.RESERVED_TOKENS_FOR_RESPONSE = 3500  # מאוזן
    config.context.CONTEXT_OVERLAP_TOKENS = 250  # overlap גבוה
    
    # 🎯 LLM מאוזן לדיוק ומהירות
    config.llm.TEMPERATURE = 0.03                # מאוד נמוך לעקביות
    config.llm.MAX_OUTPUT_TOKENS = 4000          # הורדה מ-5000 לשיפור מהירות
    
    # ⚡ ביצועים מותאמים - מטרה: מתחת ל-3 שניות
    config.performance.TARGET_SEARCH_TIME_MS = 2000   # הורדה מ-5000
    config.performance.TARGET_GENERATION_TIME_MS = 4000  # הורדה מ-8000
    
    # 🔍 לוגים מפורטים לניטור איכות
    config.optimization.ENABLE_DETAILED_LOGGING = True
    config.performance.LOG_SEARCH_ANALYTICS = True
    config.performance.LOG_PERFORMANCE_METRICS = True
    
    # 🚀 אופטימיזציות נוספות
    config.search.SEARCH_TIMEOUT_SECONDS = 15   # timeout מאוזן
    config.llm.GENERATION_TIMEOUT_SECONDS = 30   # timeout מאוזן
    
    return config


# Profile 8: Maximum Accuracy - No performance compromises
def get_maximum_accuracy_profile() -> RAGConfig:
    """
    פרופיל לדיוק מקסימלי ללא התחשבות במהירות
    מבוסס על ביצועי שיא של 96.7% - מטרה 98-100%
    ** EXTREME ACCURACY MODE - NO PERFORMANCE LIMITS **
    """
    config = RAGConfig()
    
    # 🎯 הגדרות חיפוש אגרסיביות מקסימליות
    config.search.SIMILARITY_THRESHOLD = 0.08     # סף גבוה יותר לאיכות מקסימלית
    config.search.HIGH_QUALITY_THRESHOLD = 0.85  # גבוה יותר
    config.search.MAX_CHUNKS_RETRIEVED = 60      # מקסימום צ'אנקים אפשרי
    config.search.MAX_CHUNKS_FOR_CONTEXT = 50    # מקסימום בקונטקסט
    
    # 🔧 Chunking אופטימלי לכיסוי מקסימלי
    config.chunk.DEFAULT_CHUNK_SIZE = 800        # גדלות מאוזנת
    config.chunk.DEFAULT_CHUNK_OVERLAP = 400     # 50% overlap מקסימלי
    config.chunk.TARGET_TOKENS_PER_CHUNK = 160   # טוקנים מפורטים
    
    # 📈 איזון לטובת semantic (זיהוי מושגים עמוק)
    config.search.HYBRID_SEMANTIC_WEIGHT = 0.75  # דגש על semantic
    config.search.HYBRID_KEYWORD_WEIGHT = 0.25   # keyword משלים
    
    # 📊 קונטקסט מקסימלי - אפס פשרות
    config.context.MAX_CONTEXT_TOKENS = 20000    # מקסימום גבוה
    config.context.RESERVED_TOKENS_FOR_RESPONSE = 6000  # תשובות מפורטות
    config.context.CONTEXT_OVERLAP_TOKENS = 500  # overlap גבוה מאוד
    
    # 🎯 LLM לדיוק מוחלט
    config.llm.TEMPERATURE = 0.01                # כמעט דטרמיניסטי לחלוטין
    config.llm.MAX_OUTPUT_TOKENS = 6000          # תשובות מקיפות
    config.llm.TOP_P = 0.9                       # דיוק גבוה
    
    # ⚡ ביצועים - מהירות לא רלוונטית
    config.performance.TARGET_SEARCH_TIME_MS = 10000   # 10 שניות - לא משנה
    config.performance.TARGET_GENERATION_TIME_MS = 15000  # 15 שניות - לא משנה
    
    # 🔍 כל האופטימיזציות האפשריות
    config.optimization.ENABLE_DETAILED_LOGGING = True
    config.performance.LOG_SEARCH_ANALYTICS = True
    config.performance.LOG_PERFORMANCE_METRICS = True
    config.optimization.ENABLE_CHUNK_RERANKING = True
    
    # 🚀 timeouts גבוהים לעיבוד מורכב
    config.search.SEARCH_TIMEOUT_SECONDS = 300   # 5 דקות
    config.llm.GENERATION_TIMEOUT_SECONDS = 600  # 10 דקות
    
    # 🎛️ הגדרות מתקדמות לדיוק מקסימלי
    config.search.USE_QUERY_EXPANSION = True     # הרחבת חיפוש
    config.search.ENABLE_FUZZY_MATCHING = True   # התאמה מעורפלת
    config.context.ENABLE_CONTEXT_RERANKING = True  # דירוג מחדש של קונטקסט
    
    return config


# Dictionary of all profiles - חייב להיות לפני הטעינה הדינמית
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

# טוען פרופילים דינמיים מהקובץ ומוסיף אותם ל-PROFILES
for profile_id, profile_data in dynamic_profiles_data.items():
    if profile_id not in PROFILES:  # רק אם לא קיים כבר
        PROFILES[profile_id] = lambda data=profile_data: create_profile_from_data(data)
        DYNAMIC_PROFILE_DESCRIPTIONS[profile_id] = profile_data.get('description', f'Custom profile: {profile_id}')

def save_new_profile(profile_id: str, profile_data: Dict[str, Any]) -> None:
    """שומר פרופיל חדש לקובץ ומוסיף לזיכרון"""
    # Load existing profiles
    existing_profiles = load_dynamic_profiles()
    
    # Add new profile
    existing_profiles[profile_id] = profile_data
    
    # Save to file
    save_dynamic_profiles(existing_profiles)
    
    # Add to memory
    PROFILES[profile_id] = lambda: create_profile_from_data(profile_data)
    DYNAMIC_PROFILE_DESCRIPTIONS[profile_id] = profile_data.get('description', f'Custom profile: {profile_id}')

def delete_profile(profile_id: str) -> bool:
    """מוחק פרופיל (רק פרופילים דינמיים)"""
    # ודא שזה לא פרופיל מובנה
    built_in_profiles = {"high_quality", "fast", "balanced", "improved", "debug", 
                        "enhanced_testing", "optimized_testing", "maximum_accuracy"}
    
    if profile_id in built_in_profiles:
        return False  # לא ניתן למחוק פרופילים מובנים
    
    # Load existing profiles
    existing_profiles = load_dynamic_profiles()
    
    if profile_id in existing_profiles:
        # Remove from file
        del existing_profiles[profile_id]
        save_dynamic_profiles(existing_profiles)
        
        # Remove from memory
        if profile_id in PROFILES:
            del PROFILES[profile_id]
        if profile_id in DYNAMIC_PROFILE_DESCRIPTIONS:
            del DYNAMIC_PROFILE_DESCRIPTIONS[profile_id]
        
        return True
    
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
    """Returns list of profiles with descriptions (excluding hidden profiles)"""
    # Load hidden profiles list
    hidden_profiles = load_hidden_profiles()
    
    # Static profile descriptions
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
    
    # Filter out hidden built-in profiles
    visible_static_profiles = {
        profile_id: description 
        for profile_id, description in static_profiles.items() 
        if profile_id not in hidden_profiles
    }
    
    # Add dynamically created profiles
    dynamic_profiles = {}
    for profile_id in PROFILES.keys():
        if profile_id not in static_profiles:
            # Use stored description if available, otherwise generic description
            description = DYNAMIC_PROFILE_DESCRIPTIONS.get(profile_id, f"Custom profile: {profile_id}")
            dynamic_profiles[profile_id] = description
    
    # Combine visible static and dynamic profiles
    return {**visible_static_profiles, **dynamic_profiles}


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
