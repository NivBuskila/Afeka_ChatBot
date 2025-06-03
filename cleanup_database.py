#!/usr/bin/env python
'''
סקריפט לניקוי מסד הנתונים ותיקון הגדרות הצ'אנקינג
זה יסיר את כל הווקטורים והמסמכים הקיימים ויעדכן את הגדרות החלוקה למסמכים
'''

import os
import sys
import asyncio
import logging
from pathlib import Path
import dotenv
from supabase import create_client

# הגדרת לוגר
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# הגדרות חדשות לחלוקת מסמכים
NEW_CHUNK_SIZE = 2000  # גודל חדש לצ'אנק (הרבה יותר גדול מהקודם - 800)
NEW_CHUNK_OVERLAP = 200  # חפיפה חדשה בין צ'אנקים
MAX_VECTORS = 500  # הגבלת מספר וקטורים למסמך

async def update_document_processor():
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

async def delete_all_data(supabase_client):
    """מחיקת כל הנתונים ממסד הנתונים"""
    try:
        # קבלת רשימת המסמכים
        response = supabase_client.table("documents").select("id").execute()
        if not response.data:
            logger.info("אין מסמכים במסד הנתונים")
            return True
        
        document_ids = [doc['id'] for doc in response.data]
        logger.info(f"נמצאו {len(document_ids)} מסמכים למחיקה")
        
        # מחיקת קטעי טקסט (chunks) מכל המסמכים
        for doc_id in document_ids:
            try:
                # מחיקת קטעים מטבלת document_chunks
                chunks_response = supabase_client.table("document_chunks").delete().eq("document_id", doc_id).execute()
                logger.info(f"נמחקו קטעים ממסמך {doc_id} בטבלת document_chunks: {len(chunks_response.data) if hasattr(chunks_response, 'data') else 0} קטעים")
                
                # מחיקת קטעים מטבלת embeddings (לתאימות לאחור)
                embeddings_response = supabase_client.table("embeddings").delete().eq("document_id", doc_id).execute()
                logger.info(f"נמחקו קטעים ממסמך {doc_id} בטבלת embeddings: {len(embeddings_response.data) if hasattr(embeddings_response, 'data') else 0} קטעים")
            except Exception as e_chunks:
                logger.error(f"שגיאה במחיקת קטעים ממסמך {doc_id}: {e_chunks}")
        
        # מחיקת כל המסמכים
        docs_response = supabase_client.table("documents").delete().in_("id", document_ids).execute()
        logger.info(f"נמחקו {len(docs_response.data) if hasattr(docs_response, 'data') else 0} מסמכים מטבלת documents")
        
        return True
    except Exception as e:
        logger.error(f"שגיאה במחיקת נתונים: {e}")
        return False

async def main():
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
    
    # 1. מחיקת כל הנתונים
    logger.info("מתחיל מחיקת נתונים...")
    if await delete_all_data(supabase):
        logger.info("כל הנתונים נמחקו בהצלחה")
    else:
        logger.error("שגיאה במחיקת הנתונים")
    
    # 2. עדכון הגדרות document_processor.py
    logger.info("מעדכן את הגדרות החלוקה...")
    if await update_document_processor():
        logger.info("הגדרות החלוקה עודכנו בהצלחה")
    else:
        logger.error("שגיאה בעדכון הגדרות החלוקה")
    
    logger.info("הפעולות הסתיימו")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 