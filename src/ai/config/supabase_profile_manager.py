#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supabase-Only Profile Management System for RAG
===============================================

This system manages RAG profiles using only Supabase database, 
replacing the JSON-based storage completely.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class SupabaseProfileManager:
    """Manages RAG profiles exclusively through Supabase database"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        )
        if not self.supabase:
            raise ValueError("Failed to initialize Supabase client")
        logger.info("🔗 SupabaseProfileManager initialized successfully")
    
    def get_current_profile(self) -> str:
        """Get the currently active profile"""
        try:
            response = self.supabase.table('rag_profiles').select('profile_key').eq('is_active', True).is_('deleted_at', 'null').single().execute()
            
            if response.data:
                profile_key = response.data['profile_key']
                logger.info(f"🎯 Current active profile: {profile_key}")
                return profile_key
            else:
                # No active profile found, set default
                logger.warning("⚠️ No active profile found, setting default to 'maximum_accuracy'")
                self.set_current_profile('maximum_accuracy')
                return 'maximum_accuracy'
                
        except Exception as e:
            logger.error(f"❌ Error getting current profile: {e}")
            return 'maximum_accuracy'  # Safe fallback
    
    def set_current_profile(self, profile_key: str) -> bool:
        """Set the currently active profile"""
        try:
            # First, deactivate all profiles
            self.supabase.table('rag_profiles').update({'is_active': False}).is_('deleted_at', 'null').execute()
            
            # Then activate the requested profile
            response = self.supabase.table('rag_profiles').update({
                'is_active': True
            }).eq('profile_key', profile_key).is_('deleted_at', 'null').execute()
            
            if response.data:
                logger.info(f"✅ Successfully set current profile to: {profile_key}")
                return True
            else:
                logger.error(f"❌ Profile '{profile_key}' not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error setting current profile to '{profile_key}': {e}")
            return False
    
    def get_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all non-deleted profiles"""
        try:
            response = self.supabase.table('rag_profiles').select('*').is_('deleted_at', 'null').order('created_at').execute()
            
            profiles = {}
            for profile in response.data:
                profiles[profile['profile_key']] = {
                    'id': profile['profile_key'],
                    'name': profile['name'],
                    'description': profile['description'],
                    'isActive': profile['is_active'],
                    'isCustom': profile['is_custom'],
                    'config': profile['config'],
                    'characteristics': profile['characteristics'] or {}
                }
            
            logger.info(f"📋 Retrieved {len(profiles)} profiles from Supabase")
            return profiles
            
        except Exception as e:
            logger.error(f"❌ Error getting all profiles: {e}")
            return {}
    
    def get_profile_by_key(self, profile_key: str) -> Optional[Dict[str, Any]]:
        """Get a specific profile by its key"""
        try:
            response = self.supabase.table('rag_profiles').select('*').eq('profile_key', profile_key).is_('deleted_at', 'null').single().execute()
            
            if response.data:
                profile = response.data
                return {
                    'id': profile['profile_key'],
                    'name': profile['name'],
                    'description': profile['description'],
                    'isActive': profile['is_active'],
                    'isCustom': profile['is_custom'],
                    'config': profile['config'],
                    'characteristics': profile['characteristics'] or {}
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting profile '{profile_key}': {e}")
            return None
    
    def save_profile(self, profile_key: str, profile_data: Dict[str, Any]) -> bool:
        """Save or update a profile"""
        try:
            # Check if profile exists
            existing = self.supabase.table('rag_profiles').select('id').eq('profile_key', profile_key).is_('deleted_at', 'null').execute()
            
            profile_record = {
                'profile_key': profile_key,
                'name': profile_data.get('name', profile_key),
                'description': profile_data.get('description', ''),
                'is_active': profile_data.get('isActive', False),
                'is_custom': profile_data.get('isCustom', True),
                'is_hidden': False,  # Default to visible
                'config': profile_data.get('config', {}),
                'characteristics': profile_data.get('characteristics', {})
            }
            
            if existing.data:
                # Update existing profile
                profile_record['updated_at'] = 'now()'
                response = self.supabase.table('rag_profiles').update(profile_record).eq('profile_key', profile_key).is_('deleted_at', 'null').execute()
                logger.info(f"🔄 Updated existing profile: {profile_key}")
            else:
                # Create new profile
                response = self.supabase.table('rag_profiles').insert(profile_record).execute()
                logger.info(f"➕ Created new profile: {profile_key}")
            
            return response.data is not None
            
        except Exception as e:
            logger.error(f"❌ Error saving profile '{profile_key}': {e}")
            return False
    
    def delete_profile(self, profile_key: str) -> bool:
        """Soft delete a profile"""
        try:
            response = self.supabase.table('rag_profiles').update({
                'deleted_at': 'now()',
                'is_active': False
            }).eq('profile_key', profile_key).is_('deleted_at', 'null').execute()
            
            if response.data:
                logger.info(f"🗑️ Soft deleted profile: {profile_key}")
                return True
            else:
                logger.error(f"❌ Profile '{profile_key}' not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting profile '{profile_key}': {e}")
            return False
    
    def get_hidden_profiles(self) -> List[str]:
        """Get list of hidden profile keys"""
        try:
            response = self.supabase.table('rag_profiles').select('profile_key').eq('is_hidden', True).is_('deleted_at', 'null').execute()
            
            hidden_profiles = [profile['profile_key'] for profile in response.data]
            logger.info(f"🔒 Retrieved {len(hidden_profiles)} hidden profiles")
            return hidden_profiles
            
        except Exception as e:
            logger.error(f"❌ Error getting hidden profiles: {e}")
            return []
    
    def set_profile_hidden(self, profile_key: str, is_hidden: bool) -> bool:
        """Set profile visibility"""
        try:
            response = self.supabase.table('rag_profiles').update({
                'is_hidden': is_hidden
            }).eq('profile_key', profile_key).is_('deleted_at', 'null').execute()
            
            if response.data:
                visibility = "hidden" if is_hidden else "visible"
                logger.info(f"👁️ Set profile '{profile_key}' to {visibility}")
                return True
            else:
                logger.error(f"❌ Profile '{profile_key}' not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error setting profile visibility for '{profile_key}': {e}")
            return False
    
    def list_available_profiles(self) -> Dict[str, str]:
        """Get all non-hidden, non-deleted profiles for display"""
        try:
            response = self.supabase.table('rag_profiles').select('profile_key, name, description').eq('is_hidden', False).is_('deleted_at', 'null').order('created_at').execute()
            
            profiles = {}
            for profile in response.data:
                profiles[profile['profile_key']] = profile['description'] or profile['name']
            
            logger.info(f"📋 Listed {len(profiles)} available profiles")
            return profiles
            
        except Exception as e:
            logger.error(f"❌ Error listing available profiles: {e}")
            return {}
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity and return report"""
        try:
            # Count profiles by status
            all_profiles = self.supabase.table('rag_profiles').select('*').execute()
            
            total = len(all_profiles.data)
            active = len([p for p in all_profiles.data if p['is_active'] and not p['deleted_at']])
            deleted = len([p for p in all_profiles.data if p['deleted_at']])
            hidden = len([p for p in all_profiles.data if p['is_hidden'] and not p['deleted_at']])
            
            report = {
                'total_profiles': total,
                'active_profiles': active,
                'deleted_profiles': deleted,
                'hidden_profiles': hidden,
                'available_profiles': total - deleted - hidden,
                'data_integrity': 'GOOD' if active <= 1 else 'WARNING - Multiple active profiles'
            }
            
            logger.info(f"🔍 Data integrity report: {report}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error validating data integrity: {e}")
            return {'error': str(e)}

# Create global instance
_supabase_manager = None

def get_supabase_profile_manager() -> SupabaseProfileManager:
    """Get singleton instance of SupabaseProfileManager"""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseProfileManager()
    return _supabase_manager

# Backward compatibility functions
def get_current_profile() -> str:
    """Get current profile - Supabase version"""
    return get_supabase_profile_manager().get_current_profile()

def set_current_profile(profile_key: str) -> bool:
    """Set current profile - Supabase version"""
    return get_supabase_profile_manager().set_current_profile(profile_key)

def get_available_profiles() -> Dict[str, str]:
    """Get available profiles - Supabase version"""
    return get_supabase_profile_manager().list_available_profiles()

def load_dynamic_profiles() -> Dict[str, Dict[str, Any]]:
    """Load dynamic profiles - Supabase version"""
    return get_supabase_profile_manager().get_all_profiles()

def save_new_profile(profile_key: str, profile_data: Dict[str, Any]) -> bool:
    """Save new profile - Supabase version"""
    return get_supabase_profile_manager().save_profile(profile_key, profile_data)

def delete_profile(profile_key: str) -> bool:
    """Delete profile - Supabase version"""
    return get_supabase_profile_manager().delete_profile(profile_key)

def get_hidden_profiles() -> List[str]:
    """Get hidden profiles - Supabase version"""
    return get_supabase_profile_manager().get_hidden_profiles()

if __name__ == "__main__":
    # Test the new system
    manager = get_supabase_profile_manager()
    
    print("🧪 Testing Supabase Profile Manager")
    print("=" * 50)
    
    # Test data integrity
    integrity = manager.validate_data_integrity()
    print(f"Data Integrity: {integrity}")
    
    # Test current profile
    current = manager.get_current_profile()
    print(f"Current Profile: {current}")
    
    # Test listing profiles
    profiles = manager.list_available_profiles()
    print(f"Available Profiles: {list(profiles.keys())}") 