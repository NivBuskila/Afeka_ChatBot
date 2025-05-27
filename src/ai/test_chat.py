import requests
import json
import time
import sys

# הגדרת ה-URL של השירות
BASE_URL = "http://localhost:5000"

def test_chat_api(message="What is section 8.7 about?", use_rag=True):
    """בדיקת ה-API של הצ'אט"""
    print(f"Sending query: '{message}'")
    print(f"Use RAG: {use_rag}")
    
    try:
        # שליחת בקשה ל-API
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": message,
                "use_rag": use_rag,
                "add_sources": True
            },
            timeout=10  # זמן קצר יותר
        )
        request_time = time.time() - start_time
        
        # בדיקת התשובה
        if response.status_code == 200:
            data = response.json()
            
            print("\n===== API Response =====")
            print(f"Status: {response.status_code}")
            print(f"Time: {request_time:.2f} seconds")
            print(f"RAG Used: {data.get('rag_used', False)}")
            print(f"RAG Count: {data.get('rag_count', 0)}")
            print(f"Processing Time: {data.get('processing_time', 0):.2f} seconds")
            
            print("\n===== Response Content =====")
            print(data.get('result', "No result"))
            
            # הצגת מקורות אם יש
            if data.get('sources'):
                print("\n===== Sources =====")
                for i, source in enumerate(data['sources']):
                    print(f"Source {i+1}: {source.get('title', 'Unknown')} (Score: {source.get('similarity', 0):.2f})")
            
            return data
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

if __name__ == "__main__":
    # בדיקת ה-API
    message = "מה אומר סעיף 8.7 בתקנון?" if len(sys.argv) <= 1 else sys.argv[1]
    print("\n\n========== HEBREW TEST (5 sec timeout) ==========")
    
    # בדיקה עם timeout קצר יותר
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": message,
                "use_rag": True,
                "add_sources": True
            },
            timeout=5  # זמן קצר יותר
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"RAG Used: {data.get('rag_used', False)}")
            print(f"RAG Count: {data.get('rag_count', 0)}")
            print(f"Processing Time: {data.get('processing_time', 0):.2f} seconds")
            print("\nResponse Start:")
            print(data.get('result', "No result")[:200] + "..." if len(data.get('result', "")) > 200 else data.get('result', ""))
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Exception (expected for Hebrew): {str(e)}")
    
    print("\n\n========== ENGLISH TEST ==========")
    test_chat_api("What does section 8.7 of the afeka regulations say?", use_rag=True) 