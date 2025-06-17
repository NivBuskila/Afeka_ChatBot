# פרומט 3.1: ניקוי הערות NOTE/TEMP מיותרות

## מטרה

הסרת הערות NOTE ו-TEMP שלא מוסיפות ערך איכותי לקוד.

## שינויים נדרשים:

### 1. src/backend/middleware/rate_limit.py

הסר:

```python
# Note: Consider making these paths configurable
```

### 2. src/backend/api/routers/chat.py

הסר:

```python
# Note: user_id from chat_data is available if needed: chat_data.user_id
```

### 3. src/backend/api/vector_management.py

החלף:

```python
"url": f"temp://{temp_file_path}",
```

ב:

```python
"url": f"file://{temp_file_path}",
```

והסר:

```python
if document["url"].startswith("temp://"):
```

החלף ב:

```python
if document["url"].startswith("file://"):
```

### 4. src/ai/services/document_processor.py

עדכן את הפונקציה:

```python
async def _update_document_status(self, document_id: int, status: str, note: Optional[str] = None):
```

הסר את הפרמטר `note` אם לא בשימוש, או החלף ב-`description` אם כן.

### 5. בדיקה כללית

חפש ועבור על כל הקבצים הערות שמתחילות ב:

- `# Note:`
- `# TODO:`
- `# FIXME:`
- `# TEMP:`
- `# HACK:`

הסר הערות שלא מוסיפות ערך, כמו:

- "Input validation is assumed to be done elsewhere"
- "Consider making this configurable"
- "This is temporary"

## אחרי השינויים:

- הקוד יכיל רק הערות איכותיות הסבירות לוגיקה עסקית
- אין הערות מערכת מיותרות
- קוד נקי ומקצועי
