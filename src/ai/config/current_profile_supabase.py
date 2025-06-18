#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supabase-Based Current Profile Management System for RAG
========================================================

This system manages the currently active profile for the RAG system
using only Supabase database, replacing JSON file storage.
"""

import logging
from typing import Dict, Any
from .supabase_profile_manager import get_supabase_profile_manager

logger = logging.getLogger(__name__)

def get_current_profile() -> str:
    """Returns the current active profile from Supabase"""
    try:
        manager = get_supabase_profile_manager()
        profile = manager.get_current_profile()
        logger.info(f"Retrieved current profile from Supabase: {profile}")
        return profile
    except Exception as e:
        logger.error(f" Error getting current profile from Supabase: {e}")
        return "maximum_accuracy"  # Safe fallback

def set_current_profile(profile_name: str) -> None:
    """Sets the current active profile in Supabase"""
    try:
        manager = get_supabase_profile_manager()
        success = manager.set_current_profile(profile_name)
        if success:
            logger.info(f"Successfully set current profile to: {profile_name}")
        else:
            logger.error(f"Failed to set current profile to: {profile_name}")
    except Exception as e:
        logger.error(f"Error setting current profile '{profile_name}': {e}")

def get_available_profiles() -> Dict[str, str]:
    """Returns a list of all available profiles from Supabase"""
    try:
        manager = get_supabase_profile_manager()
        profiles = manager.list_available_profiles()
        logger.info(f"Retrieved {len(profiles)} available profiles from Supabase")
        return profiles
    except Exception as e:
        logger.error(f"Error getting available profiles from Supabase: {e}")
        # Return a basic fallback
        return {
            "maximum_accuracy": "Maximum Accuracy - No performance limits (Target: 98-100%)",
            "optimized_testing": "Optimized Testing - Balanced performance & accuracy"
        }

def refresh_profiles():
    """Refreshes the list of available profiles - No-op for Supabase version"""
    try:
        manager = get_supabase_profile_manager()
        # Force refresh by creating a new manager instance
        global _supabase_manager
        _supabase_manager = None
        logger.info("Refreshed Supabase profile manager")
    except Exception as e:
        logger.warning(f" Could not refresh profiles: {e}")

if __name__ == "__main__":
    print("Supabase RAG Profile Management")
    print("=" * 50)
    
    current = get_current_profile()
    print(f"Current profile: {current}")
    
    profiles = get_available_profiles()
    print(f"\nAvailable profiles ({len(profiles)}):")
    for name, desc in profiles.items():
        status = "ACTIVE" if name == current else "INACTIVE"
        print(f"  {status} {name}: {desc}") 