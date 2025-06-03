import os
import logging
import dotenv
import requests
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

def clean_database_urgent():
    """ניקוי מהיר ובכוח של כל המסמכים והצ'אנקים"""
    try:
        logger.info("מתחיל ניקוי חירום...")
        
        # מחיקת כל הצ'אנקים ישירות באמצעות SQL
        try:
            # בדיקה אם יש צ'אנקים באמצעות שאילתה פשוטה
            chunks = supabase.table("document_chunks").select("id").execute()
            chunk_count = len(chunks.data)
            logger.info(f"נמצאו {chunk_count} צ'אנקים")
            
            # שאילתת SQL ישירה למחיקת כל הצ'אנקים
            sql_query = """
            DELETE FROM document_chunks;
            """
            try_execute_sql(sql_query)
            logger.info("כל הצ'אנקים נמחקו בהצלחה")
            
        except Exception as e:
            logger.error(f"שגיאה במחיקת צ'אנקים: {e}")
            # ניסיון חלופי באמצעות TRUNCATE
            try:
                logger.info("מנסה למחוק צ'אנקים באמצעות API ישיר...")
                truncate_chunks = """
                TRUNCATE TABLE document_chunks RESTART IDENTITY;
                """
                try_execute_sql(truncate_chunks)
                logger.info("מחיקת צ'אנקים הושלמה באמצעות TRUNCATE")
            except Exception as e2:
                logger.error(f"גם TRUNCATE נכשל: {e2}")
        
        # מחיקת כל המסמכים ישירות
        try:
            # בדיקה אם יש מסמכים
            docs = supabase.table("documents").select("id").execute()
            doc_count = len(docs.data)
            logger.info(f"נמצאו {doc_count} מסמכים")
            
            # שאילתת SQL ישירה למחיקת כל המסמכים
            sql_query = """
            DELETE FROM documents;
            """
            try_execute_sql(sql_query)
            logger.info("כל המסמכים נמחקו בהצלחה")
            
        except Exception as e:
            logger.error(f"שגיאה במחיקת מסמכים: {e}")
            # ניסיון חלופי באמצעות TRUNCATE
            try:
                logger.info("מנסה למחוק מסמכים באמצעות API ישיר...")
                truncate_docs = """
                TRUNCATE TABLE documents RESTART IDENTITY CASCADE;
                """
                try_execute_sql(truncate_docs)
                logger.info("מחיקת מסמכים הושלמה באמצעות TRUNCATE")
            except Exception as e2:
                logger.error(f"גם TRUNCATE נכשל: {e2}")
        
        logger.info("ניקוי החירום הושלם")
        
    except Exception as e:
        logger.error(f"שגיאה בניקוי חירום: {e}")

def try_execute_sql(sql_query):
    """מנסה להריץ שאילתת SQL במספר דרכים שונות"""
    
    # ניסיון 1: באמצעות Supabase REST API
    try:
        logger.info("מנסה להריץ SQL דרך REST API...")
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        response = requests.post(
            f"{supabase_url}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={"query": sql_query}
        )
        
        if response.status_code < 400:
            logger.info("SQL הורץ בהצלחה דרך REST API")
            return response.json() if response.text else {"status": "success"}
        else:
            logger.warning(f"שגיאה בהרצת SQL דרך REST API: {response.text}")
            raise Exception(f"REST API שגיאה: {response.text}")
            
    except Exception as e:
        logger.warning(f"ניסיון 1 נכשל: {e}")
    
    # ניסיון 2: באמצעות PostgreSQL connection string אם זמין
    try:
        logger.info("מנסה להריץ SQL ישירות דרך PostgreSQL...")
        pg_connection_string = os.getenv('DATABASE_URL')
        
        if pg_connection_string:
            import psycopg2
            conn = psycopg2.connect(pg_connection_string)
            cursor = conn.cursor()
            cursor.execute(sql_query)
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("SQL הורץ בהצלחה דרך PostgreSQL ישיר")
            return {"status": "success"}
        else:
            raise Exception("אין מחרוזת חיבור ל-PostgreSQL")
            
    except Exception as e:
        logger.warning(f"ניסיון 2 נכשל: {e}")
    
    # ניסיון 3: באמצעות פונקציית RPC מותאמת אישית אם קיימת
    try:
        logger.info("מנסה להריץ SQL דרך RPC...")
        response = supabase.rpc("exec_sql", {"query": sql_query}).execute()
        logger.info("SQL הורץ בהצלחה דרך RPC")
        return response
        
    except Exception as e:
        logger.warning(f"ניסיון 3 נכשל: {e}")
        raise Exception("כל הניסיונות להריץ SQL נכשלו")

if __name__ == "__main__":
    clean_database_urgent() 