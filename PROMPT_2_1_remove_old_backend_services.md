# פרומט 2.1: הסרת Backend Services הישנים

## מטרה

הסרת קבצי services ישנים כפולים שהוחלפו בגרסאות חדשות.

## קבצים למחיקה:

### 1. הסר את הקבצים הבאים:

```
src/backend/services/chat_service.py
src/backend/services/document_service.py
```

### 2. הסר את התיקייה:

```
src/backend/services/
```

(רק אם היא ריקה אחרי מחיקת הקבצים)

## הסבר:

- הקבצים האלה הם גרסאות ישנות של services
- הגרסאות החדשות נמצאות ב-`src/backend/app/services/`
- הגרסאות החדשות מממשות interfaces ומעוצבות טוב יותר
- אין תלות בקבצים הישנים האלה

## לפני המחיקה - ודא:

1. ש-`src/backend/app/services/chat_service.py` קיים ופועל
2. ש-`src/backend/app/services/document_service.py` קיים ופועל
3. שאין imports לקבצים הישנים בקוד

## אחרי המחיקה:

- הפרויקט יהיה נקי מכפלי קוד
- יישאר רק implementation אחד לכל service
