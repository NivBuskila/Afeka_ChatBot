import os
import logging
import time
import dotenv
from supabase import create_client

# הגדרת לוגר
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# טעינת משתני סביבה
dotenv.load_dotenv()
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

# יצירת לקוח Supabase
supabase = create_client(supabase_url, supabase_key)

def delete_all_documents():
    """מחיקת כל המסמכים אחד אחד (כולל chunks)"""
    try:
        # קבלת רשימת המסמכים
        response = supabase.table("documents").select("id,name,status").execute()
        documents = response.data
        logger.info(f"נמצאו {len(documents)} מסמכים")
        
        for doc in documents:
            doc_id = doc["id"]
            doc_name = doc["name"]
            doc_status = doc["status"]
            
            logger.info(f"מוחק מסמך ID={doc_id}, שם={doc_name}, סטטוס={doc_status}")
            
            # 1. מחיקת כל ה-chunks של המסמך
            try:
                # בדיקת כמה chunks יש למסמך
                chunks_response = supabase.table("document_chunks").select("id").eq("document_id", doc_id).execute()
                chunks = chunks_response.data
                chunk_count = len(chunks)
                logger.info(f"מוחק {chunk_count} chunks למסמך {doc_id}")
                
                # מחיקה בקבוצות של 50 כדי למנוע timeout
                batch_size = 50
                for i in range(0, chunk_count, batch_size):
                    batch = chunks[i:i+batch_size]
                    chunk_ids = [chunk["id"] for chunk in batch]
                    
                    if chunk_ids:
                        logger.info(f"מוחק קבוצת chunks {i+1} עד {i+len(batch)} מתוך {chunk_count}")
                        delete_response = supabase.table("document_chunks").delete().in_("id", chunk_ids).execute()
                        time.sleep(1)  # המתנה קצרה בין בקשות
                
                logger.info(f"הושלמה מחיקת {chunk_count} chunks למסמך {doc_id}")
            except Exception as e:
                logger.error(f"שגיאה במחיקת chunks למסמך {doc_id}: {e}")
            
            # 2. מחיקת רשומת המסמך עצמו
            try:
                time.sleep(2)  # המתנה לפני מחיקת המסמך
                delete_response = supabase.table("documents").delete().eq("id", doc_id).execute()
                logger.info(f"המסמך {doc_id} נמחק בהצלחה")
            except Exception as e:
                logger.error(f"שגיאה במחיקת המסמך {doc_id}: {e}")
        
        logger.info("הושלמה מחיקת כל המסמכים")
    
    except Exception as e:
        logger.error(f"שגיאה כללית: {e}")

if __name__ == "__main__":
    delete_all_documents() 