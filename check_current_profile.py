#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('src')

try:
    from src.ai.config.current_profile import get_current_profile
    from src.ai.config.rag_config import rag_config
    
    print("🔍 בדיקת פרופיל נוכחי")
    print("=" * 30)
    
    current_profile = get_current_profile()
    print(f"📊 פרופיל נוכחי: {current_profile}")
    
    # בדיקת הגדרות
    print(f"\n⚙️ הגדרות נוכחיות:")
    print(f"   - SIMILARITY_THRESHOLD: {rag_config.search.SIMILARITY_THRESHOLD}")
    print(f"   - HYBRID_SEARCH_FUNCTION: {rag_config.database.HYBRID_SEARCH_FUNCTION}")
    print(f"   - SEMANTIC_SEARCH_FUNCTION: {rag_config.database.SEMANTIC_SEARCH_FUNCTION}")
    print(f"   - MAX_CHUNKS_RETRIEVED: {rag_config.search.MAX_CHUNKS_RETRIEVED}")
    
except Exception as e:
    print(f"❌ שגיאה: {e}")
    import traceback
    traceback.print_exc() 