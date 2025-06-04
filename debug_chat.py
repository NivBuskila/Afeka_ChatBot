import requests
import json

def test_with_debug():
    # בדיקה עם שאלה ברורה על התקנון
    test_cases = [
        "מה כתוב בסעיף 1.5.2 בתקנון?",
        "מה זה 'על תנאי' בתקנון אפקה?",
        "מה הן הדרישות לסטודנט על תנאי?"
    ]
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n=== בדיקה {i}: {question} ===")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/chat",
                json={
                    "message": question,
                    "user_id": "test",
                    "history": []
                },
                timeout=15
            )
            
            print(f"סטטוס: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("תשובה:")
                print(result.get("response", "אין תשובה"))
                
                if "sources" in result:
                    print(f"\nמקורות: {len(result['sources'])}")
            else:
                print(f"שגיאה: {response.text}")
                
        except Exception as e:
            print(f"שגיאה: {e}")

if __name__ == "__main__":
    test_with_debug() 