#!/usr/bin/env python
"""
סקריפט למחיקת מסמך ספציפי מ-Supabase כולל כל הווקטורים המשויכים אליו
"""

import os
import sys
import asyncio
import logging
import time
import dotenv
from supabase import create_client

# הגדרת לוגר
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_document_info(supabase, document_id):
    """קבלת מידע על המסמך"""
    try:
        response = supabase.table("documents").select("*").eq("id", document_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"שגיאה בקבלת מידע על מסמך {document_id}: {e}")
        return None

async def delete_document_chunks(supabase, document_id):
    """מחיקת כל ה-chunks של מסמך מסוים בקבוצות קטנות"""
    try:
        # קבלת ה-IDs של כל ה-chunks
        response = supabase.table("document_chunks").select("id").eq("document_id", document_id).execute()
        if not response.data:
            logger.info(f"לא נמצאו chunks למסמך {document_id}")
            return True
        
        chunk_ids = [chunk["id"] for chunk in response.data]
        logger.info(f"נמצאו {len(chunk_ids)} chunks למסמך {document_id}")
        
        # מחיקה בקבוצות קטנות
        batch_size = 50
        for i in range(0, len(chunk_ids), batch_size):
            batch = chunk_ids[i:i+batch_size]
            logger.info(f"מוחק קבוצת chunks {i+1} עד {min(i+batch_size, len(chunk_ids))} מתוך {len(chunk_ids)}")
            
            try:
                response = supabase.table("document_chunks").delete().in_("id", batch).execute()
                logger.info(f"נמחקו {len(response.data) if hasattr(response, 'data') else 0} chunks בקבוצה")
            except Exception as batch_error:
                logger.error(f"שגיאה במחיקת קבוצת chunks: {batch_error}")
            
            # חכה קצת בין הבקשות כדי לא לעמוס את השרת
            time.sleep(1)
        
        return True
    except Exception as e:
        logger.error(f"שגיאה במחיקת chunks למסמך {document_id}: {e}")
        return False

async def delete_document_record(supabase, document_id):
    """מחיקת הרשומה של המסמך עצמו"""
    try:
        response = supabase.table("documents").delete().eq("id", document_id).execute()
        if response.data and len(response.data) > 0:
            logger.info(f"רשומת המסמך {document_id} נמחקה בהצלחה")
            return True
        else:
            logger.warning(f"לא נמחקה רשומת המסמך {document_id}")
            return False
    except Exception as e:
        logger.error(f"שגיאה במחיקת רשומת המסמך {document_id}: {e}")
        return False

async def list_all_documents(supabase):
    """רשימת כל המסמכים במערכת"""
    try:
        response = supabase.table("documents").select("id, name, status, created_at").order("id", desc=False).execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        logger.error(f"שגיאה בקבלת רשימת המסמכים: {e}")
        return []

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
    
    # בדיקה אם יש ID בארגומנטים
    if len(sys.argv) > 1:
        try:
            document_id = int(sys.argv[1])
            await delete_specific_document(supabase, document_id)
            return
        except ValueError:
            logger.error(f"מזהה מסמך לא תקין: {sys.argv[1]}")
            return
    
    # אם לא התקבל ID - הצג רשימת מסמכים ובקש בחירה
    documents = await list_all_documents(supabase)
    if not documents:
        logger.info("אין מסמכים במערכת")
        return
    
    print("\nרשימת המסמכים במערכת:")
    for i, doc in enumerate(documents):
        print(f"{i+1}. ID: {doc['id']} | שם: {doc['name']} | סטטוס: {doc['status']} | נוצר: {doc['created_at']}")
    
    try:
        choice = input("\nבחר מספר מסמך למחיקה (0 למחיקת הכל): ")
        if choice == '0':
            confirmation = input("האם אתה בטוח שברצונך למחוק את כל המסמכים? (כן/לא): ")
            if confirmation.lower() in ["כן", "yes", "y"]:
                for doc in documents:
                    await delete_specific_document(supabase, doc['id'])
            else:
                logger.info("המחיקה בוטלה")
                return
        else:
            index = int(choice) - 1
            if 0 <= index < len(documents):
                document_id = documents[index]['id']
                await delete_specific_document(supabase, document_id)
            else:
                logger.error("בחירה לא תקינה")
    except ValueError:
        logger.error("קלט לא תקין")
        return

async def delete_specific_document(supabase, document_id):
    """מחיקת מסמך ספציפי - פונקציה מרכזית"""
    logger.info(f"מתחיל מחיקת מסמך {document_id}")
    
    # קבלת מידע על המסמך
    doc_info = await get_document_info(supabase, document_id)
    if not doc_info:
        logger.error(f"לא נמצא מסמך עם ID {document_id}")
        return
    
    logger.info(f"נמצא מסמך: ID={doc_info['id']}, שם={doc_info['name']}, סטטוס={doc_info['status']}")
    confirmation = input(f"האם אתה בטוח שברצונך למחוק את המסמך '{doc_info['name']}'? (כן/לא): ")
    
    if confirmation.lower() not in ["כן", "yes", "y"]:
        logger.info("המחיקה בוטלה")
        return
    
    # מחיקת ה-chunks
    logger.info(f"מתחיל מחיקת chunks למסמך {document_id}")
    chunks_deleted = await delete_document_chunks(supabase, document_id)
    
    if chunks_deleted:
        # מחיקת רשומת המסמך
        logger.info(f"מתחיל מחיקת רשומת המסמך {document_id}")
        doc_deleted = await delete_document_record(supabase, document_id)
        
        if doc_deleted:
            logger.info(f"מסמך {document_id} נמחק בהצלחה כולל כל ה-chunks שלו")
        else:
            logger.warning(f"ה-chunks נמחקו, אבל רשומת המסמך {document_id} לא נמחקה")
    else:
        logger.error(f"שגיאה במחיקת ה-chunks של מסמך {document_id}, המחיקה בוטלה")

if __name__ == "__main__":
    asyncio.run(main()) 