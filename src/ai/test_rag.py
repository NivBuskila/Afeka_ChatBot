#!/usr/bin/env python
"""
כלי בדיקה למערכת RAG - מאפשר לשלוח שאלות ולראות את התהליך המלא של מציאת מידע רלוונטי ויצירת תשובה
"""
import os
import sys
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from dotenv import load_dotenv
from langchain_core.documents import Document

# הגדרת הלוגר
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# טעינת משתני סביבה
load_dotenv()

# וידוא שה-core נמצא ב-path
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(current_dir))

# יבוא טוען המסמכים הפשוט
try:
    from document_loader import SimpleTextLoader
except ImportError:
    # אם לא נמצא, ניצור מחלקה פשוטה במקום
    logger.warning("מודול document_loader לא נמצא. יוצר טוען פשוט מקומי.")
    
    class SimpleTextLoader:
        """טוען מסמכים פשוט מקומי"""
        
        @staticmethod
        def load_file(file_path: str, encoding: str = 'utf-8') -> Optional[Document]:
            try:
                file_path = Path(file_path)
                
                if not file_path.exists():
                    logger.error(f"הקובץ {file_path} לא קיים")
                    return None
                    
                if not file_path.name.endswith('.txt'):
                    logger.warning(f"הקובץ {file_path} אינו קובץ טקסט. מסנן...")
                    return None
                
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                metadata = {
                    "source": str(file_path.name),
                    "file_path": str(file_path),
                    "file_type": "text",
                }
                
                lines = content.split('\n')
                if lines and lines[0].startswith('סגנון מסמך:'):
                    style_tag = lines[0].replace('סגנון מסמך:', '').strip()
                    metadata["document_style"] = style_tag
                
                return Document(page_content=content, metadata=metadata)
                
            except Exception as e:
                logger.error(f"שגיאה בטעינת הקובץ {file_path}: {e}")
                return None
                
        @staticmethod
        def load_directory(directory_path: str, glob_pattern: str = "**/*.txt", encoding: str = 'utf-8') -> List[Document]:
            try:
                directory = Path(directory_path)
                
                if not directory.exists() or not directory.is_dir():
                    logger.error(f"התיקייה {directory} לא קיימת")
                    return []
                
                documents = []
                for file_path in directory.glob(glob_pattern):
                    if file_path.is_file():
                        document = SimpleTextLoader.load_file(str(file_path), encoding)
                        if document:
                            documents.append(document)
                            logger.info(f"נטען בהצלחה: {file_path.name}")
                
                return documents
                
            except Exception as e:
                logger.error(f"שגיאה בטעינת קבצים מהתיקייה {directory_path}: {e}")
                return []

# יבוא עבור vectorstore
try:
    from langchain_core.vectorstores import VectorStore
    from langchain_chroma import Chroma
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    logger.error("לא ניתן לטעון את מודולי ה-vector store. ודא שהספריות מותקנות.")
    sys.exit(1)

class RAGTester:
    """מחלקה לבדיקה ושליטה על מערכת RAG"""
    
    def __init__(self, api_key: Optional[str] = None, vector_store_dir: Optional[str] = None, collection_name: str = "afeka_docs"):
        """
        אתחול בודק ה-RAG
        
        Args:
            api_key: מפתח ה-API של Gemini (ברירת מחדל: נלקח ממשתני הסביבה)
            vector_store_dir: תיקיית ה-vector store (ברירת מחדל: נלקח ממשתני הסביבה)
            collection_name: שם האוסף במאגר הוקטורי
        """
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("לא נמצא מפתח API. יש להגדיר GEMINI_API_KEY במשתני הסביבה או להעביר כפרמטר.")
        
        self.vector_store_dir = vector_store_dir or os.environ.get('VECTOR_STORE_DIR', './data/vector_store')
        self.collection_name = collection_name
        
        # יצירת נתיב אבסולוטי
        vector_store_path = Path(self.vector_store_dir)
        if not vector_store_path.is_absolute():
            self.vector_store_dir = str((root_dir / vector_store_path).resolve())
            
        logger.info(f"שימוש בתיקיית vector store: {self.vector_store_dir}")
        
        self.vector_store = None
        self.last_question = None
        self.last_answer = None
        self.last_docs = None
        
    def load_documents(self, docs_dir: str, glob_pattern: str = "**/*.txt", reset_vector_store: bool = False) -> bool:
        """
        טעינת מסמכים למערכת ה-RAG
        
        Args:
            docs_dir: תיקיית המסמכים
            glob_pattern: תבנית לבחירת קבצים
            reset_vector_store: האם למחוק מאגר וקטורי קיים ולהתחיל מחדש
            
        Returns:
            bool: האם הטעינה הצליחה
        """
        # בדיקה שהתיקייה קיימת
        docs_path = Path(docs_dir)
        if not docs_path.exists():
            logger.error(f"תיקיית המסמכים {docs_dir} לא קיימת")
            return False
            
        if not docs_path.is_absolute():
            docs_dir = str((root_dir / docs_path).resolve())
            
        logger.info(f"טוען מסמכים מ: {docs_dir}")
        
        try:
            # טען את המסמכים באמצעות הטוען הפשוט
            docs = SimpleTextLoader.load_directory(docs_dir, glob_pattern)
            
            if not docs:
                logger.error(f"לא נמצאו מסמכים בתיקייה {docs_dir}")
                return False
            
            logger.info(f"נטענו {len(docs)} מסמכים")
            
            # יצירת vector store ישירות
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=self.api_key)
            
            # מחיקת מאגר וקטורי קיים אם התבקש
            if reset_vector_store and os.path.exists(self.vector_store_dir):
                logger.info(f"מוחק vector store קיים מ-{self.vector_store_dir}")
                shutil.rmtree(self.vector_store_dir)
            
            os.makedirs(self.vector_store_dir, exist_ok=True)
            
            # נסיון ליצור vector store חדש
            try:
                logger.info(f"יוצר vector store חדש ב-{self.vector_store_dir}")
                self.vector_store = Chroma.from_documents(
                    documents=docs,
                    embedding=embeddings,
                    persist_directory=self.vector_store_dir,
                    collection_name=self.collection_name
                )
                self.vector_store.persist()
                logger.info(f"מסמכים נטענו והוכנסו ל-vector store בהצלחה")
                return True
            except Exception as e:
                logger.error(f"שגיאה ביצירת vector store: {e}")
                
                # אם נכשל, ננסה למחוק ולנסות שוב
                logger.info("מנסה למחוק את מאגר הוקטורים ולנסות שוב")
                if os.path.exists(self.vector_store_dir):
                    shutil.rmtree(self.vector_store_dir)
                
                os.makedirs(self.vector_store_dir, exist_ok=True)
                
                # נסיון אחרון ליצור vector store חדש
                try:
                    logger.info(f"יוצר vector store חדש (ניסיון שני) ב-{self.vector_store_dir}")
                    self.vector_store = Chroma.from_documents(
                        documents=docs,
                        embedding=embeddings,
                        persist_directory=self.vector_store_dir,
                        collection_name=self.collection_name
                    )
                    self.vector_store.persist()
                    logger.info(f"מסמכים נטענו והוכנסו ל-vector store בהצלחה")
                    return True
                except Exception as e2:
                    logger.error(f"שגיאה ביצירת vector store (ניסיון שני): {e2}")
                    return False
                
        except Exception as e:
            logger.error(f"שגיאה בטעינת מסמכים: {e}")
            return False
    
    def ask(self, question: str, debug: bool = True, max_docs: int = 5) -> str:
        """
        שליחת שאלה למערכת ה-RAG וקבלת תשובה
        
        Args:
            question: השאלה לשאול
            debug: האם להציג מידע לצורכי דיבאג
            max_docs: מספר מקסימלי של מסמכים להציג
            
        Returns:
            str: התשובה מהמערכת
        """
        self.last_question = question
        
        # צור שאילתה והצג את התהליך
        if debug:
            logger.info("\n" + "="*50)
            logger.info(f"שאלה: {question}")
            logger.info("="*50)
        
        try:
            # בדיקה שיש לנו vector store
            if not self.vector_store:
                logger.error("לא נמצא vector store. יש לטעון מסמכים קודם.")
                return "נא לטעון מסמכים למערכת לפני שאילת שאלות."
            
            # חיפוש מסמכים רלוונטיים
            try:
                docs = self.vector_store.similarity_search(question, k=max_docs)
                self.last_docs = docs
            except Exception as e:
                logger.error(f"שגיאה בחיפוש מסמכים: {e}")
                return f"שגיאה בחיפוש מסמכים: {e}"
            
            if not docs:
                logger.warning("לא נמצאו מסמכים רלוונטיים לשאלה")
                return "לא נמצאו מסמכים רלוונטיים לשאלה. נסה לנסח את השאלה אחרת."
            
            if debug:
                logger.info("\nמסמכים רלוונטיים שנמצאו:")
                logger.info("-"*50)
                for i, doc in enumerate(docs[:max_docs], 1):
                    logger.info(f"מסמך {i}:")
                    logger.info(f"מקור: {doc.metadata.get('source', 'לא ידוע')}")
                    content_preview = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
                    logger.info(f"תוכן: {content_preview}")
                    logger.info("-"*50)
            
            # בניית הפרומפט
            context = "\n\n".join([doc.page_content for doc in docs])
            
            prompt = f"""
            אתה עוזר לסטודנטים במכללת אפקה להנדסה. השב על השאלה בהתבסס על המידע הבא בלבד.
            אם המידע לא מכיל תשובה ברורה, ציין זאת ואל תמציא מידע.
            השתמש בשפה עברית בתשובתך.
            
            מידע:
            {context}
            
            שאלה: {question}
            
            תשובה:
            """
            
            # קבלת תשובה מהמודל
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", 
                google_api_key=self.api_key,
                temperature=0.2,
                convert_system_message_to_human=True
            )
            
            response = llm.invoke(prompt)
            answer = response.content
            self.last_answer = answer
            
            if debug:
                logger.info("\nתשובה:")
                logger.info("-"*50)
                logger.info(answer)
                logger.info("-"*50)
            
            return answer
            
        except Exception as e:
            logger.error(f"שגיאה בשאלה: {e}")
            return f"אירעה שגיאה: {str(e)}"
    
    def save_last_interaction(self, output_file: str):
        """
        שמירת האינטראקציה האחרונה לקובץ
        
        Args:
            output_file: שם הקובץ לשמירה
        """
        if not all([self.last_question, self.last_answer, self.last_docs]):
            logger.error("אין אינטראקציה אחרונה לשמירה")
            return
            
        interaction = {
            "question": self.last_question,
            "documents": [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "לא ידוע"),
                    "metadata": doc.metadata
                }
                for doc in self.last_docs
            ],
            "answer": self.last_answer
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(interaction, f, ensure_ascii=False, indent=2)
            
        logger.info(f"האינטראקציה נשמרה לקובץ: {output_file}")
    
    def interactive_mode(self):
        """מצב אינטראקטיבי לשאילת שאלות"""
        logger.info("\n" + "="*50)
        logger.info("מצב אינטראקטיבי של מערכת ה-RAG")
        logger.info("הקלד 'exit' או 'quit' כדי לצאת")
        logger.info("הקלד 'save <filename>' כדי לשמור את האינטראקציה האחרונה")
        logger.info("="*50 + "\n")
        
        while True:
            try:
                question = input("\nשאלה: ")
                
                if question.lower() in ['exit', 'quit', 'יציאה']:
                    break
                    
                if question.lower().startswith('save ') or question.lower().startswith('שמור '):
                    parts = question.split(' ', 1)
                    if len(parts) > 1:
                        filename = parts[1]
                        self.save_last_interaction(filename)
                    else:
                        logger.error("נא לציין שם קובץ")
                    continue
                
                if not question.strip():
                    continue
                    
                self.ask(question)
                
            except KeyboardInterrupt:
                print("\nיציאה...")
                break
            except Exception as e:
                logger.error(f"שגיאה: {e}")

def main():
    """נקודת כניסה ראשית"""
    import argparse
    
    parser = argparse.ArgumentParser(description="כלי בדיקה למערכת RAG")
    parser.add_argument("--vector-store", default=None, help="נתיב לתיקיית ה-vector store")
    parser.add_argument("--load-docs", default=None, help="נתיב לתיקיית מסמכים לטעינה")
    parser.add_argument("--question", "-q", default=None, help="שאלה לשאול")
    parser.add_argument("--save", "-s", default=None, help="שמירת התוצאה לקובץ")
    parser.add_argument("--reset", action="store_true", help="מחיקת מאגר וקטורי קיים ויצירת מאגר חדש")
    
    args = parser.parse_args()
    
    try:
        # יצירת בודק RAG
        tester = RAGTester(vector_store_dir=args.vector_store)
        
        # טעינת מסמכים אם צוין
        if args.load_docs:
            if not tester.load_documents(args.load_docs, reset_vector_store=args.reset):
                logger.error(f"לא ניתן לטעון מסמכים מ-{args.load_docs}")
                return 1
        
        # שאילת שאלה אם צוינה
        if args.question:
            answer = tester.ask(args.question)
            
            # שמירה לקובץ אם צוין
            if args.save:
                tester.save_last_interaction(args.save)
                
            return 0
        
        # מצב אינטראקטיבי כברירת מחדל
        tester.interactive_mode()
        
    except Exception as e:
        logger.error(f"שגיאה: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 