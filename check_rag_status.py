#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('src')
sys.path.append('src/backend')
import asyncio
from src.ai.services.rag_service import RAGService

async def check_rag_status():
    try:
        rag = RAGService()
        print("🔍 בדיקת סטטוס מערכת RAG")
        print("=" * 50)
        
        # נבדוק כמה מסמכים יש במערכת
        result = rag.supabase.table('documents').select('*', count='exact').execute()
        print(f'📊 סה''כ מסמכים: {result.count}')
        
        if result.data:
            print('\n📋 סטטוס מסמכים:')
            status_count = {}
            for doc in result.data:
                status = doc["processing_status"]
                status_count[status] = status_count.get(status, 0) + 1
                if len([d for d in result.data[:5] if d == doc]) <= 5:  # הראה 5 ראשונים
                    print(f'  - {doc["name"]}: {status}')
            
            print(f'\n📈 סיכום סטטוסים: {status_count}')
        
        # נבדוק כמה chunks יש
        chunks_result = rag.supabase.table('document_chunks').select('*', count='exact').execute()
        print(f'\n🧩 סה''כ chunks: {chunks_result.count}')
        
        # נבדוק אם יש embeddings
        if chunks_result.data:
            sample_chunk = chunks_result.data[0]
            has_embedding = sample_chunk.get('embedding') is not None
            print(f'📍 דוגמה לchunk עם embedding: {has_embedding}')
            if has_embedding:
                print(f'   - Embedding length: {len(sample_chunk["embedding"]) if sample_chunk["embedding"] else 0}')
            
        # נבדוק את פונקציית החיפוש
        print(f'\n🔧 בדיקת פונקציית hybrid_search במסד הנתונים...')
        try:
            # נבדוק אם הפונקציה קיימת
            test_result = rag.supabase.rpc('hybrid_search', {
                'query_text': 'טסט',
                'query_embedding': [0.0] * 768,
                'similarity_threshold': 0.5,
                'max_results': 1
            }).execute()
            print(f'✅ פונקציית hybrid_search פועלת')
        except Exception as func_e:
            print(f'❌ בעיה בפונקציית hybrid_search: {func_e}')
            
        # ננסה חיפוש פשוט
        print(f'\n🔍 ניסוי חיפוש פשוט...')
        search_results = await rag.hybrid_search('סטודנט')
        print(f'תוצאות חיפוש: {len(search_results)} נמצאו')
        
        if search_results:
            print('📄 דוגמה לתוצאה:')
            result = search_results[0]
            print(f'  - מסמך: {result.get("document_name", "N/A")}')
            print(f'  - ציון דמיון: {result.get("similarity", "N/A")}')
            print(f'  - טקסט: {result.get("chunk_text", "")[:100]}...')
        
    except Exception as e:
        print(f'❌ שגיאה כללית: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_rag_status()) 