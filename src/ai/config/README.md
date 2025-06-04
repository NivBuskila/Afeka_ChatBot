# מערכת הגדרות RAG - מכללת אפקה

## סקירה כללית

קובץ `rag_config.py` מכיל את כל הגדרות מערכת RAG במקום מרכזי אחד. זה מחליף את כל ה-magic numbers שהיו פזורים בקוד ומאפשר אופטימיזציה קלה של המערכת.

## מבנה ההגדרות

### 📋 SearchConfig - הגדרות חיפוש

```python
SIMILARITY_THRESHOLD: float = 0.55  # סף דמיון מינימלי
MAX_CHUNKS_RETRIEVED: int = 12      # מספר צ'אנקים מקסימלי לחיפוש
MAX_CHUNKS_FOR_CONTEXT: int = 8     # מספר צ'אנקים לשליחה ל-LLM
HYBRID_SEMANTIC_WEIGHT: float = 0.7 # משקל חיפוש סמנטי
HYBRID_KEYWORD_WEIGHT: float = 0.3  # משקל חיפוש מילות מפתח
```

### 🔧 EmbeddingConfig - הגדרות Embeddings

```python
MODEL_NAME: str = "models/embedding-001"    # מודל ה-embedding
TASK_TYPE_DOCUMENT: str = "retrieval_document"
TASK_TYPE_QUERY: str = "retrieval_query"
EMBEDDING_DIMENSION: int = 768              # ממד ה-embedding
MAX_RETRIES: int = 3                        # ניסיונות חוזרים
```

### ✂️ ChunkConfig - הגדרות חלוקת צ'אנקים

```python
DEFAULT_CHUNK_SIZE: int = 2000              # גודל צ'אנק בתווים
DEFAULT_CHUNK_OVERLAP: int = 200            # חפיפה בין צ'אנקים
MAX_CHUNKS_PER_DOCUMENT: int = 500          # מקסימום צ'אנקים למסמך
MAX_TOKENS_PER_CHUNK: int = 512             # מקסימום טוקנים לצ'אנק
TARGET_TOKENS_PER_CHUNK: int = 350          # יעד טוקנים לצ'אנק
```

### 🎯 ContextConfig - הגדרות בניית הקשר

```python
MAX_CONTEXT_TOKENS: int = 6000              # מקסימום טוקנים להקשר
RESERVED_TOKENS_FOR_QUERY: int = 500        # טוקנים שמורים לשאילתה
RESERVED_TOKENS_FOR_RESPONSE: int = 1500    # טוקנים שמורים לתשובה
CHUNK_SEPARATOR: str = "\n\n---\n\n"        # מפריד בין צ'אנקים
```

### 🤖 LLMConfig - הגדרות מודל השפה

```python
MODEL_NAME: str = "gemini-2.0-flash"        # מודל ה-LLM
TEMPERATURE: float = 0.1                    # טמפרטורה נמוכה לעקביות
MAX_OUTPUT_TOKENS: int = 2048               # אורך תשובה מקסימלי
GENERATION_TIMEOUT_SECONDS: int = 45        # זמן המתנה מקסימלי
```

### 🗄️ DatabaseConfig - הגדרות מסד נתונים

```python
DOCUMENTS_TABLE: str = "documents"
CHUNKS_TABLE: str = "document_chunks"
SEMANTIC_SEARCH_FUNCTION: str = "advanced_semantic_search"
HYBRID_SEARCH_FUNCTION: str = "hybrid_search"
```

### ⚡ PerformanceConfig - הגדרות ביצועים

```python
MAX_SEARCH_TIME_MS: int = 5000              # 5 שניות מקסימום
TARGET_SEARCH_TIME_MS: int = 2000           # יעד של 2 שניות
ENABLE_EMBEDDING_CACHE: bool = True         # הפעלת מטמון
LOG_SEARCH_ANALYTICS: bool = True           # רישום סטטיסטיקות
```

## איך להשתמש

### ייבוא בקוד

```python
from config.rag_config import (
    get_search_config,
    get_embedding_config,
    get_chunk_config,
    get_context_config,
    get_llm_config
)

# שימוש בהגדרות
search_config = get_search_config()
threshold = search_config.SIMILARITY_THRESHOLD
max_chunks = search_config.MAX_CHUNKS_RETRIEVED
```

### בדיקת הגדרות נוכחיות

```python
# רץ את הקובץ לראות את כל ההגדרות
python src/backend/config/rag_config.py
```

### קבלת הגדרות כמילון

```python
from config.rag_config import rag_config

all_settings = rag_config.get_config_dict()
print(json.dumps(all_settings, indent=2, ensure_ascii=False))
```

## אופטימיזציה

### שינוי ספי דמיון

אם המערכת מוצאת יותר מדי או מעט תוצאות:

```python
# ב-rag_config.py
SIMILARITY_THRESHOLD: float = 0.45  # הנמך לעוד תוצאות
SIMILARITY_THRESHOLD: float = 0.65  # הגבה למעט תוצאות איכותיות
```

### שינוי מספר צ'אנקים

לשליטה במספר התוצאות:

```python
MAX_CHUNKS_RETRIEVED: int = 15      # יותר תוצאות
MAX_CHUNKS_FOR_CONTEXT: int = 10    # יותר הקשר ל-LLM
```

### שינוי גודל צ'אנקים

לאיכות טובה יותר של חיתוך:

```python
DEFAULT_CHUNK_SIZE: int = 1500      # צ'אנקים קטנים יותר
DEFAULT_CHUNK_OVERLAP: int = 300    # חפיפה גדולה יותר
```

### שינוי משקלי חיפוש היברידי

לכוונון איזון סמנטי/מילות מפתח:

```python
HYBRID_SEMANTIC_WEIGHT: float = 0.8  # יותר דגש על סמנטיקה
HYBRID_KEYWORD_WEIGHT: float = 0.2   # פחות דגש על מילות מפתח
```

## בדיקות ביצועים

### הרצת בדיקה מהירה

```bash
python RAG_test/debug_rag.py
```

### בדיקה מקיפה

```bash
python RAG_test/test_runner.py
```

### ניטור ביצועים

הגדרות הביצועים מגדירות יעדים וספים:

- `TARGET_SEARCH_TIME_MS`: יעד זמן חיפוש (2 שניות)
- `MAX_SEARCH_TIME_MS`: זמן מקסימלי לפני אזהרה (5 שניות)
- `LOG_SEARCH_ANALYTICS`: האם לרשום סטטיסטיקות חיפוש

## שגיאות נפוצות ופתרונות

### שגיאת תקינות הגדרות

```
⚠️ שגיאות בהגדרות RAG:
  - SIMILARITY_THRESHOLD חייב להיות בין 0.0 ל-1.0
```

**פתרון**: בדוק שכל הספים בטווח התקין

### ביצועים איטיים

אם זמני התגובה גבוהים:

1. הקטן `MAX_CHUNKS_RETRIEVED`
2. הקטן `DEFAULT_CHUNK_SIZE`
3. הפעל `ENABLE_EMBEDDING_CACHE`

### תוצאות חיפוש לא רלוונטיות

1. שנה `SIMILARITY_THRESHOLD`
2. כוון `HYBRID_SEMANTIC_WEIGHT` ו-`HYBRID_KEYWORD_WEIGHT`
3. בדוק `MAX_CHUNKS_FOR_CONTEXT`

## שינויים היסטוריים

### גרסה 1.0 (עכשיו)

- העברת כל ה-magic numbers לconfig מרכזי
- הוספת בדיקות תקינות
- תמיכה בפונקציות עזר
- תיעוד מפורט

### לפני הרפקטור

- ערכים קבועים פזורים בקוד
- קשה לשנות הגדרות
- אין בדיקת תקינות
- קשה לבדוק אופטימיזציות

## התאמות נוספות

### הוספת הגדרה חדשה

1. הוסף לכלאס המתאים (SearchConfig, ChunkConfig וכו')
2. הוסף בדיקת תקינות ב-`validate_config()`
3. עדכן תיעוד
4. עדכן קוד שמשתמש בהגדרה

### יצירת פרופיל הגדרות חדש

```python
# ליצור קובץ rag_config_experimental.py
# עם הגדרות שונות לבדיקות A/B
```

## תמיכה

לשאלות או בעיות:

1. בדוק את הלוגים של המערכת
2. רץ `python rag_config.py` לבדיקת תקינות
3. השווה עם הגדרות ברירת מחדל

---

**זכור**: כל שינוי בהגדרות ישפיע על כל המערכת. בדוק היטב לפני הפעלה בפרודקשן!
