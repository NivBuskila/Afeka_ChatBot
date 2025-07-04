#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Profile Management Script
========================

Script for managing RAG system profiles centrally.
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

backend_dir = project_root / "src" / "backend"
sys.path.insert(0, str(backend_dir))

def main():
    print("RAG Profile Management")
    print("=" * 50)
    
    try:
        from src.ai.config.current_profile import (
            get_current_profile_name, 
            set_current_profile
        )
        from src.ai.config.rag_config_profiles import list_profiles
        
        current_profile_name = get_current_profile_name()
        print(f"Current profile: {current_profile_name}")
        
        print("\nOptions:")
        print("1. View current configuration")
        print("2. Change profile")
        print("3. List all profiles")
        print("4. Test configuration")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            print(f"\nCurrent profile: {current_profile_name}")
            
        elif choice == "2":
            profiles = list_profiles()
            print("\nAvailable profiles:")
            for i, (name, desc) in enumerate(profiles.items(), 1):
                print(f"{i}. {name}: {desc}")
            
            try:
                selection = int(input(f"\nSelect profile (1-{len(profiles)}): "))
                profile_name = list(profiles.keys())[selection - 1]
                set_current_profile(profile_name)
                print(f"Profile changed to: {profile_name}")
                
            except (ValueError, IndexError):
                print("Invalid selection")
                
        elif choice == "3":
            profiles = list_profiles()
            print("\nAll available profiles:")
            for name, desc in profiles.items():
                print(f"• {name}: {desc}")
                
        elif choice == "4":
            print("\nTesting configuration...")
            try:
                from src.ai.services.rag_service import RAGService
                
                print("Creating RAGService with current profile...")
                rag = RAGService()
                print("RAGService created successfully!")
                
                print(f"Current profile: {rag.search_config.SIMILARITY_THRESHOLD}")
                
            except Exception as e:
                print(f"Error testing configuration: {e}")
                
        elif choice == "5":
            print("Goodbye!")
            
        else:
            print("Invalid option")
            
    except ImportError as e:
        print(f"Error importing profile system: {e}")
        print("Make sure you're running from the project root directory")

if __name__ == "__main__":
    main()