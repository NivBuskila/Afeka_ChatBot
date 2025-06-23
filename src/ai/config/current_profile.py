#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Current profile manager for RAG configuration
Central manager for profile selection and configuration loading
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union

from .rag_config_profiles import get_profile, list_profiles, DEFAULT_PROFILE, SupabaseCompatibleConfig
from .rag_config_profiles_supabase import (
    get_profile_from_supabase,
    get_profiles_from_supabase,
    get_default_profile_from_supabase,
    save_profile_to_supabase,
    delete_profile_from_supabase,
    save_default_profile,
    has_supabase_config
)

logger = logging.getLogger(__name__)

# Global variable to store the current profile
_current_profile_name: str = DEFAULT_PROFILE
_current_profile_config: Optional[SupabaseCompatibleConfig] = None

def get_current_profile_name() -> str:
    """Return the current profile name"""
    global _current_profile_name
    logger.info(f"get_current_profile_name() called, returning: '{_current_profile_name}'")
    return _current_profile_name

def get_current_profile() -> SupabaseCompatibleConfig:
    """Return the current profile configuration"""
    global _current_profile_config
    
    if _current_profile_config is None:
        # Load default profile if not already loaded
        set_current_profile(DEFAULT_PROFILE)
    
    return _current_profile_config

def set_current_profile(profile_name: str, save_as_default: bool = False) -> bool:
    """
    Change the current profile
    
    Args:
        profile_name: Profile name to switch to
        save_as_default: Whether to save as default profile
        
    Returns:
        bool: Success status
    """
    global _current_profile_name, _current_profile_config
    
    try:
        # Try to load from Supabase first
        if has_supabase_config():
            try:
                profile_config = get_profile_from_supabase(profile_name)
                if profile_config:
                    _current_profile_name = profile_name
                    _current_profile_config = profile_config
                    logger.info(f"Loaded profile '{profile_name}' from Supabase")
                    
                    # Save as default if requested
                    if save_as_default:
                        save_default_profile(profile_name)
                        logger.info(f"Set '{profile_name}' as default profile")
                    
                    return True
            except Exception as e:
                logger.warning(f"Failed to load from Supabase: {e}")
        
        # Fallback to local profiles
        profile_config = get_profile(profile_name)
        _current_profile_name = profile_name
        _current_profile_config = profile_config
        logger.info(f"Switched to profile: {profile_name}")
        
        # Save to file for persistence
        _save_current_profile_to_file(profile_name)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to set profile '{profile_name}': {e}")
        return False

def reload_current_profile() -> bool:
    """
    Reload the current profile from source
    Useful when configuration has been updated
    
    Returns:
        bool: Success status
    """
    return set_current_profile(_current_profile_name)

def _save_current_profile_to_file(profile_name: str) -> None:
    """Save the current profile name to a file for persistence"""
    try:
        config_dir = Path(__file__).parent
        profile_file = config_dir / ".current_profile"
        profile_file.write_text(profile_name)
    except Exception as e:
        logger.warning(f"Failed to save profile to file: {e}")

def _load_profile_from_file() -> Optional[str]:
    """Load the saved profile name from file"""
    try:
        config_dir = Path(__file__).parent
        profile_file = config_dir / ".current_profile"
        if profile_file.exists():
            return profile_file.read_text().strip()
    except Exception as e:
        logger.warning(f"Failed to load profile from file: {e}")
    return None

# Initialize on module load
def _initialize_profile():
    """Initialize profile on module load"""
    global _current_profile_name, _current_profile_config
    
    logger.info("_initialize_profile() called - initializing RAG profile")
    
    # First, try to get default from Supabase
    if has_supabase_config():
        try:
            default_profile = get_default_profile_from_supabase()
            if default_profile:
                logger.info(f"Loading default profile from Supabase: {default_profile}")
                if set_current_profile(default_profile):
                    logger.info(f"Successfully loaded profile from Supabase: {default_profile}")
                    return
        except Exception as e:
            logger.warning(f"Failed to load default from Supabase: {e}")
    else:
        logger.info("Supabase config not available, skipping Supabase profile loading")
    
    # Then try environment variable
    env_profile = os.environ.get('RAG_PROFILE')
    if env_profile:
        # Validate that profile exists
        available_profiles = list_profiles()
        supabase_profiles = []
        if has_supabase_config():
            try:
                supabase_profiles = list(get_profiles_from_supabase().keys())
            except:
                pass
        
        if env_profile in available_profiles or env_profile in supabase_profiles:
            logger.info(f"Loading profile from environment: {env_profile}")
            if set_current_profile(env_profile):
                logger.info(f"Successfully loaded profile from environment: {env_profile}")
                return
        else:
            logger.warning(f"Profile '{env_profile}' from environment not found")
    else:
        logger.info(f"No RAG_PROFILE environment variable set")
    
    # Try to load from file
    saved_profile = _load_profile_from_file()
    if saved_profile:
        available_profiles = list_profiles()
        supabase_profiles = []
        if has_supabase_config():
            try:
                supabase_profiles = list(get_profiles_from_supabase().keys())
            except:
                pass
        
        if saved_profile in available_profiles or saved_profile in supabase_profiles:
            logger.info(f"Loading saved profile from file: {saved_profile}")
            if set_current_profile(saved_profile):
                logger.info(f"Successfully loaded profile from file: {saved_profile}")
                return
        else:
            logger.warning(f"Saved profile '{saved_profile}' not found in available profiles")
    else:
        logger.info("No saved profile file found")
    
    # Default to 'balanced' profile
    logger.info(f"Using default profile: {DEFAULT_PROFILE}")
    if set_current_profile(DEFAULT_PROFILE):
        logger.info(f"Successfully set default profile: {DEFAULT_PROFILE}")
    else:
        logger.error(f"Failed to set default profile: {DEFAULT_PROFILE}")
        # Fallback to hardcoded values
        _current_profile_name = DEFAULT_PROFILE
        _current_profile_config = None
        logger.warning(f"Using hardcoded fallback profile: {_current_profile_name}")

# Initialize profile when module loads
logger.info("Module loading - about to call _initialize_profile()")
_initialize_profile()
logger.info(f"Module loaded - current profile set to: '{_current_profile_name}'")

# Export convenience functions
def get_search_config():
    """Get search configuration from current profile"""
    return get_current_profile().search

def get_context_config():
    """Get context configuration from current profile"""
    return get_current_profile().context

def get_llm_config():
    """Get LLM configuration from current profile"""
    return get_current_profile().llm

def get_performance_config():
    """Get performance configuration from current profile"""
    return get_current_profile().performance

def get_database_config():
    """Get database configuration from current profile"""
    return get_current_profile().database

def get_embedding_config():
    """Get embedding configuration from current profile"""
    return get_current_profile().embedding

# Export all important items
__all__ = [
    'get_current_profile_name',
    'get_current_profile',
    'set_current_profile',
    'reload_current_profile',
    'get_search_config',
    'get_context_config',
    'get_llm_config',
    'get_performance_config',
    'get_database_config',
    'get_embedding_config'
]

if __name__ == "__main__":
    print("Supabase RAG Profile Management")
    print("=" * 50)
    
    current = get_current_profile_name()
    print(f"Current profile: {current}")
    
    # Import the function from the right place
    from .current_profile_supabase import get_available_profiles
    profiles = get_available_profiles()
    print(f"\nAvailable profiles ({len(profiles)}):")
    for name, desc in profiles.items():
        status = "ACTIVE" if name == current else ""
        print(f"  {status} {name}: {desc}")