#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
קובץ הגדרות מערכת RAG - מכללת אפקה
========================================

קובץ זה מכיל את כל הגדרות מערכת RAG במקום מרכזי אחד.
שינוי ערכים כאן ישפיע על כל המערכת באופן אחיד.

לצורך אופטימיזציה, ערוך את הערכים כאן ורץ בדיקות ביצועים.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class SearchConfig:
    """הגדרות חיפוש במערכת RAG"""
    
    # ספי דמיון לחיפוש
    SIMILARITY_THRESHOLD: float = 0.3  # סף דמיון מינימלי לכל הצ'אנקים (lowered for better results)
    HIGH_QUALITY_THRESHOLD: float = 0.75  # סף לתוצאות איכותיות גבוהות
    LOW_QUALITY_THRESHOLD: float = 0.40  # סף מינימלי לתוצאות חלשות
    
    # מספר תוצאות מקסימלי
    MAX_CHUNKS_RETRIEVED: int = 12  # מספר צ'אנקים מקסימלי לכל חיפוש
    MAX_CHUNKS_FOR_CONTEXT: int = 8  # מספר צ'אנקים בפועל לשליחה ל-LLM
    MAX_RESULTS_EXTENDED: int = 20  # חיפוש מורחב לצרכים מיוחדים
    
    # משקלים לחיפוש היברידי
    HYBRID_SEMANTIC_WEIGHT: float = 0.7  # משקל החיפוש הסמנטי
    HYBRID_KEYWORD_WEIGHT: float = 0.3  # משקל חיפוש מילות המפתח
    
    # הגדרות זמן תגובה
    SEARCH_TIMEOUT_SECONDS: int = 30  # זמן המתנה מקסימלי לחיפוש
    EMBEDDING_TIMEOUT_SECONDS: int = 15  # זמן המתנה ליצירת embedding


@dataclass
class EmbeddingConfig:
    """הגדרות יצירת embeddings"""
    
    # מודל ה-embedding
    MODEL_NAME: str = "models/embedding-001"  # מודל Gemini לembedding
    TASK_TYPE_DOCUMENT: str = "retrieval_document"  # סוג משימה למסמכים
    TASK_TYPE_QUERY: str = "retrieval_query"  # סוג משימה לשאילתות
    
    # הגדרות embedding
    EMBEDDING_DIMENSION: int = 768  # ממד ה-embedding (למודל Gemini)
    BATCH_SIZE: int = 10  # מספר טקסטים לעיבוד בבת אחת
    MAX_INPUT_LENGTH: int = 8192  # אורך מקסימלי של טקסט לembedding
    
    # הגדרות retry
    MAX_RETRIES: int = 3  # מספר ניסיונות חוזרים
    RETRY_DELAY_SECONDS: float = 1.0  # זמן המתנה בין ניסיונות


@dataclass
class ChunkConfig:
    """הגדרות עיבוד וחלוקת צ'אנקים"""
    
    # גודל צ'אנקים
    DEFAULT_CHUNK_SIZE: int = 2000  # גודל צ'אנק בתווים
    MIN_CHUNK_SIZE: int = 100  # גודל מינימלי לצ'אנק
    MAX_CHUNK_SIZE: int = 4000  # גודל מקסימלי לצ'אנק
    
    # חפיפה בין צ'אנקים
    DEFAULT_CHUNK_OVERLAP: int = 200  # חפיפה רגילה בתווים
    MIN_CHUNK_OVERLAP: int = 50  # חפיפה מינימלית
    MAX_CHUNK_OVERLAP: int = 500  # חפיפה מקסימלית
    
    # הגדרות עיבוד מסמכים
    MAX_CHUNKS_PER_DOCUMENT: int = 500  # מספר צ'אנקים מקסימלי למסמך
    MIN_CHUNKS_PER_DOCUMENT: int = 1  # מספר צ'אנקים מינימלי
    
    # הגדרות טוקנים
    MAX_TOKENS_PER_CHUNK: int = 512  # טוקנים מקסימלי לצ'אנק
    TARGET_TOKENS_PER_CHUNK: int = 350  # יעד טוקנים לצ'אנק
    MIN_TOKENS_PER_CHUNK: int = 50  # טוקנים מינימלי לצ'אנק


@dataclass
class ContextConfig:
    """הגדרות בניית הקשר ל-LLM"""
    
    # הגדרות טוקנים
    MAX_CONTEXT_TOKENS: int = 6000  # מקסימום טוקנים לכל ההקשר
    RESERVED_TOKENS_FOR_QUERY: int = 500  # טוקנים שמורים לשאילתה
    RESERVED_TOKENS_FOR_RESPONSE: int = 1500  # טוקנים שמורים לתשובה
    
    # חישוב זמין להקשר
    @property
    def AVAILABLE_CONTEXT_TOKENS(self) -> int:
        return (self.MAX_CONTEXT_TOKENS - 
                self.RESERVED_TOKENS_FOR_QUERY - 
                self.RESERVED_TOKENS_FOR_RESPONSE)
    
    # הגדרות בניית הקשר
    INCLUDE_CITATIONS: bool = True  # האם לכלול ציטוטים
    INCLUDE_CHUNK_HEADERS: bool = True  # האם לכלול כותרות צ'אנקים
    INCLUDE_PAGE_NUMBERS: bool = True  # האם לכלול מספרי עמודים
    
    # מפרידים
    CHUNK_SEPARATOR: str = "\n\n---\n\n"  # מפריד בין צ'אנקים
    CITATION_SEPARATOR: str = " | "  # מפריד בציטוטים


@dataclass
class LLMConfig:
    """הגדרות מודל השפה"""
    
    # מודל ה-LLM
    MODEL_NAME: str = "gemini-2.0-flash"
    TEMPERATURE: float = 0.1  # נמוך לתשובות עקביות
    MAX_OUTPUT_TOKENS: int = 2048  # אורך תשובה מקסימלי
    
    # הגדרות בטיחות
    SAFETY_SETTINGS: Dict[str, str] = field(default_factory=lambda: {
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE", 
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
    })
    
    # הגדרות timeout
    GENERATION_TIMEOUT_SECONDS: int = 45  # זמן המתנה ליצירת תשובה


@dataclass
class DatabaseConfig:
    """הגדרות מסד נתונים"""
    
    # שמות טבלאות
    DOCUMENTS_TABLE: str = "documents"
    CHUNKS_TABLE: str = "document_chunks"
    ANALYTICS_TABLE: str = "search_analytics"
    
    # שמות פונקציות RPC
    SEMANTIC_SEARCH_FUNCTION: str = "match_documents_semantic"  # Changed to working function
    HYBRID_SEARCH_FUNCTION: str = "hybrid_search_documents"
    CONTEXTUAL_SEARCH_FUNCTION: str = "contextual_search"
    ANALYTICS_FUNCTION: str = "log_search_analytics"
    LOG_ANALYTICS_FUNCTION: str = "log_search_analytics"  # Added missing field
    
    # הגדרות Connection Pool
    MAX_CONNECTIONS: int = 20
    CONNECTION_TIMEOUT: int = 30


@dataclass
class PerformanceConfig:
    """הגדרות ביצועים"""
    
    # זמני תגובה מקסימליים (במילישניות)
    MAX_SEARCH_TIME_MS: int = 5000  # 5 שניות
    MAX_EMBEDDING_TIME_MS: int = 3000  # 3 שניות
    MAX_GENERATION_TIME_MS: int = 8000  # 8 שניות
    
    # זמני תגובה יעד (במילישניות)
    TARGET_SEARCH_TIME_MS: int = 2000  # 2 שניות
    TARGET_EMBEDDING_TIME_MS: int = 1000  # 1 שנייה
    TARGET_GENERATION_TIME_MS: int = 4000  # 4 שניות
    
    # הגדרות caching
    ENABLE_EMBEDDING_CACHE: bool = True
    EMBEDDING_CACHE_SIZE: int = 1000  # מספר embeddings במטמון
    EMBEDDING_CACHE_TTL_SECONDS: int = 3600  # שעה
    
    # הגדרות לוגים וניתוח
    LOG_SEARCH_ANALYTICS: bool = True  # רישום סטטיסטיקות חיפוש
    LOG_PERFORMANCE_METRICS: bool = True  # רישום מדדי ביצועים


@dataclass
class OptimizationConfig:
    """הגדרות אופטימיזציה"""
    
    # הגדרות לבדיקות A/B
    ENABLE_AB_TESTING: bool = False
    AB_TEST_SPLIT_RATIO: float = 0.5  # 50/50 split
    
    # הגדרות לוגים וניתוח
    ENABLE_DETAILED_LOGGING: bool = True
    LOG_SEARCH_ANALYTICS: bool = True
    LOG_PERFORMANCE_METRICS: bool = True
    
    # הגדרות אופטימיזציה אוטומטית
    AUTO_ADJUST_THRESHOLDS: bool = False  # אופטימיזציה אוטומטית של ספים
    MIN_SEARCH_RESULTS_FOR_ADJUSTMENT: int = 100  # מינימום חיפושים לאופטימיזציה


class RAGConfig:
    """מחלקה ראשית להגדרות RAG"""
    
    def __init__(self):
        self.search = SearchConfig()
        self.embedding = EmbeddingConfig()
        self.chunk = ChunkConfig()
        self.context = ContextConfig()
        self.llm = LLMConfig()
        self.database = DatabaseConfig()
        self.performance = PerformanceConfig()
        self.optimization = OptimizationConfig()
    
    def get_config_dict(self) -> Dict[str, Any]:
        """מחזיר את כל ההגדרות כמילון לשמירה או debug"""
        return {
            "search": self.search.__dict__,
            "embedding": self.embedding.__dict__,
            "chunk": self.chunk.__dict__,
            "context": {
                **self.context.__dict__,
                "available_context_tokens": self.context.AVAILABLE_CONTEXT_TOKENS
            },
            "llm": self.llm.__dict__,
            "database": self.database.__dict__,
            "performance": self.performance.__dict__,
            "optimization": self.optimization.__dict__
        }
    
    def validate_config(self) -> List[str]:
        """בדיקת תקינות ההגדרות"""
        errors = []
        
        # בדיקת ספי דמיון
        if not 0.0 <= self.search.SIMILARITY_THRESHOLD <= 1.0:
            errors.append("SIMILARITY_THRESHOLD חייב להיות בין 0.0 ל-1.0")
        
        # בדיקת גדלי צ'אנק
        if self.chunk.MIN_CHUNK_SIZE >= self.chunk.MAX_CHUNK_SIZE:
            errors.append("MIN_CHUNK_SIZE חייב להיות קטן מ-MAX_CHUNK_SIZE")
        
        # בדיקת טוקנים
        if self.context.AVAILABLE_CONTEXT_TOKENS <= 0:
            errors.append("AVAILABLE_CONTEXT_TOKENS חייב להיות חיובי")
        
        # בדיקת משקלים היברידיים
        total_weight = self.search.HYBRID_SEMANTIC_WEIGHT + self.search.HYBRID_KEYWORD_WEIGHT
        if abs(total_weight - 1.0) > 0.01:
            errors.append("סך משקלי החיפוש ההיברידי חייב להיות 1.0")
        
        return errors


# יצירת instance גלובלי
rag_config = RAGConfig()

# בדיקת תקינות בעת ייבוא
config_errors = rag_config.validate_config()
if config_errors:
    print("⚠️ שגיאות בהגדרות RAG:")
    for error in config_errors:
        print(f"  - {error}")
    print("אנא תקן את ההגדרות בקובץ rag_config.py")


# פונקציות עזר למסמכי API
def get_search_config() -> SearchConfig:
    """מחזיר הגדרות חיפוש"""
    return rag_config.search

def get_embedding_config() -> EmbeddingConfig:
    """מחזיר הגדרות embedding"""
    return rag_config.embedding

def get_chunk_config() -> ChunkConfig:
    """מחזיר הגדרות צ'אנקים"""
    return rag_config.chunk

def get_context_config() -> ContextConfig:
    """מחזיר הגדרות הקשר"""
    return rag_config.context

def get_llm_config() -> LLMConfig:
    """מחזיר הגדרות LLM"""
    return rag_config.llm

def get_database_config() -> DatabaseConfig:
    """מחזיר הגדרות מסד נתונים"""
    return rag_config.database

def get_performance_config() -> PerformanceConfig:
    """מחזיר הגדרות ביצועים"""
    return rag_config.performance

def get_optimization_config() -> OptimizationConfig:
    """מחזיר הגדרות אופטימיזציה"""
    return rag_config.optimization


if __name__ == "__main__":
    # בדיקה מהירה של ההגדרות
    print("🔧 הגדרות מערכת RAG:")
    print("=" * 50)
    
    config_dict = rag_config.get_config_dict()
    for section, settings in config_dict.items():
        print(f"\n📋 {section.upper()}:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    
    print(f"\n✅ ההגדרות תקינות: {len(config_errors) == 0}") 