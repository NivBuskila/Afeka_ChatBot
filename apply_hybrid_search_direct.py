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

def apply_hybrid_search_function():
    """יישום ישיר של פונקציית החיפוש ההיברידי לבסיס הנתונים"""
    try:
        logger.info("מתחיל ליישם את פונקציית החיפוש ההיברידי...")
        
        # קריאת קובץ ה-SQL
        sql_file_path = "src/supabase/fix_hybrid_search.sql"
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # פיצול הקובץ לפקודות נפרדות לביצוע נפרד
        sql_statements = split_sql_file(sql_content)
        
        # ביצוע כל אחת מהפקודות בנפרד
        for i, sql in enumerate(sql_statements):
            if sql.strip():  # רק אם השאילתה אינה ריקה
                logger.info(f"מריץ שאילתה {i+1}/{len(sql_statements)}...")
                try:
                    result = execute_sql_directly(sql)
                    logger.info(f"שאילתה {i+1} בוצעה בהצלחה")
                except Exception as e:
                    logger.error(f"שגיאה בשאילתה {i+1}: {e}")
        
        # בדיקת הפונקציה
        try:
            logger.info("בודק אם הפונקציה הותקנה בהצלחה...")
            test_query = "SELECT * FROM hybrid_search_documents(array_fill(0::float, ARRAY[768]), 'בדיקה', 0.5, 5);"
            result = execute_sql_directly(test_query)
            logger.info("הפונקציה הותקנה בהצלחה!")
        except Exception as e:
            logger.error(f"הפונקציה לא הותקנה כראוי: {e}")
        
        logger.info("תהליך יישום פונקציית החיפוש ההיברידי הסתיים")
        
    except Exception as e:
        logger.error(f"שגיאה ביישום פונקציית החיפוש ההיברידי: {e}")

def split_sql_file(sql_content):
    """מפצל קובץ SQL לפקודות נפרדות"""
    # פיצול לפי ; עם התייחסות למקרים מיוחדים
    statements = []
    current_statement = []
    
    in_function_body = False
    in_do_block = False
    
    for line in sql_content.split('\n'):
        stripped_line = line.strip()
        
        # מעקב אחר מצב תוך פונקציה/בלוק
        if "CREATE OR REPLACE FUNCTION" in line or "CREATE FUNCTION" in line:
            in_function_body = True
        elif "DO $$" in line:
            in_do_block = True
        
        # הוספת השורה לפקודה הנוכחית
        current_statement.append(line)
        
        # בדיקת סיום פונקציה/בלוק/פקודה
        if in_function_body and stripped_line.endswith('$$;'):
            in_function_body = False
            statements.append('\n'.join(current_statement))
            current_statement = []
        elif in_do_block and stripped_line.endswith('$$;'):
            in_do_block = False
            statements.append('\n'.join(current_statement))
            current_statement = []
        elif not in_function_body and not in_do_block and stripped_line.endswith(';'):
            # רק אם לא בתוך פונקציה או בלוק
            if not any(kw in stripped_line for kw in ['--', 'END;']):  # לא הערה ולא סיום בלוק
                statements.append('\n'.join(current_statement))
                current_statement = []
    
    # טיפול בהצהרה אחרונה אם נשארה
    if current_statement:
        statements.append('\n'.join(current_statement))
    
    return statements

def execute_sql_directly(sql_query):
    """הרצת שאילתת SQL ישירות דרך REST API"""
    try:
        # שימוש בפונקציית rpc קיימת אם יש, אחרת שימוש בשאילתה ישירה
        try:
            response = supabase.rpc("exec_sql", {"query": sql_query}).execute()
            return response
        except Exception as e:
            logger.warning(f"שגיאה בשימוש ב-RPC: {e}")
            # בקשה ישירה למסד הנתונים
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            # ניסיון להתחבר ישירות ל-REST API של Postgres 
            url = f"{supabase_url}/rest/v1/rpc/exec_sql"
            response = requests.post(url, headers=headers, json={"query": sql_query})
            
            if response.status_code >= 400:
                error_text = response.text
                if len(error_text) > 500:
                    error_text = error_text[:500] + "..."
                logger.error(f"SQL error (status {response.status_code}): {error_text}")
                
                # ניסיון דרך נקודת קצה חלופית
                logger.warning("מנסה דרך נקודת קצה חלופית...")
                url = f"{supabase_url}/rest/v1/"
                response = requests.post(url, headers=headers, json={"query": sql_query})
                
                if response.status_code >= 400:
                    error_text = response.text
                    if len(error_text) > 500:
                        error_text = error_text[:500] + "..."
                    logger.error(f"SQL error (alternative endpoint): {error_text}")
                    
                    # אם עדיין נכשל, ננסה להשתמש ב-PostgREST ישירות
                    logger.warning("מנסה להתחבר ל-PostgREST ישירות...")
                    headers["Content-Type"] = "text/plain"
                    response = requests.post(
                        f"{supabase_url}/rest/v1/",
                        headers=headers,
                        data=sql_query
                    )
                    
                    if response.status_code >= 400:
                        raise Exception(f"SQL error via direct PostgREST: {response.text}")
            
            return response.json() if response.text else {"status": "success"}
            
    except Exception as e:
        logger.error(f"Error executing SQL: {e}")
        raise

if __name__ == "__main__":
    apply_hybrid_search_function() 