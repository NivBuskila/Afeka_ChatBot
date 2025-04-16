#!/usr/bin/env python
"""
סקריפט פשוט לבדיקת Gemini API
הפעלה: python test_gemini.py
"""
import os
from google import genai

def main():
    # קבלת מפתח ה-API (יש להגדיר משתנה סביבה או להשתמש בברירת מחדל מהקוד)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s')
    
    print("בדיקת חיבור ל-Gemini API")
    print("-------------------------")
    print(f"משתמש במפתח API: {GEMINI_API_KEY[:5]}...")

    # יצירת מופע Client
    genai_client = genai.Client(api_key=GEMINI_API_KEY)
    
    # בדיקת חיבור על ידי שליחת בקשה פשוטה
    print("\nשולח בקשה לג'מיני...")
    try:
        response = genai_client.models.generate_content(
            model="gemini-2.0-flash",
            contents="הצג את עצמך בקצרה בעברית"
        )
        
        print("\nתשובה מג'מיני:")
        print("----------------")
        print(response.text)
        print("\nהבדיקה הצליחה!")
        
        # לולאת שאלות אינטראקטיבית
        print("\nמוכן לשאלות (הקלד 'יציאה' כדי לסיים):")
        while True:
            user_input = input("\nשאלה: ")
            if user_input.lower() in ['exit', 'quit', 'יציאה']:
                break
                
            if not user_input.strip():
                continue
                
            try:
                response = genai_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=user_input
                )
                print("\nתשובה:")
                print(response.text)
            except Exception as e:
                print(f"שגיאה: {e}")
                
    except Exception as e:
        print(f"שגיאה בחיבור לג'מיני: {e}")
        print("אנא ודא שמפתח ה-API תקין ושיש לך חיבור לאינטרנט.")

if __name__ == "__main__":
    main() 