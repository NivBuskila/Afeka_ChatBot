#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Current Profile Management System for RAG
=========================================

This system manages the currently active profile for the RAG system.
The profile is saved in a separate file and reloaded each time.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional

# Path to the current profile file
CONFIG_DIR = Path(__file__).parent
CURRENT_PROFILE_FILE = CONFIG_DIR / "current_profile.json"
DYNAMIC_PROFILES_FILE = CONFIG_DIR / "dynamic_profiles.json"

def get_current_profile() -> str:
    """Returns the current profile"""
    try:
        if CURRENT_PROFILE_FILE.exists():
            with open(CURRENT_PROFILE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("current_profile", "improved")
        else:
            # Create default file
            set_current_profile("improved")
            return "improved"
    except Exception as e:
        print(f"Error loading current profile: {e}")
        return "improved"

def set_current_profile(profile_name: str) -> None:
    """Sets the current profile"""
    try:
        data = {"current_profile": profile_name}
        with open(CURRENT_PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Set current profile to: {profile_name}")
    except Exception as e:
        print(f"Error setting current profile: {e}")

def get_available_profiles() -> Dict[str, str]:
    """Returns a list of all available profiles"""
    # Built-in static profiles
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
    
    # Load dynamic profiles from file
    dynamic_profiles = {}
    try:
        if DYNAMIC_PROFILES_FILE.exists():
            with open(DYNAMIC_PROFILES_FILE, 'r', encoding='utf-8') as f:
                dynamic_data = json.load(f)
                for profile_id, profile_data in dynamic_data.items():
                    description = profile_data.get('description', f'Custom profile: {profile_id}')
                    dynamic_profiles[profile_id] = description
    except Exception as e:
        print(f"Error loading dynamic profiles: {e}")
    
    # Merge profiles
    all_profiles = {**static_profiles, **dynamic_profiles}
    
    print(f"Available profiles: {list(all_profiles.keys())}")
    return all_profiles

def refresh_profiles():
    """Refreshes the list of available profiles"""
    # Re-import the profiles module to load changes
    try:
        import importlib
        import sys
        
        # Refresh the profiles module
        if 'src.ai.config.rag_config_profiles' in sys.modules:
            importlib.reload(sys.modules['src.ai.config.rag_config_profiles'])
        elif 'config.rag_config_profiles' in sys.modules:
            importlib.reload(sys.modules['config.rag_config_profiles'])
            
        print("✅ Refreshed profiles module")
    except Exception as e:
        print(f"Warning: Could not refresh profiles module: {e}")

if __name__ == "__main__":
    print("🔧 RAG Profile Management")
    print("=" * 50)
    
    current = get_current_profile()
    print(f"Current profile: {current}")
    
    profiles = get_available_profiles()
    print(f"\nAvailable profiles ({len(profiles)}):")
    for name, desc in profiles.items():
        status = "🟢 ACTIVE" if name == current else "⚪"
        print(f"  {status} {name}: {desc}")