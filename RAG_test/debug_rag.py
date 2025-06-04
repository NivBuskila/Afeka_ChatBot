#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import asyncio
import logging

# הוספת הנתיב של הפרויקט
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, 'src', 'backend'))

from services.rag_service import RAGService

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_profile(profile_name: str, query: str):
    """בדיקת פרופיל ספציפי"""
    print(f"\n🔧 בדיקת פרופיל: {profile_name.upper()}")
    print("=" * 60)
    
    try:
        # יצירת RAG service עם פרופיל
        rag = RAGService(config_profile=profile_name)
        
        # הצגת הגדרות הפרופיל
        print(f"📊 הגדרות הפרופיל:")
        print(f"   - similarity_threshold: {rag.search_config.SIMILARITY_THRESHOLD}")
        print(f"   - max_chunks: {rag.search_config.MAX_CHUNKS_RETRIEVED}")
        print(f"   - max_context_tokens: {rag.context_config.MAX_CONTEXT_TOKENS}")
        print(f"   - temperature: {rag.llm_config.TEMPERATURE}")
        print(f"   - semantic_weight: {rag.search_config.HYBRID_SEMANTIC_WEIGHT}")
        
        # בדיקת תשובה
        answer = await rag.generate_answer(query, search_method='hybrid')
        
        print(f"\n💬 תוצאות:")
        print(f"   - צ'אנקים שנמצאו: {len(answer.get('chunks_selected', []))}")
        print(f"   - מספר מקורות: {len(answer.get('sources', []))}")
        print(f"   - זמן תגובה: {answer.get('response_time_ms')}ms")
        
        if answer.get('chunks_selected'):
            print(f"   - ציון ממוצע: {sum(chunk.get('similarity_score', 0) for chunk in answer['chunks_selected'][:5]) / min(5, len(answer['chunks_selected'])):.3f}")
            
        if answer.get('answer'):
            print(f"   - תשובה: {answer['answer'][:150]}...")
            return True
        else:
            print("   ⚠️ לא נוצרה תשובה")
            return False
            
    except Exception as e:
        print(f"   ❌ שגיאה: {e}")
        return False

async def compare_profiles():
    """השוואה בין פרופילים שונים"""
    
    profiles_to_test = ["balanced", "fast", "high_quality", "debug"]
    test_query = "מה אומר סעיף 1.5.1?"
    
    print("🔍 השוואת פרופילים")
    print("=" * 80)
    print(f"שאילתה לבדיקה: '{test_query}'")
    
    results = {}
    
    for profile in profiles_to_test:
        try:
            success = await test_profile(profile, test_query)
            results[profile] = "✅ הצליח" if success else "❌ נכשל"
        except Exception as e:
            results[profile] = f"❌ שגיאה: {str(e)[:50]}"
    
    print("\n📊 סיכום תוצאות:")
    print("=" * 40)
    for profile, result in results.items():
        print(f"   {profile.ljust(15)}: {result}")

async def debug_rag():
    """בדיקה של מערכת RAG"""
    
    try:
        # יצירת RAG service
        rag = RAGService()
        
        # שאלה פשוטה לבדיקה
        test_query = "מה אומר סעיף 1.5.1?"
        
        print(f"🔍 בודק שאילתה: '{test_query}'")
        
        # הצגת הגדרות נוכחיות
        print(f"📊 הגדרות נוכחיות:")
        print(f"   - similarity_threshold: {rag.search_config.SIMILARITY_THRESHOLD}")
        print(f"   - max_chunks: {rag.search_config.MAX_CHUNKS_RETRIEVED}")
        print(f"   - max_context_tokens: {rag.context_config.MAX_CONTEXT_TOKENS}")
        print(f"   - model: {rag.llm_config.MODEL_NAME}")
        print(f"   - temperature: {rag.llm_config.TEMPERATURE}")
        
        # שמירת הגדרות מקוריות לשחזור
        original_threshold = rag.search_config.SIMILARITY_THRESHOLD
        original_max_chunks = rag.search_config.MAX_CHUNKS_RETRIEVED
        
        # שינוי זמני להגדרות נמוכות יותר לבדיקה
        rag.search_config.SIMILARITY_THRESHOLD = 0.3  # הנמכה משמעותית
        rag.search_config.MAX_CHUNKS_RETRIEVED = 15  # הגדלה
        
        print(f"\n🔧 הגדרות זמניות לבדיקה:")
        print(f"   - similarity_threshold: {rag.search_config.SIMILARITY_THRESHOLD}")
        print(f"   - max_chunks: {rag.search_config.MAX_CHUNKS_RETRIEVED}")
        
        # בדיקה 1: חיפוש סמנטי בלבד
        print("\n🧠 בדיקת חיפוש סמנטי:")
        semantic_results = await rag.semantic_search(test_query)
        print(f"   נמצאו {len(semantic_results)} תוצאות")
        
        if semantic_results:
            for i, result in enumerate(semantic_results[:3]):
                score = result.get('similarity_score', 0)
                preview = result.get('chunk_text', '')[:100]
                print(f"   {i+1}. ציון: {score:.3f} | {preview}...")
        else:
            print("   ⚠️ לא נמצאו תוצאות")
        
        # בדיקה 2: חיפוש היברידי
        print("\n🔄 בדיקת חיפוש היברידי:")
        hybrid_results = await rag.hybrid_search(test_query)
        print(f"   נמצאו {len(hybrid_results)} תוצאות")
        
        if hybrid_results:
            for i, result in enumerate(hybrid_results[:3]):
                sim_score = result.get('similarity_score', 0)
                kw_score = result.get('keyword_score', 0) 
                combined = result.get('combined_score', 0)
                preview = result.get('chunk_text', '')[:100]
                print(f"   {i+1}. סמנטי: {sim_score:.3f} | מילות מפתח: {kw_score:.3f} | משולב: {combined:.3f}")
                print(f"      {preview}...")
        else:
            print("   ⚠️ לא נמצאו תוצאות")
        
        # בדיקה 3: יצירת תשובה מלאה
        print("\n💬 יצירת תשובה מלאה:")
        answer = await rag.generate_answer(test_query, search_method='hybrid')
        
        print(f"   צ'אנקים שנמצאו: {len(answer.get('chunks_selected', []))}")
        print(f"   מספר מקורות: {len(answer.get('sources', []))}")
        print(f"   זמן תגובה: {answer.get('response_time_ms')}ms")
        print(f"   שיטת חיפוש: {answer.get('search_method')}")
        
        # הצגת פרטי config שנוצרו
        if 'config_used' in answer:
            config = answer['config_used']
            print(f"   Config ששימש: threshold={config.get('similarity_threshold')}, "
                  f"max_chunks={config.get('max_chunks')}, "
                  f"model={config.get('model')}")
        
        if answer.get('answer'):
            print(f"   תשובה: {answer['answer'][:200]}...")
        else:
            print("   ⚠️ לא נוצרה תשובה")
        
        # בדיקה 4: הצגת הגדרות כמילון
        print("\n⚙️ כל ההגדרות:")
        all_config = rag.get_current_config()
        for section, settings in all_config.items():
            print(f"   📋 {section.upper()}:")
            for key, value in list(settings.items())[:3]:  # רק 3 ראשונים מכל חלק
                print(f"      {key}: {value}")
            if len(settings) > 3:
                print(f"      ... ועוד {len(settings) - 3} הגדרות")
        
        # החזרת הגדרות מקוריות
        rag.search_config.SIMILARITY_THRESHOLD = original_threshold
        rag.search_config.MAX_CHUNKS_RETRIEVED = original_max_chunks
        
        print("\n✅ בדיקה הושלמה בהצלחה!")
        print(f"🔄 הגדרות הוחזרו: threshold={original_threshold}, max_chunks={original_max_chunks}")
        
    except Exception as e:
        logger.error(f"שגיאה בבדיקה: {e}")
        print(f"❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # בדיקה עם פרופילים
    print("🎯 בדיקת פרופילי הגדרות")
    asyncio.run(compare_profiles())
    
    print("\n" + "="*80 + "\n")
    
    # בדיקה רגילה
    print("🔧 בדיקה רגילה")
    asyncio.run(debug_rag()) 