# פרומט 2.2: איחוד Dependency Functions כפולות

## מטרה

הסרת פונקציות dependency כפולות והשארת רק ה-implementation המעודכן.

## שינויים נדרשים:

### 1. עדכון src/backend/main.py

הסר את הפונקציה הכפולה:

```python
# הסר את זה:
def get_chat_service() -> IChatService:
    # implementation...
```

השאר רק import של הפונקציה מ-deps:

```python
from app.api.deps import get_chat_service
```

### 2. בדיקת src/backend/api/routers/documents.py

ודא שהוא משתמש ב-imports הנכונים:

```python
from ...app.api.deps import get_document_service
```

במקום:

```python
from ...services.document_service import get_document_service
```

### 3. בדיקת src/backend/api/routers/chat.py

ודא שהוא משתמש ב-imports הנכונים:

```python
from ...app.api.deps import get_chat_service
```

### 4. הסרת src/backend/api/rag.py אם כפול

בדוק אם יש כפילות עם `src/backend/app/api/routes/rag.py`
אם כן, השאר רק את החדש יותר.

## הסבר:

- יש כפילות של dependency functions במקומות שונים
- הגרסאות ב-`app/api/deps.py` הן העדכניות ומממשות interfaces
- צריך לאחד הכל לשימוש בגרסאות העדכניות

## אחרי השינויים:

- רק פונקציה אחת לכל dependency
- כל ה-imports מובילים לאותו מקום
- אין כפילות קוד
