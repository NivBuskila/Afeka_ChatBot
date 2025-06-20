#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supabase-Based Current Profile Management System for RAG
========================================================

This system manages the currently active profile for the RAG system
using only Supabase database, replacing JSON file storage.
"""

import logging
import sys
import os
from typing import Dict, Any, Union, Optional

# Add current directory to path for direct imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

try:
    from supabase_profile_manager import get_supabase_profile_manager
except ImportError:
    # Try relative import
    try:
        from .supabase_profile_manager import get_supabase_profile_manager
    except ImportError:
        # Fallback - import from absolute path
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "supabase_profile_manager",
            os.path.join(os.path.dirname(__file__), "supabase_profile_manager.py")
        )
        if spec is not None and spec.loader is not None:
            supabase_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(supabase_module)
            get_supabase_profile_manager = supabase_module.get_supabase_profile_manager
        else:
            # Final fallback - create a dummy function
            logger.error("Failed to load supabase_profile_manager")
            def get_supabase_profile_manager() -> Optional[Any]:
                return None

def get_current_profile() -> str:
    """Returns the current active profile from Supabase"""
    try:
        manager = get_supabase_profile_manager()
        if manager is None:
            logger.warning("⚠️ Supabase profile manager not available, using default")
            return "maximum_accuracy"
        
        profile = manager.get_current_profile()
        logger.info(f"🎯 Retrieved current profile from Supabase: {profile}")
        return profile
    except Exception as e:
        logger.error(f"❌ Error getting current profile from Supabase: {e}")
        return "maximum_accuracy"  # Safe fallback

def set_current_profile(profile_name: str) -> bool:
    """Sets the current active profile in Supabase"""
    try:
        manager = get_supabase_profile_manager()
        if manager is None:
            logger.warning("⚠️ Supabase profile manager not available")
            return False
            
        success = manager.set_current_profile(profile_name)
        if success:
            logger.info(f"✅ Successfully set current profile to: {profile_name}")
            return True
        else:
            logger.error(f"❌ Failed to set current profile to: {profile_name}")
            return False
    except Exception as e:
        logger.error(f"❌ Error setting current profile '{profile_name}': {e}")
        return False

def get_available_profiles() -> Dict[str, str]:
    """Returns a list of all available profiles from Supabase"""
    try:
        manager = get_supabase_profile_manager()
        if manager is None:
            logger.warning("⚠️ Supabase profile manager not available, using fallback")
            return {
                "maximum_accuracy": "Maximum Accuracy - No performance limits (Target: 98-100%)",
                "optimized_testing": "Optimized Testing - Balanced performance & accuracy"
            }
            
        profiles = manager.list_available_profiles()
        logger.info(f"📋 Retrieved {len(profiles)} available profiles from Supabase")
        return profiles
    except Exception as e:
        logger.error(f"❌ Error getting available profiles from Supabase: {e}")
        # Return a basic fallback
        return {
            "maximum_accuracy": "Maximum Accuracy - No performance limits (Target: 98-100%)",
            "optimized_testing": "Optimized Testing - Balanced performance & accuracy"
        }

def get_current_profile_with_validation() -> str:
    """מחזיר פרופיל נוכחי עם וולידציה שהוא קיים"""
    try:
        profile = get_current_profile()
        
        # וולידציה שהפרופיל קיים
        from .rag_config_profiles import PROFILES
        if profile not in PROFILES:
            logger.warning(f"⚠️ Profile '{profile}' not found in available profiles")
            logger.info(f"📋 Available profiles: {list(PROFILES.keys())}")
            
            # שינוי לפרופיל balanced כברירת מחדל
            set_current_profile("balanced")
            return "balanced"
        
        return profile
        
    except Exception as e:
        logger.error(f"❌ Error getting current profile: {e}")
        return "balanced"  # Safe fallback


def validate_profile_config(profile_name: str) -> Dict[str, Any]:
    """בודק שהפרופיל עובד נכון ומחזיר את הההגדרות שלו"""
    try:
        from .rag_config_profiles import get_profile
        config = get_profile(profile_name)
        
        return {
            "valid": True,
            "profile_name": profile_name,
            "similarity_threshold": config.search.SIMILARITY_THRESHOLD,
            "max_chunks": config.search.MAX_CHUNKS_RETRIEVED,
            "temperature": config.llm.TEMPERATURE,
            "use_system_instruction": config.llm.USE_SYSTEM_INSTRUCTION,
            "system_instruction": config.llm.SYSTEM_INSTRUCTION[:100] if config.llm.SYSTEM_INSTRUCTION else "None"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "profile_name": profile_name
        }


def refresh_profiles():
    """Refreshes the list of available profiles - No-op for Supabase version"""
    try:
        # Force refresh by getting a new manager instance
        import importlib
        manager_module = importlib.import_module('.supabase_profile_manager', package='src.ai.config')
        importlib.reload(manager_module)
        logger.info("🔄 Refreshed Supabase profile manager")
    except Exception as e:
        logger.warning(f"⚠️ Could not refresh profiles: {e}")

if __name__ == "__main__":
    print("🔧 Supabase RAG Profile Management")
    print("=" * 50)
    
    current = get_current_profile()
    print(f"Current profile: {current}")
    
    profiles = get_available_profiles()
    print(f"\nAvailable profiles ({len(profiles)}):")
    for name, desc in profiles.items():
        status = "🟢 ACTIVE" if name == current else "⚪"
        print(f"  {status} {name}: {desc}")