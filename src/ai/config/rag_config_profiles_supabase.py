#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supabase-Based RAG Config Profiles Management System
===================================================

This system manages RAG configuration profiles using only Supabase database,
replacing JSON file storage completely.
"""

import logging
from typing import Dict, Any, List, Optional
from .supabase_profile_manager import get_supabase_profile_manager

logger = logging.getLogger(__name__)

def load_dynamic_profiles() -> Dict[str, Any]:
    """Load all profiles from Supabase database"""
    try:
        manager = get_supabase_profile_manager()
        profiles = manager.get_all_profiles()
        logger.info(f"Loaded {len(profiles)} profiles from Supabase")
        return profiles
    except Exception as e:
        logger.error(f"Error loading profiles from Supabase: {e}")
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
                logger.warning(f"Failed to save profile: {profile_key}")
        
        logger.info(f"Saved {saved_count}/{len(profiles_data)} profiles to Supabase")
        
    except Exception as e:
        logger.error(f"Error saving profiles to Supabase: {e}")

def get_hidden_profiles() -> List[str]:
    """Get the list of hidden profiles from Supabase"""
    try:
        manager = get_supabase_profile_manager()
        hidden = manager.get_hidden_profiles()
        logger.info(f"Retrieved {len(hidden)} hidden profiles from Supabase")
        return hidden
    except Exception as e:
        logger.error(f"Error getting hidden profiles from Supabase: {e}")
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
                logger.warning(f"Failed to hide profile: {profile_key}")
        
        logger.info(f"Set {hidden_count}/{len(hidden_list)} profiles as hidden in Supabase")
        
    except Exception as e:
        logger.error(f"Error saving hidden profiles to Supabase: {e}")

def get_profile_config(profile_name: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific profile from Supabase"""
    try:
        manager = get_supabase_profile_manager()
        profile = manager.get_profile_by_key(profile_name)
        
        if profile:
            config = profile.get('config', {})
            logger.info(f"Retrieved config for profile '{profile_name}' from Supabase")
            return config
        else:
            logger.warning(f"Profile '{profile_name}' not found in Supabase")
            return None
            
    except Exception as e:
        logger.error(f"Error getting profile config '{profile_name}' from Supabase: {e}")
        return None

def update_profile_config(profile_name: str, config: Dict[str, Any]) -> bool:
    """Update configuration for a specific profile in Supabase"""
    try:
        manager = get_supabase_profile_manager()
        profile = manager.get_profile_by_key(profile_name)
        
        if profile:
            # Update the config part
            profile['config'] = config
            success = manager.save_profile(profile_name, profile)
            
            if success:
                logger.info(f"Updated config for profile '{profile_name}' in Supabase")
                return True
            else:
                logger.error(f"Failed to update config for profile '{profile_name}' in Supabase")
                return False
        else:
            logger.warning(f"Profile '{profile_name}' not found for config update")
            return False
            
    except Exception as e:
        logger.error(f"Error updating profile config '{profile_name}' in Supabase: {e}")
        return False

def create_new_profile(profile_key: str, name: str, description: str, config: Dict[str, Any], 
                      characteristics: Optional[Dict[str, Any]] = None) -> bool:
    """Create a new profile in Supabase"""
    try:
        manager = get_supabase_profile_manager()
        
        profile_data = {
            "name": name,
            "description": description,
            "config": config,
            "characteristics": characteristics or {},
            "isActive": False,
            "isCustom": True
        }
        
        success = manager.save_profile(profile_key, profile_data)
        
        if success:
            logger.info(f"Created new profile '{profile_key}' in Supabase")
            return True
        else:
            logger.error(f"Failed to create profile '{profile_key}' in Supabase")
            return False
            
    except Exception as e:
        logger.error(f"Error creating profile '{profile_key}' in Supabase: {e}")
        return False

def delete_profile(profile_key: str) -> bool:
    """Delete a profile from Supabase (soft delete)"""
    try:
        manager = get_supabase_profile_manager()
        success = manager.delete_profile(profile_key)
        
        if success:
            logger.info(f"Deleted profile '{profile_key}' from Supabase")
            return True
        else:
            logger.error(f"Failed to delete profile '{profile_key}' from Supabase")
            return False
            
    except Exception as e:
        logger.error(f"Error deleting profile '{profile_key}' from Supabase: {e}")
        return False

def save_new_profile(profile_key: str, profile_data: Dict[str, Any]) -> bool:
    """Save a new profile to Supabase (backward compatibility)"""
    try:
        manager = get_supabase_profile_manager()
        success = manager.save_profile(profile_key, profile_data)
        
        if success:
            logger.info(f"Saved new profile '{profile_key}' to Supabase")
            return True
        else:
            logger.error(f"Failed to save new profile '{profile_key}' to Supabase")
            return False
            
    except Exception as e:
        logger.error(f"Error saving new profile '{profile_key}' to Supabase: {e}")
        return False

def get_available_profile_names() -> List[str]:
    """Get list of available (non-hidden) profile names from Supabase"""
    try:
        manager = get_supabase_profile_manager()
        profiles = manager.list_available_profiles()
        profile_names = list(profiles.keys())
        logger.info(f"Retrieved {len(profile_names)} available profile names from Supabase")
        return profile_names
    except Exception as e:
        logger.error(f"Error getting available profile names from Supabase: {e}")
        return ["maximum_accuracy", "optimized_testing"]  # Fallback

def validate_profile_integrity() -> Dict[str, Any]:
    """Validate profile data integrity in Supabase"""
    try:
        manager = get_supabase_profile_manager()
        integrity_report = manager.validate_data_integrity()
        logger.info(f"Profile integrity validation completed")
        return integrity_report
    except Exception as e:
        logger.error(f"Error validating profile integrity: {e}")
        return {"error": str(e), "status": "failed"}

# === Functions required by current_profile.py ===

def get_profile_from_supabase(profile_name: str) -> Optional[Dict[str, Any]]:
    """Get a specific profile from Supabase (for compatibility with current_profile.py)"""
    try:
        manager = get_supabase_profile_manager()
        profile = manager.get_profile_by_key(profile_name)
        
        if profile:
            logger.info(f"Retrieved profile '{profile_name}' from Supabase")
            return profile
        else:
            logger.warning(f"Profile '{profile_name}' not found in Supabase")
            return None
            
    except Exception as e:
        logger.error(f"Error getting profile '{profile_name}' from Supabase: {e}")
        return None

def get_profiles_from_supabase() -> Dict[str, Any]:
    """Get all profiles from Supabase (for compatibility with current_profile.py)"""
    try:
        manager = get_supabase_profile_manager()
        profiles = manager.get_all_profiles()
        logger.info(f"Retrieved {len(profiles)} profiles from Supabase")
        return profiles
    except Exception as e:
        logger.error(f"Error getting profiles from Supabase: {e}")
        return {}

def get_default_profile_from_supabase() -> Optional[str]:
    """Get the default profile name from Supabase (for compatibility with current_profile.py)"""
    try:
        manager = get_supabase_profile_manager()
        default_profile = manager.get_current_profile()
        logger.info(f"Retrieved default profile '{default_profile}' from Supabase")
        return default_profile
    except Exception as e:
        logger.error(f"Error getting default profile from Supabase: {e}")
        return None

def save_profile_to_supabase(profile_key: str, profile_data: Dict[str, Any]) -> bool:
    """Save a profile to Supabase (for compatibility with current_profile.py)"""
    try:
        manager = get_supabase_profile_manager()
        success = manager.save_profile(profile_key, profile_data)
        
        if success:
            logger.info(f"Saved profile '{profile_key}' to Supabase")
            return True
        else:
            logger.error(f"Failed to save profile '{profile_key}' to Supabase")
            return False
            
    except Exception as e:
        logger.error(f"Error saving profile '{profile_key}' to Supabase: {e}")
        return False

def delete_profile_from_supabase(profile_key: str) -> bool:
    """Delete a profile from Supabase (for compatibility with current_profile.py)"""
    try:
        manager = get_supabase_profile_manager()
        success = manager.delete_profile(profile_key)
        
        if success:
            logger.info(f"Deleted profile '{profile_key}' from Supabase")
            return True
        else:
            logger.error(f"Failed to delete profile '{profile_key}' from Supabase")
            return False
            
    except Exception as e:
        logger.error(f"Error deleting profile '{profile_key}' from Supabase: {e}")
        return False

def save_default_profile(profile_name: str) -> bool:
    """Save the default profile name to Supabase (for compatibility with current_profile.py)"""
    try:
        manager = get_supabase_profile_manager()
        success = manager.set_current_profile(profile_name)
        
        if success:
            logger.info(f"Set default profile to '{profile_name}' in Supabase")
            return True
        else:
            logger.error(f"Failed to set default profile to '{profile_name}' in Supabase")
            return False
            
    except Exception as e:
        logger.error(f"Error setting default profile '{profile_name}' in Supabase: {e}")
        return False

def has_supabase_config() -> bool:
    """Check if Supabase configuration is available (for compatibility with current_profile.py)"""
    try:
        manager = get_supabase_profile_manager()
        # Try to perform a simple operation to check if Supabase is available
        manager.get_all_profiles()
        return True
    except Exception as e:
        logger.warning(f"Supabase configuration not available: {e}")
        return False

if __name__ == "__main__":
    print("Supabase RAG Config Profiles Management")
    print("=" * 60)
    
    # Test loading profiles
    profiles = load_dynamic_profiles()
    print(f"\nLoaded {len(profiles)} profiles:")
    for key, profile in profiles.items():
        status = "ACTIVE" if profile.get('isActive') else ""
        print(f"  {status} {key}: {profile['name']}")
    
    # Test hidden profiles
    hidden = get_hidden_profiles()
    print(f"\nHidden profiles ({len(hidden)}): {hidden}")
    
    # Test integrity
    integrity = validate_profile_integrity()
    print(f"\nIntegrity Report: {integrity}") 