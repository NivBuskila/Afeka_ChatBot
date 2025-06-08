#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('src')
sys.path.append('src/backend')
from src.ai.services.rag_service import RAGService

def debug_functions():
    try:
        rag = RAGService()
        print("🔍 בדיקת פונקציות במסד הנתונים")
        print("=" * 60)
        
        # בדיקת פונקציות קיימות
        functions_query = """
        SELECT 
            routine_name,
            routine_type,
            data_type,
            external_language,
            routine_definition
        FROM information_schema.routines 
        WHERE routine_schema = 'public' 
        AND routine_name LIKE '%search%'
        ORDER BY routine_name;
        """
        
        # לא יכול לעשות query ישיר, אז ננסה עם RPC
        print("📋 פונקציות חיפוש זמינות:")
        
        # בדיקת פונקציות ספציפיות
        test_funcs = [
            'match_documents',
            'hybrid_search',
            'hybrid_search_documents', 
            'advanced_semantic_search',
            'semantic_search'
        ]
        
        # יצירת embedding בסיסי לבדיקה
        import asyncio
        
        async def test_functions():
            query_embedding = await rag.generate_query_embedding('test')
            
            for func_name in test_funcs:
                try:
                    print(f"\n🔧 בדיקת {func_name}:")
                    
                    if func_name == 'match_documents':
                        result = rag.supabase.rpc(func_name, {
                            'query_embedding': query_embedding,
                            'match_threshold': 0.3,
                            'match_count': 1
                        }).execute()
                    elif func_name == 'hybrid_search':
                        result = rag.supabase.rpc(func_name, {
                            'query_text': 'test',
                            'query_embedding': query_embedding,
                            'similarity_threshold': 0.3,
                            'max_results': 1
                        }).execute()
                    elif func_name == 'hybrid_search_documents':
                        result = rag.supabase.rpc(func_name, {
                            'query_text': 'test',
                            'query_embedding': query_embedding,
                            'match_threshold': 0.3,
                            'match_count': 1,
                            'semantic_weight': 0.6,
                            'keyword_weight': 0.4
                        }).execute()
                    else:
                        # ננסה עם פרמטרים בסיסיים
                        result = rag.supabase.rpc(func_name, {
                            'query_embedding': query_embedding,
                            'similarity_threshold': 0.3,
                            'max_results': 1
                        }).execute()
                    
                    if result.data is not None:
                        print(f"   ✅ עובדת! החזירה {len(result.data)} תוצאות")
                        if result.data:
                            sample = result.data[0]
                            print(f"   📄 דוגמה: {list(sample.keys())[:5]}")
                    else:
                        print(f"   ⚠️ עובדת אבל החזירה None")
                        
                except Exception as e:
                    print(f"   ❌ לא עובדת: {str(e)[:100]}...")
        
        asyncio.run(test_functions())
        
        # בדיקת הconfiguration שמשתמש ב-RAG service
        print(f"\n⚙️ הגדרות RAG Service:")
        print(f"   - HYBRID_SEARCH_FUNCTION: {rag.db_config.HYBRID_SEARCH_FUNCTION}")
        print(f"   - SEMANTIC_SEARCH_FUNCTION: {rag.db_config.SEMANTIC_SEARCH_FUNCTION}")
        print(f"   - SIMILARITY_THRESHOLD: {rag.search_config.SIMILARITY_THRESHOLD}")
        
    except Exception as e:
        print(f'❌ שגיאה כללית: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_functions() 