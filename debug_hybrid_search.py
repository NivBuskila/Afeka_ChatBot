#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('src')
sys.path.append('src/backend')
import asyncio
from src.ai.services.rag_service import RAGService

async def debug_hybrid_search():
    try:
        rag = RAGService()
        print("🔍 בדיקת פונקציית hybrid_search")
        print("=" * 50)
        
        # ננסה לקרוא לפונקציה ישירות
        query_text = 'סטודנט'
        print(f"שאילתא: {query_text}")
        
        # יצירת embedding פשוט
        print("📍 יצירת embedding...")
        query_embedding = await rag.generate_query_embedding(query_text)
        print(f"   - Embedding length: {len(query_embedding)}")
        
        # ננסה לקרוא לפונקציה עם שמות שונים
        function_names_to_try = [
            'hybrid_search',
            'hybrid_search_documents',
            'match_documents_hybrid'
        ]
        
        for func_name in function_names_to_try:
            print(f"\n🔧 ניסוי פונקציה: {func_name}")
            try:
                # ננסה עם הפרמטרים הבסיסיים
                result = rag.supabase.rpc(func_name, {
                    'query_text': query_text,
                    'query_embedding': query_embedding,
                    'similarity_threshold': 0.3,  # סף נמוך
                    'max_results': 5
                }).execute()
                
                if result.data:
                    print(f"   ✅ הפונקציה עובדת! נמצאו {len(result.data)} תוצאות")
                    for i, res in enumerate(result.data[:2]):
                        print(f"   {i+1}. {res.get('document_name', 'N/A')}: {res.get('combined_score', 0):.3f}")
                else:
                    print(f"   ⚠️ הפונקציה עובדת אבל החזירה 0 תוצאות")
                    
            except Exception as e:
                print(f"   ❌ שגיאה בפונקציה {func_name}: {e}")
        
        # ננסה חיפוש סמנטי רגיל
        print(f"\n🔍 ניסוי חיפוש סמנטי רגיל...")
        try:
            result = rag.supabase.rpc('match_documents', {
                'query_embedding': query_embedding,
                'match_threshold': 0.3,
                'match_count': 5
            }).execute()
            
            if result.data:
                print(f"   ✅ חיפוש סמנטי: נמצאו {len(result.data)} תוצאות")
            else:
                print(f"   ⚠️ חיפוש סמנטי: 0 תוצאות")
                
        except Exception as e:
            print(f"   ❌ שגיאה בחיפוש סמנטי: {e}")
        
        # נבדוק את מבנה הtable
        print(f"\n📊 בדיקת מבנה הטבלה...")
        try:
            sample_chunks = rag.supabase.table('document_chunks').select('*').limit(2).execute()
            if sample_chunks.data:
                chunk = sample_chunks.data[0]
                print(f"   - ID: {chunk.get('id')}")
                print(f"   - Document ID: {chunk.get('document_id')}")
                print(f"   - Has embedding: {chunk.get('embedding') is not None}")
                print(f"   - Text preview: {chunk.get('chunk_text', '')[:100]}...")
            else:
                print("   ❌ לא נמצאו chunks בטבלה")
        except Exception as e:
            print(f"   ❌ שגיאה בקריאת טבלה: {e}")
        
    except Exception as e:
        print(f'❌ שגיאה כללית: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_hybrid_search()) 