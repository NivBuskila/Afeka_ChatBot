#!/usr/bin/env python
"""
סקריפט פשוט להורדת מסמכים מ-Supabase, שמירתם בתיקיית docs,
וטעינתם למערכת RAG.
"""
import os
import logging
import sys
from dotenv import load_dotenv
import supabase
from pathlib import Path

# טעינת משתני סביבה מקובץ .env
load_dotenv()

# הגדרת לוגר
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_documents_from_supabase(supabase_url, supabase_key, output_dir="../../data/docs"):
    """
    הורדת מסמכים מ-Supabase ושמירתם בתיקיית הפלט.
    """
    try:
        # יצירת לקוח Supabase
        client = supabase.create_client(supabase_url, supabase_key)
        logger.info("התחברות ל-Supabase בוצעה בהצלחה")
        
        # יצירת נתיב אבסולוטי לתיקיית הפלט
        current_dir = Path(__file__).parent
        absolute_output_dir = (current_dir / output_dir).resolve()
        logger.info(f"תיקיית היעד: {absolute_output_dir}")
        
        # יצירת תיקיית הפלט אם לא קיימת
        os.makedirs(absolute_output_dir, exist_ok=True)
        
        # ביצוע שאילתה לקבלת כל המסמכים
        response = client.table("documents").select("*").execute()
        
        if not hasattr(response, 'data') or not response.data:
            logger.warning("לא נמצאו מסמכים ב-Supabase")
            return False
            
        documents = response.data
        logger.info(f"נמצאו {len(documents)} מסמכים ב-Supabase")
        
        # שמירת כל מסמך בקובץ
        files_saved = 0
        for doc in documents:
            doc_id = doc.get('id')
            doc_name = doc.get('name', f"doc_{doc_id}")
            doc_content = doc.get('content')
            
            # אם אין תוכן, דילוג
            if not doc_content:
                logger.warning(f"אין תוכן למסמך {doc_id} - מדלג")
                continue
            
            # יצירת שם קובץ בטוח
            safe_name = "".join(c for c in doc_name if c.isalnum() or c in "._- ").strip().replace(' ', '_')
            file_path = os.path.join(absolute_output_dir, f"{safe_name}.txt")
            
            # שמירה לקובץ
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            logger.info(f"נשמר מסמך {doc_id} לקובץ {file_path}")
            files_saved += 1
        
        logger.info(f"נשמרו בהצלחה {files_saved} מתוך {len(documents)} מסמכים")
        return absolute_output_dir if files_saved > 0 else False
        
    except Exception as e:
        logger.error(f"שגיאה בהורדת מסמכים מ-Supabase: {e}")
        return False

def load_documents_to_rag(docs_dir):
    """
    טעינת מסמכים מתיקיית docs למערכת RAG.
    """
    try:
        from core.rag import AfekaRAG
        
        # קבלת מפתח API מהסביבה
        api_key = os.environ.get('GEMINI_API_KEY')
        vector_store_dir = os.environ.get('VECTOR_STORE_DIR', '../../data/vector_store')
        
        if not api_key:
            logger.error("לא נמצא GEMINI_API_KEY במשתני הסביבה")
            return False
        
        # יצירת נתיב אבסולוטי לתיקיית vector store
        current_dir = Path(__file__).parent
        absolute_vector_store_dir = (current_dir / vector_store_dir).resolve()
        logger.info(f"תיקיית vector store: {absolute_vector_store_dir}")
        
        # יצירת תיקיית vector store אם לא קיימת
        os.makedirs(absolute_vector_store_dir, exist_ok=True)
        
        # יצירת מופע RAG
        rag = AfekaRAG(
            api_key=api_key,
            persist_directory=str(absolute_vector_store_dir),
            collection_name="afeka_docs"
        )
        
        # טעינת מסמכים מהתיקייה
        success = rag.load_directory(
            directory_path=str(docs_dir),
            glob_pattern="**/*.txt",
            chunk_size=1000,
            chunk_overlap=200
        )
        
        if success:
            logger.info(f"מסמכים נטענו בהצלחה מ-{docs_dir} ל-RAG")
            return True
        else:
            logger.error(f"נכשל בטעינת מסמכים מ-{docs_dir} ל-RAG")
            return False
            
    except Exception as e:
        logger.error(f"שגיאה בטעינת מסמכים ל-RAG: {e}")
        return False

def main():
    """נקודת כניסה ראשית"""
    # קבלת פרטי התחברות ל-Supabase ממשתני הסביבה
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("יש להגדיר SUPABASE_URL ו-SUPABASE_KEY במשתני הסביבה")
        return 1
    
    output_dir = "../../data/docs"
    
    # הורדת מסמכים מ-Supabase
    result = download_documents_from_supabase(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        output_dir=output_dir
    )
    
    if not result:
        logger.error("נכשל בהורדת מסמכים מ-Supabase")
        return 1
    
    # טעינת מסמכים ל-RAG
    success = load_documents_to_rag(result)
    if not success:
        logger.error("נכשל בטעינת מסמכים ל-RAG")
        return 1
    
    logger.info("עיבוד המסמכים הושלם בהצלחה")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 