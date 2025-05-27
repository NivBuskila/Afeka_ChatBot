# מדריך הפעלת מערכת ניהול מסד הנתונים הוקטורי - Gemini

## סקירה כללית

מערכת ניהול מסד נתונים וקטורי עבור RAG המשתמשת ב-Google Gemini embeddings.

## דרישות מוקדמות

### 1. מפתח API של Gemini

- היכנס ל-[Google AI Studio](https://makersuite.google.com/app/apikey)
- צור מפתח API חדש
- העתק את המפתח לקובץ `.env`

### 2. מסד נתונים Supabase

- פרויקט Supabase פעיל עם pgvector extension
- מפתחות API (URL, ANON_KEY, SERVICE_KEY)

## הגדרת הסביבה

### 1. צור קובץ .env

```bash
cp .env-example .env
```

### 2. ערוך את קובץ .env

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# AI Configuration
GEMINI_API_KEY=your-gemini-api-key

# Service URLs
VITE_BACKEND_URL=http://localhost:8000
```

### 3. התקן תלויות

```bash
# Backend
cd src/backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## הפעלת Migrations

### 1. הפעל את ה-migrations בסדר הנכון:

```sql
-- ב-Supabase SQL Editor:

-- Migration 1: הגדרה בסיסית
\i src/supabase/migrations/20250128000001_vector_embeddings.sql

-- Migration 2: עדכון ל-Gemini (אם יש נתונים קיימים)
\i src/supabase/migrations/20250128000002_update_to_gemini.sql
```

### 2. וודא שה-pgvector extension פעיל:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## הפעלת המערכת

### 1. הפעל את ה-Backend

```bash
cd src/backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. הפעל את ה-Frontend

```bash
cd src/frontend
npm run dev
```

### 3. גש לדשבורד

- פתח דפדפן בכתובת: http://localhost:3000
- השתמש ב-token `dev-token` לאימות

## בדיקת המערכת

### הרץ את סקריפט הבדיקה:

```bash
python test_vector_system.py
```

הסקריפט יבדוק:

- ✅ חיבור ל-API
- ✅ העלאת מסמך
- ✅ עיבוד ויצירת embeddings
- ✅ חיפוש סמנטי
- ✅ חיפוש היברידי
- ✅ מחיקת מסמכים

## תכונות המערכת

### 📤 העלאת מסמכים

- תמיכה ב-PDF, TXT, DOCX, DOC
- עיבוד אוטומטי לחלקים (chunks)
- יצירת embeddings עם Gemini
- מעקב סטטוס עיבוד

### 🔍 חיפוש

- **חיפוש סמנטי**: מבוסס על דמיון וקטורי
- **חיפוש היברידי**: משלב חיפוש סמנטי ומילות מפתח
- תוצאות עם ציון דמיון

### 🗑️ ניהול מסמכים

- מחיקת מסמכים כולל embeddings
- סטטיסטיקות מערכת
- מעקב אחר סטטוס עיבוד

### 📊 דשבורד

- ממשק בעברית
- העלאת קבצים עם drag & drop
- טבלת מסמכים עם סטטוס
- כרטיסי סטטיסטיקות

## מפרט טכני

### Embeddings

- **מודל**: Google Gemini `models/embedding-001`
- **ממדים**: 768
- **סוג משימה**: `retrieval_document`

### מסד נתונים

- **טבלאות**: `documents`, `document_chunks`
- **אינדקסים**: IVFFlat עם cosine similarity
- **פונקציות**: חיפוש סמנטי והיברידי

### API Endpoints

```
POST /api/vector/upload-document     # העלאת מסמך
GET  /api/vector/documents          # רשימת מסמכים
GET  /api/vector/document/{id}/status # סטטוס מסמך
DELETE /api/vector/document/{id}     # מחיקת מסמך
POST /api/vector/search             # חיפוש סמנטי
POST /api/vector/search/hybrid      # חיפוש היברידי
GET  /api/vector/stats              # סטטיסטיקות
```

## פתרון בעיות

### שגיאות נפוצות

#### 1. שגיאת אימות Gemini

```
Error: API key not valid
```

**פתרון**: וודא שה-GEMINI_API_KEY נכון בקובץ .env

#### 2. שגיאת חיבור למסד נתונים

```
Error: relation "documents" does not exist
```

**פתרון**: הפעל את ה-migrations

#### 3. שגיאת pgvector

```
Error: extension "vector" is not available
```

**פתרון**: הפעל `CREATE EXTENSION vector;` ב-Supabase

### לוגים

- Backend logs: `src/backend/logs/`
- Document processing: `document_processor.log`

## הרחבות עתידיות

### תכונות מתוכננות

- [ ] תמיכה בפורמטים נוספים (PPT, HTML)
- [ ] חיפוש מתקדם עם פילטרים
- [ ] ניתוח סנטימנט
- [ ] תמיכה בשפות נוספות
- [ ] אופטימיזציה של embeddings

### אופטימיזציות

- [ ] Caching של embeddings
- [ ] עיבוד batch של מסמכים
- [ ] דחיסת וקטורים
- [ ] אינדקסים מתקדמים

## תמיכה

לשאלות ובעיות, פתח issue בפרויקט או צור קשר עם הצוות.
