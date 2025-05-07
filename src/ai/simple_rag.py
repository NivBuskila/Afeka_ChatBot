#!/usr/bin/env python
"""
מערכת RAG פשוטה בלי תלויות חיצוניות מסובכות
"""
import os
import sys
import math
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv

import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# הגדרת הלוגר
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# טעינת משתני סביבה
load_dotenv()

class SimpleDocument:
    """מחלקה פשוטה למסמך"""
    
    def __init__(self, content: str, metadata: Dict[str, Any] = None):
        """
        אתחול מסמך
        
        Args:
            content: תוכן המסמך
            metadata: מטה-דאטה של המסמך
        """
        self.content = content
        self.metadata = metadata or {}
        
    def __str__(self) -> str:
        """מחזיר את תוכן המסמך"""
        return self.content

class SimpleLoader:
    """טוען מסמכים פשוט"""
    
    @staticmethod
    def load_file(file_path: str, encoding: str = 'utf-8') -> Optional[SimpleDocument]:
        """
        טעינת קובץ טקסט ויצירת מסמך
        
        Args:
            file_path: נתיב לקובץ
            encoding: קידוד הקובץ
            
        Returns:
            SimpleDocument או None אם הייתה שגיאה
        """
        try:
            file_path = Path(file_path)
            
            # בדיקה שהקובץ קיים
            if not file_path.exists():
                logger.error(f"הקובץ {file_path} לא קיים")
                return None
                
            # בדיקה שהקובץ אכן טקסט
            if not file_path.name.endswith('.txt'):
                logger.warning(f"הקובץ {file_path} אינו קובץ טקסט. מסנן...")
                return None
            
            # קריאת התוכן
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # יצירת מסמך
            metadata = {
                "source": str(file_path.name),
                "file_path": str(file_path),
                "file_type": "text",
            }
            
            # בדיקה של תגיות סגנון בראש המסמך
            lines = content.split('\n')
            if lines and lines[0].startswith('סגנון מסמך:'):
                style_tag = lines[0].replace('סגנון מסמך:', '').strip()
                metadata["document_style"] = style_tag
            
            return SimpleDocument(content=content, metadata=metadata)
            
        except Exception as e:
            logger.error(f"שגיאה בטעינת הקובץ {file_path}: {e}")
            return None
    
    @staticmethod
    def load_directory(directory_path: str, glob_pattern: str = "**/*.txt", encoding: str = 'utf-8') -> List[SimpleDocument]:
        """
        טעינת כל קבצי הטקסט בתיקייה
        
        Args:
            directory_path: נתיב לתיקייה
            glob_pattern: תבנית לבחירת קבצים
            encoding: קידוד הקבצים
            
        Returns:
            רשימת מסמכים
        """
        try:
            directory = Path(directory_path)
            
            # בדיקה שהתיקייה קיימת
            if not directory.exists() or not directory.is_dir():
                logger.error(f"התיקייה {directory} לא קיימת")
                return []
            
            # מציאת כל הקבצים המתאימים
            documents = []
            for file_path in directory.glob(glob_pattern):
                if file_path.is_file():
                    document = SimpleLoader.load_file(str(file_path), encoding)
                    if document:
                        documents.append(document)
                        logger.info(f"נטען בהצלחה: {file_path.name}")
            
            logger.info(f"נטענו {len(documents)} מסמכים בסך הכל")
            return documents
            
        except Exception as e:
            logger.error(f"שגיאה בטעינת קבצים מהתיקייה {directory_path}: {e}")
            return []
            
class SimpleVectorStore:
    """
    אחסון וקטורי פשוט המבוסס על sentence-transformers
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        אתחול אחסון וקטורי פשוט
        
        Args:
            model_name: שם המודל להטמנות
        """
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = []
    
    def add_documents(self, documents: List[SimpleDocument]) -> None:
        """
        הוספת מסמכים לאחסון הוקטורי
        
        Args:
            documents: רשימת מסמכים להוספה
        """
        if not documents:
            return
            
        # חישוב הטמנות למסמכים
        contents = [doc.content for doc in documents]
        new_embeddings = self.model.encode(contents)
        
        # הוספת המסמכים וההטמנות
        self.documents.extend(documents)
        self.embeddings.extend(new_embeddings)
        
        logger.info(f"נוספו {len(documents)} מסמכים לאחסון הוקטורי")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[SimpleDocument, float]]:
        """
        חיפוש מסמכים דומים לשאילתה
        
        Args:
            query: שאילתה לחיפוש
            k: מספר מסמכים להחזיר
            
        Returns:
            רשימת צמדים (מסמך, ציון דמיון)
        """
        if not self.documents:
            logger.warning("אין מסמכים באחסון הוקטורי")
            return []
            
        # חישוב הטמנה לשאילתה
        query_embedding = self.model.encode(query)
        
        # חישוב דמיון קוסינוס לכל המסמכים
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            # חישוב דמיון קוסינוס
            dot_product = np.dot(query_embedding, doc_embedding)
            norm_query = np.linalg.norm(query_embedding)
            norm_doc = np.linalg.norm(doc_embedding)
            similarity = dot_product / (norm_query * norm_doc)
            
            similarities.append((i, similarity))
        
        # מיון לפי דמיון (מהגבוה לנמוך)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # החזרת המסמכים הדומים ביותר
        results = []
        for i, similarity in similarities[:k]:
            results.append((self.documents[i], similarity))
            
        return results
    
    def save(self, file_path: str) -> bool:
        """
        שמירת האחסון הוקטורי לקובץ
        
        Args:
            file_path: נתיב לקובץ
            
        Returns:
            האם השמירה הצליחה
        """
        try:
            data = {
                "documents": [
                    {
                        "content": doc.content,
                        "metadata": doc.metadata
                    }
                    for doc in self.documents
                ],
                "embeddings": [embedding.tolist() for embedding in self.embeddings]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                
            logger.info(f"האחסון הוקטורי נשמר לקובץ: {file_path}")
            return True
        except Exception as e:
            logger.error(f"שגיאה בשמירת האחסון הוקטורי: {e}")
            return False
    
    def load(self, file_path: str) -> bool:
        """
        טעינת אחסון וקטורי מקובץ
        
        Args:
            file_path: נתיב לקובץ
            
        Returns:
            האם הטעינה הצליחה
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.documents = [
                SimpleDocument(content=doc_data["content"], metadata=doc_data["metadata"])
                for doc_data in data["documents"]
            ]
            
            self.embeddings = [np.array(embedding) for embedding in data["embeddings"]]
            
            logger.info(f"האחסון הוקטורי נטען מהקובץ: {file_path}")
            return True
        except Exception as e:
            logger.error(f"שגיאה בטעינת האחסון הוקטורי: {e}")
            return False

class SimpleRAG:
    """מערכת RAG פשוטה"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        אתחול מערכת RAG
        
        Args:
            api_key: מפתח API של Google Gemini
        """
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("לא נמצא מפתח API של Google Gemini. הגדר את GEMINI_API_KEY במשתני הסביבה או העבר כפרמטר")
            
        # הגדרת Gemini
        genai.configure(api_key=self.api_key)
        
        # יצירת מודלים
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # אחסון וקטורי
        self.vector_store = SimpleVectorStore()
        
        # שמירת האינטראקציה האחרונה
        self.last_query = None
        self.last_docs = None
        self.last_answer = None
    
    def load_documents(self, directory_path: str, glob_pattern: str = "**/*.txt") -> bool:
        """
        טעינת מסמכים מתיקייה
        
        Args:
            directory_path: נתיב לתיקייה
            glob_pattern: תבנית לבחירת קבצים
            
        Returns:
            האם הטעינה הצליחה
        """
        try:
            documents = SimpleLoader.load_directory(directory_path, glob_pattern)
            if not documents:
                logger.error("לא נמצאו מסמכים לטעינה")
                return False
                
            self.vector_store.add_documents(documents)
            return True
        except Exception as e:
            logger.error(f"שגיאה בטעינת מסמכים: {e}")
            return False
    
    def search_documents(self, query: str, k: int = 5) -> List[Tuple[SimpleDocument, float]]:
        """
        חיפוש מסמכים רלוונטיים לשאילתה
        
        Args:
            query: שאילתה לחיפוש
            k: מספר מסמכים להחזיר
            
        Returns:
            רשימת צמדים (מסמך, ציון דמיון)
        """
        return self.vector_store.similarity_search(query, k=k)
    
    def ask(self, query: str, k: int = 3, debug: bool = True) -> str:
        """
        שאילת שאלה למערכת RAG
        
        Args:
            query: שאלה לשאול
            k: מספר מסמכים רלוונטיים לחפש
            debug: האם להציג מידע דיבאג
            
        Returns:
            תשובה מהמערכת
        """
        self.last_query = query
        
        if debug:
            logger.info("\n" + "="*50)
            logger.info(f"שאלה: {query}")
            logger.info("="*50)
        
        try:
            # חיפוש מסמכים רלוונטיים
            docs_with_scores = self.search_documents(query, k=k)
            self.last_docs = docs_with_scores
            
            if not docs_with_scores:
                logger.warning("לא נמצאו מסמכים רלוונטיים")
                return "לא נמצאו מסמכים רלוונטיים לשאלה זו."
                
            # הצגת המסמכים
            if debug:
                logger.info("\nמסמכים רלוונטיים שנמצאו:")
                logger.info("-"*50)
                for i, (doc, score) in enumerate(docs_with_scores, 1):
                    logger.info(f"מסמך {i} (ציון: {score:.4f}):")
                    logger.info(f"מקור: {doc.metadata.get('source', 'לא ידוע')}")
                    content_preview = doc.content[:300] + "..." if len(doc.content) > 300 else doc.content
                    logger.info(f"תוכן: {content_preview}")
                    logger.info("-"*50)
            
            # בניית הפרומפט
            context = "\n\n".join([doc.content for doc, _ in docs_with_scores])
            
            prompt = f"""
            אתה עוזר לסטודנטים במכללת אפקה להנדסה. השב על השאלה בהתבסס על המידע הבא בלבד.
            אם המידע לא מכיל תשובה ברורה, ציין זאת ואל תמציא מידע.
            השתמש בשפה עברית בתשובתך.
            
            מידע:
            {context}
            
            שאלה: {query}
            
            תשובה:
            """
            
            # קבלת תשובה מהמודל
            response = self.model.generate_content(prompt)
            answer = response.text
            self.last_answer = answer
            
            if debug:
                logger.info("\nתשובה:")
                logger.info("-"*50)
                logger.info(answer)
                logger.info("-"*50)
                
            return answer
            
        except Exception as e:
            logger.error(f"שגיאה בשאילת שאלה: {e}")
            return f"אירעה שגיאה: {str(e)}"
    
    def save_vector_store(self, file_path: str) -> bool:
        """
        שמירת האחסון הוקטורי לקובץ
        
        Args:
            file_path: נתיב לקובץ
            
        Returns:
            האם השמירה הצליחה
        """
        return self.vector_store.save(file_path)
    
    def load_vector_store(self, file_path: str) -> bool:
        """
        טעינת אחסון וקטורי מקובץ
        
        Args:
            file_path: נתיב לקובץ
            
        Returns:
            האם הטעינה הצליחה
        """
        return self.vector_store.load(file_path)
    
    def save_last_interaction(self, file_path: str) -> bool:
        """
        שמירת האינטראקציה האחרונה לקובץ
        
        Args:
            file_path: נתיב לקובץ
            
        Returns:
            האם השמירה הצליחה
        """
        if not all([self.last_query, self.last_docs, self.last_answer]):
            logger.error("אין אינטראקציה אחרונה לשמירה")
            return False
            
        try:
            data = {
                "query": self.last_query,
                "documents": [
                    {
                        "content": doc.content,
                        "metadata": doc.metadata,
                        "score": score
                    }
                    for doc, score in self.last_docs
                ],
                "answer": self.last_answer
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"האינטראקציה נשמרה לקובץ: {file_path}")
            return True
        except Exception as e:
            logger.error(f"שגיאה בשמירת האינטראקציה: {e}")
            return False

def main():
    """נקודת כניסה ראשית"""
    import argparse
    
    parser = argparse.ArgumentParser(description="מערכת RAG פשוטה")
    parser.add_argument("--load-docs", help="נתיב לתיקיית מסמכים לטעינה")
    parser.add_argument("--question", "-q", help="שאלה לשאול")
    parser.add_argument("--save-store", help="נתיב לשמירת האחסון הוקטורי")
    parser.add_argument("--load-store", help="נתיב לטעינת אחסון וקטורי")
    parser.add_argument("--save-interaction", "-s", help="נתיב לשמירת האינטראקציה האחרונה")
    
    args = parser.parse_args()
    
    try:
        # יצירת מערכת RAG
        rag = SimpleRAG()
        
        # טעינת אחסון וקטורי אם צוין
        if args.load_store:
            if not rag.load_vector_store(args.load_store):
                logger.error(f"לא ניתן לטעון אחסון וקטורי מ-{args.load_store}")
                return 1
        
        # טעינת מסמכים אם צוין
        if args.load_docs:
            if not rag.load_documents(args.load_docs):
                logger.error(f"לא ניתן לטעון מסמכים מ-{args.load_docs}")
                return 1
                
        # שמירת האחסון הוקטורי אם צוין
        if args.save_store:
            if not rag.save_vector_store(args.save_store):
                logger.error(f"לא ניתן לשמור אחסון וקטורי ל-{args.save_store}")
                return 1
        
        # שאילת שאלה אם צוינה
        if args.question:
            rag.ask(args.question)
            
            # שמירת האינטראקציה האחרונה אם צוינה
            if args.save_interaction:
                if not rag.save_last_interaction(args.save_interaction):
                    logger.error(f"לא ניתן לשמור אינטראקציה ל-{args.save_interaction}")
                    return 1
                    
            return 0
            
        # מצב אינטראקטיבי
        logger.info("\n" + "="*50)
        logger.info("מערכת RAG פשוטה - מצב אינטראקטיבי")
        logger.info("הקלד 'exit' או 'quit' כדי לצאת")
        logger.info("="*50 + "\n")
        
        while True:
            try:
                query = input("\nשאלה: ")
                
                if query.lower() in ['exit', 'quit', 'יציאה']:
                    break
                    
                if not query.strip():
                    continue
                    
                rag.ask(query)
                
            except KeyboardInterrupt:
                print("\nיציאה...")
                break
            except Exception as e:
                logger.error(f"שגיאה: {e}")
        
    except Exception as e:
        logger.error(f"שגיאה כללית: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 