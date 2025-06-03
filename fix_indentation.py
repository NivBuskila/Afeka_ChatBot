#!/usr/bin/env python
'''
סקריפט לתיקון הגדרות הצ'אנקינג ובדיקת מצב מסד הנתונים
'''

import os
import sys
import logging
from pathlib import Path
import dotenv
from supabase import create_client

# הגדרת לוגר
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# הגדרות חדשות לחלוקת מסמכים
NEW_CHUNK_SIZE = 2000       # גודל חדש לצ'אנק
NEW_CHUNK_OVERLAP = 200     # חפיפה חדשה בין צ'אנקים
MAX_VECTORS = 500           # הגבלת מספר וקטורים למסמך

def update_document_processor():
    """עדכון הגדרות ב-document_processor.py"""
    try:
        filepath = Path("src/backend/services/document_processor.py")
        
        # קריאת הקובץ
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # שמירת גיבוי
        backup_path = filepath.with_suffix(filepath.suffix + '.bak2')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"גיבוי נשמר ל: {backup_path}")
        
        # עדכון הגדרות
        content = content.replace(
            "DEFAULT_CHUNK_SIZE = 800", 
            f"DEFAULT_CHUNK_SIZE = {NEW_CHUNK_SIZE}"
        )
        content = content.replace(
            "DEFAULT_CHUNK_OVERLAP = 100",
            f"DEFAULT_CHUNK_OVERLAP = {NEW_CHUNK_OVERLAP}"
        )
        content = content.replace(
            "MAX_VECTORS_PER_DOCUMENT = 1000",
            f"MAX_VECTORS_PER_DOCUMENT = {MAX_VECTORS}"
        )
        
        # שמירת השינויים
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"document_processor.py עודכן בהצלחה עם: chunk_size={NEW_CHUNK_SIZE}, "
                  f"chunk_overlap={NEW_CHUNK_OVERLAP}, max_vectors={MAX_VECTORS}")
        return True
    except Exception as e:
        logger.error(f"שגיאה בעדכון document_processor.py: {e}")
        return False

def check_database_status(supabase):
    """בדיקת מצב מסד הנתונים: כמה מסמכים ווקטורים יש"""
    try:
        # בדיקת מסמכים
        doc_response = supabase.table("documents").select("id, name, status").execute()
        documents = doc_response.data if hasattr(doc_response, 'data') else []
        
        print("\n--- מצב מסד הנתונים ---")
        print(f"מספר מסמכים: {len(documents)}")
        
        if documents:
            print("\nפירוט המסמכים:")
            for doc in documents:
                print(f"  ID: {doc['id']}, שם: {doc['name']}, סטטוס: {doc['status']}")
                
                # בדיקת מספר chunks לכל מסמך
                chunks_response = supabase.table("document_chunks").select("id").eq("document_id", doc['id']).execute()
                chunks = chunks_response.data if hasattr(chunks_response, 'data') else []
                print(f"    מספר chunks: {len(chunks)}")
        
        # בדיקת חיפוש היברידי
        print("\n--- בדיקת פונקציית חיפוש היברידי ---")
        # ניסיון לבצע חיפוש פשוט כדי לראות אם הפונקציה קיימת
        try:
            query = "test query"
            dummy_embedding = [0.0] * 768  # וקטור דמה
            
            function_call = supabase.rpc(
                "hybrid_search_documents", 
                {
                    "query_embedding": dummy_embedding,
                    "query_text": query,
                    "match_threshold": 0.7,
                    "match_count": 5
                }
            ).execute()
            
            if not hasattr(function_call, 'error') or not function_call.error:
                print("פונקציית החיפוש ההיברידי זמינה ופועלת")
            else:
                print(f"שגיאה בהפעלת פונקציית החיפוש ההיברידי: {function_call.error}")
        except Exception as e:
            print(f"שגיאה בהפעלת פונקציית החיפוש ההיברידי: {e}")
        
        return True
    except Exception as e:
        logger.error(f"שגיאה בבדיקת מצב מסד הנתונים: {e}")
        return False

def main():
    # טעינת משתני סביבה
    dotenv.load_dotenv(override=True)
    
    # בדיקת משתני סביבה
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("חסרים משתני סביבה SUPABASE_URL או SUPABASE_KEY")
        return False
    
    # יצירת קליינט Supabase
    supabase = create_client(supabase_url, supabase_key)
    
    # 1. עדכון הגדרות ה-document_processor
    logger.info("מעדכן את הגדרות החלוקה...")
    update_document_processor()
    
    # 2. בדיקת מצב מסד הנתונים
    logger.info("בודק את מצב מסד הנתונים...")
    check_database_status(supabase)
    
    logger.info("הפעולות הסתיימו")
    return True

if __name__ == "__main__":
    main() 