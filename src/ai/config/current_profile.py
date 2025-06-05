#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Central Profile Management
=========================

This file manages the current active profile for the entire RAG system.
All components (UI, tests, services) will use the same profile.
"""

import os
from typing import Optional

# הפרופיל הנוכחי - זה המקום היחיד שמגדיר את הפרופיל!
CURRENT_PROFILE = "enhanced_testing"

# אפשרות לגובר את הפרופיל דרך משתנה סביבה
ENVIRONMENT_PROFILE = os.getenv("RAG_PROFILE")

def get_current_profile() -> str:
    """
    מחזיר את הפרופיל הנוכחי.
    בסדר עדיפות:
    1. משתנה סביבה RAG_PROFILE
    2. הגדרה קבועה CURRENT_PROFILE
    """
    return ENVIRONMENT_PROFILE or CURRENT_PROFILE

def set_current_profile(profile_name: str) -> None:
    """
    מגדיר פרופיל חדש לכל המערכת.
    השינוי יחול על כל הרכיבים החדשים שיאותחלו.
    """
    global CURRENT_PROFILE
    CURRENT_PROFILE = profile_name
    print(f"🔧 פרופיל RAG עודכן ל: {profile_name}")

def get_available_profiles() -> dict:
    """מחזיר רשימת פרופילים זמינים"""
    try:
        from .rag_config_profiles import list_profiles
        return list_profiles()
    except ImportError:
        return {
            "improved": "Optimized for missing sections",
            "balanced": "Balanced performance and quality", 
            "high_quality": "Maximum quality",
            "fast": "Maximum speed",
            "debug": "Debug and development"
        }

def print_current_config():
    """מדפיס את הקונפיגורציה הנוכחית"""
    current = get_current_profile()
    profiles = get_available_profiles()
    
    print("=" * 50)
    print("🎯 RAG System Configuration")
    print("=" * 50)
    print(f"✅ Current Profile: {current}")
    print(f"📋 Description: {profiles.get(current, 'Unknown profile')}")
    print()
    print("📋 Available Profiles:")
    for name, desc in profiles.items():
        marker = "👉" if name == current else "  "
        print(f"{marker} {name}: {desc}")
    print("=" * 50)

if __name__ == "__main__":
    print_current_config() 