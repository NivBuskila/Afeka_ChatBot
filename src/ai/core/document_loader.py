"""
מודול פשוט לטעינת מסמכים מקבצי טקסט.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import requests
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class SimpleTextLoader:
    """
    טוען טקסט מקבצים בפורמט טקסט פשוט.
    """
    
    @staticmethod
    def load_file(file_path: str, encoding: str = 'utf-8') -> Optional[Document]:
        """
        טעינת קובץ טקסט ויצירת מסמך
        
        Args:
            file_path: נתיב לקובץ
            encoding: קידוד הקובץ
            
        Returns:
            Document או None אם הייתה שגיאה
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
            
            return Document(page_content=content, metadata=metadata)
            
        except Exception as e:
            logger.error(f"שגיאה בטעינת הקובץ {file_path}: {e}")
            return None
    
    @staticmethod
    def load_directory(directory_path: str, glob_pattern: str = "**/*.txt", encoding: str = 'utf-8') -> List[Document]:
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
                    document = SimpleTextLoader.load_file(str(file_path), encoding)
                    if document:
                        documents.append(document)
                        logger.info(f"נטען בהצלחה: {file_path.name}")
            
            return documents
            
        except Exception as e:
            logger.error(f"שגיאה בטעינת קבצים מהתיקייה {directory_path}: {e}")
            return []

# פונקציות ברמת המודול המשמשות את DocumentManager

def load_document(file_path: str, encoding: str = 'utf-8') -> List[Document]:
    """
    טעינת מסמך מקובץ והחזרת רשימה של מסמכים
    
    Args:
        file_path: נתיב לקובץ
        encoding: קידוד הקובץ
        
    Returns:
        רשימת מסמכים (מסמך אחד או ריקה אם נכשל)
    """
    document = SimpleTextLoader.load_file(file_path, encoding)
    return [document] if document else []

def load_from_url(url: str) -> List[Document]:
    """
    טעינת מסמך מ-URL
    
    Args:
        url: כתובת ה-URL
        
    Returns:
        רשימת מסמכים (מסמך אחד או ריקה אם נכשל)
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        content = response.text
        
        # יצירת מסמך
        metadata = {
            "source": url,
            "file_type": "url",
        }
        
        document = Document(page_content=content, metadata=metadata)
        return [document]
        
    except Exception as e:
        logger.error(f"שגיאה בטעינת מסמך מה-URL {url}: {e}")
        return []

def load_from_directory(directory_path: str, glob_pattern: str = "**/*.txt") -> List[Document]:
    """
    טעינת מסמכים מתיקייה
    
    Args:
        directory_path: נתיב לתיקייה
        glob_pattern: תבנית לבחירת קבצים
        
    Returns:
        רשימת מסמכים
    """
    return SimpleTextLoader.load_directory(directory_path, glob_pattern)

def load_from_database(
    supabase_url: str,
    supabase_key: str,
    table_name: str = "documents",
    query_filter: Optional[Dict[str, Any]] = None,
    content_field: str = "content"
) -> List[Document]:
    """
    טעינת מסמכים ממסד נתונים של Supabase
    
    Args:
        supabase_url: כתובת ה-URL של שרת ה-Supabase
        supabase_key: מפתח ה-API של Supabase
        table_name: שם הטבלה המכילה את המסמכים
        query_filter: פילטר לשאילתה (מילון)
        content_field: שם השדה המכיל את תוכן המסמך
        
    Returns:
        רשימת מסמכים
    """
    try:
        # כאן תהיה אינטגרציה עם Supabase בהמשך
        # כרגע מחזיר רשימה ריקה
        logger.warning("פונקציית load_from_database עדיין לא מיושמת במלואה")
        return []
        
    except Exception as e:
        logger.error(f"שגיאה בטעינת מסמכים ממסד הנתונים: {e}")
        return [] 