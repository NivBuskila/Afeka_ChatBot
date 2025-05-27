#!/usr/bin/env python3
"""
סקריפט בדיקה למערכת ניהול מסד הנתונים הוקטורי
"""

import os
import sys
import asyncio
import tempfile
import requests
import json
from pathlib import Path

# Add the backend path to sys.path
backend_path = Path(__file__).parent / "src" / "backend"
sys.path.insert(0, str(backend_path))

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_TOKEN = "dev-token"

def create_test_document():
    """יצירת מסמך בדיקה"""
    content = """
    זהו מסמך בדיקה למערכת RAG.
    
    המסמך מכיל מידע על בינה מלאכותית ועיבוד שפה טבעית.
    
    בינה מלאכותית (AI) היא תחום במדעי המחשב העוסק ביצירת מכונות חכמות.
    עיבוד שפה טבעית (NLP) הוא תת-תחום של AI העוסק בהבנת שפה אנושית.
    
    מערכות RAG (Retrieval-Augmented Generation) משלבות חיפוש מידע עם יצירת טקסט.
    הן מאפשרות למודלי שפה לגשת למידע עדכני ורלוונטי.
    
    מסדי נתונים וקטוריים מאחסנים embeddings של טקסטים.
    הם מאפשרים חיפוש סמנטי מהיר ויעיל.
    
    המערכת משתמשת במודל Gemini של Google ליצירת embeddings איכותיים.
    """
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        return f.name

def test_api_endpoint(endpoint, method='GET', data=None, files=None):
    """בדיקת endpoint של API"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            if files:
                response = requests.post(url, headers=headers, files=files)
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        print(f"✓ {method} {endpoint} - Status: {response.status_code}")
        
        if response.status_code < 400:
            try:
                result = response.json()
                print(f"  Response: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
                return result
            except:
                print(f"  Response: {response.text[:200]}...")
                return response.text
        else:
            print(f"  Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ {method} {endpoint} - Error: {str(e)}")
        return None

def main():
    """הרצת בדיקות המערכת"""
    print("🚀 מתחיל בדיקות מערכת ניהול מסד הנתונים הוקטורי")
    print("=" * 60)
    
    # Test 1: Check API health
    print("\n1. בדיקת בריאות API:")
    test_api_endpoint("/api/vector/stats")
    
    # Test 2: List documents
    print("\n2. רשימת מסמכים:")
    documents = test_api_endpoint("/api/vector/documents")
    
    # Test 3: Upload document
    print("\n3. העלאת מסמך בדיקה:")
    test_file_path = create_test_document()
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            upload_result = test_api_endpoint("/api/vector/upload-document", method='POST', files=files)
        
        if upload_result and 'document_id' in upload_result:
            document_id = upload_result['document_id']
            print(f"  📄 מסמך הועלה בהצלחה! ID: {document_id}")
            
            # Test 4: Check document status
            print("\n4. בדיקת סטטוס מסמך:")
            import time
            for i in range(5):  # Wait up to 25 seconds for processing
                status_result = test_api_endpoint(f"/api/vector/document/{document_id}/status")
                if status_result and status_result.get('processing_status') == 'completed':
                    print("  ✅ עיבוד המסמך הושלם!")
                    break
                elif status_result and status_result.get('processing_status') == 'failed':
                    print("  ❌ עיבוד המסמך נכשל!")
                    break
                else:
                    print(f"  ⏳ מעבד... (ניסיון {i+1}/5)")
                    time.sleep(5)
            
            # Test 5: Semantic search
            print("\n5. חיפוש סמנטי:")
            search_queries = [
                "מה זה בינה מלאכותית?",
                "איך עובדות מערכות RAG?",
                "מסדי נתונים וקטוריים"
            ]
            
            for query in search_queries:
                print(f"\n  🔍 חיפוש: '{query}'")
                search_result = test_api_endpoint("/api/vector/search", method='POST', data={
                    "query": query,
                    "limit": 3,
                    "threshold": 0.7
                })
                
                if search_result and search_result.get('results'):
                    print(f"    נמצאו {len(search_result['results'])} תוצאות")
                    for i, result in enumerate(search_result['results'][:2]):
                        similarity = result.get('similarity', 0) * 100
                        content_preview = result.get('content', '')[:100]
                        print(f"    {i+1}. דמיון: {similarity:.1f}% - {content_preview}...")
                else:
                    print("    לא נמצאו תוצאות")
            
            # Test 6: Hybrid search
            print("\n6. חיפוש היברידי:")
            hybrid_result = test_api_endpoint("/api/vector/search/hybrid", method='POST', data={
                "query": "AI ו NLP",
                "limit": 3,
                "threshold": 0.7
            })
            
            if hybrid_result and hybrid_result.get('results'):
                print(f"  נמצאו {len(hybrid_result['results'])} תוצאות בחיפוש היברידי")
            
            # Test 7: Get updated stats
            print("\n7. סטטיסטיקות מעודכנות:")
            final_stats = test_api_endpoint("/api/vector/stats")
            
            # Test 8: Delete document (optional)
            print(f"\n8. מחיקת מסמך בדיקה (ID: {document_id}):")
            delete_confirm = input("האם למחוק את מסמך הבדיקה? (y/N): ").lower()
            if delete_confirm == 'y':
                delete_result = test_api_endpoint(f"/api/vector/document/{document_id}", method='DELETE')
                if delete_result:
                    print("  🗑️ מסמך נמחק בהצלחה!")
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(test_file_path)
        except:
            pass
    
    print("\n" + "=" * 60)
    print("✅ בדיקות הושלמו!")
    print("\n📋 סיכום:")
    print("- אם כל הבדיקות עברו בהצלחה, המערכת מוכנה לשימוש")
    print("- ניתן לגשת לדשבורד בכתובת: http://localhost:3000")
    print("- להשתמש ב-token 'dev-token' לאימות")

if __name__ == "__main__":
    main() 