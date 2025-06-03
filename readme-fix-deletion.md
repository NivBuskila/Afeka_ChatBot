# תיקון בעיית מחיקת מסמכים

הבעיה: כאשר מוחקים מסמך, רק המסמך נמחק מטבלת `documents`, אבל ה-chunks וה-embeddings המקושרים נשארים בבסיס הנתונים.

## שינויים שבוצעו

1. עדכון ה-trigger של מחיקת מסמכים בסופאבייס כך שימחק גם את ה-chunks וה-embeddings המקושרים
2. עדכון קוד ה-backend כך שימחק את ה-chunks וה-embeddings במקרה שה-trigger לא עובד

## יישום השינויים

### 1. החלת השינויים בסופאבייס

כדי להחיל את השינויים בסופאבייס, יש להריץ את ה-SQL הבא בעורך ה-SQL של סופאבייס:

```sql
-- Fix document deletion trigger to also delete embeddings

-- Drop existing trigger to replace it
DROP TRIGGER IF EXISTS on_document_deletion ON documents;

-- Update the function
CREATE OR REPLACE FUNCTION handle_document_deletion()
RETURNS TRIGGER AS $$
DECLARE
  storage_path TEXT;
BEGIN
  -- Extract the storage path from the URL
  -- The URL is usually in format: https://domain.com/storage/v1/object/public/documents/filename.ext
  storage_path := substring(OLD.url from '/documents/(.*)$');

  IF storage_path IS NULL THEN
    -- Fallback: try to extract just the filename
    storage_path := substring(OLD.url from '[^/]+$');
    IF storage_path IS NOT NULL THEN
      storage_path := 'documents/' || storage_path;
    END IF;
  ELSE
    storage_path := 'documents/' || storage_path;
  END IF;

  -- Log the path we're trying to delete for debugging
  RAISE NOTICE 'Attempting to delete storage object: %', storage_path;

  -- Delete the file from storage
  DELETE FROM storage.objects
  WHERE bucket_id = 'documents'
  AND (name = storage_path OR path = storage_path OR name = OLD.url OR path = OLD.url);

  -- Delete analytics data
  DELETE FROM document_analytics
  WHERE document_id = OLD.id;

  -- Delete embeddings associated with this document
  -- Important: Delete embeddings first before document_chunks to maintain referential integrity
  DELETE FROM embeddings
  WHERE id IN (
    SELECT embedding_id FROM document_chunks
    WHERE document_id = OLD.id
  );

  -- Delete document chunks
  DELETE FROM document_chunks
  WHERE document_id = OLD.id;

  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Recreate the trigger
CREATE TRIGGER on_document_deletion
  BEFORE DELETE ON documents
  FOR EACH ROW
  EXECUTE FUNCTION handle_document_deletion();
```

### 2. ניקוי מידע ישן שכבר קיים במערכת

אם יש לכם מסמכים שכבר נמחקו, אבל יש להם עדיין chunks ו-embeddings בבסיס הנתונים, תוכלו לנקות אותם בעזרת ה-SQL הבא:

```sql
-- מחיקת embeddings שאין להם chunks מקושרים
DELETE FROM embeddings
WHERE id IN (
  SELECT e.id FROM embeddings e
  LEFT JOIN document_chunks dc ON e.id = dc.embedding_id
  WHERE dc.id IS NULL
);

-- מחיקת chunks שאין להם מסמכים מקושרים
DELETE FROM document_chunks
WHERE document_id NOT IN (
  SELECT id FROM documents
);
```

### 3. בדיקת התיקון

כדי לבדוק שהתיקון עובד כראוי:

1. העלו מסמך חדש דרך הממשק
2. ודאו שנוצרו chunks ו-embeddings (בעזרת ה-Dashboard)
3. מחקו את המסמך
4. בדקו שה-chunks וה-embeddings נמחקו גם כן

# פתרון בעיות מחיקה ו-Timeout בפרויקט

מסמך זה מסביר כיצד לטפל בבעיות במחיקת מסמכים ו-timeout בבסיס הנתונים של Supabase.

## בעיית Timeout במחיקת מסמכים

במקרים בהם יש מסמכים עם כמות גדולה מאוד של חלקים (chunks), ניסיון למחוק אותם דרך ה-API הרגיל עלול לגרום לשגיאת timeout. להלן הפתרון:

### 1. מחיקה בשלבים באמצעות סקריפט

השתמש בסקריפט `delete_document.py` שנוצר במיוחד למטרה זו:

```bash
python delete_document.py
```

הסקריפט יבצע את הפעולות הבאות:
- יציג רשימה של כל המסמכים במערכת
- יאפשר לבחור מסמך למחיקה
- ימחק את החלקים (chunks) של המסמך בקבוצות קטנות כדי להימנע מ-timeout
- ינסה למחוק את רשומת המסמך עצמה

### 2. מחיקה ישירה ב-SQL Editor של Supabase

אם עדיין יש בעיות, ניתן להריץ את הפקודות הבאות ישירות ב-SQL Editor של Supabase:

```sql
-- מחיקת כל החלקים (chunks) של המסמך
DELETE FROM document_chunks WHERE document_id = ID_המסמך;

-- מחיקת המסמך עצמו
DELETE FROM documents WHERE id = ID_המסמך;
```

## בעיית Timeout בפונקציית החיפוש ההיברידי

פונקציית החיפוש ההיברידי עלולה לגרום ל-timeout כאשר יש הרבה מאוד וקטורים במערכת. להלן הפתרון:

### 1. שימוש בגרסה המשופרת של פונקציית החיפוש

הקובץ `src/supabase/manual_migration.sql` מכיל גרסה משופרת של פונקציית החיפוש ההיברידי, שכוללת:
- הגבלת מספר התוצאות הראשוניות בחיפוש הסמנטי
- שימוש באינדקסים לשיפור הביצועים
- אופטימיזציות נוספות למניעת timeout

הרץ את ה-SQL הזה ב-SQL Editor של Supabase.

### 2. הוספת אינדקסים

הוספת אינדקסים מתאימים יכולה לשפר משמעותית את הביצועים:

```sql
-- אינדקס לוקטורי אמבדינג
CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_l2_ops);

-- אינדקס לפי מזהה מסמך
CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);

-- אינדקס לחיפוש טקסט
CREATE INDEX idx_document_chunks_chunk_text ON document_chunks USING gin(to_tsvector('english', chunk_text));
```

## מניעת בעיות בעתיד

כדי למנוע בעיות דומות בעתיד, בוצעו השינויים הבאים:

1. **הגדלת גודל החלקים (chunks)**: השינוי הגדיל את גודל החלקים מ-800 ל-2000 תווים
2. **הגבלת מספר הווקטורים למסמך**: הגבלת מספר הווקטורים למסמך הורדה מ-1000 ל-500
3. **אופטימיזציית פונקציית החיפוש**: שיפור פונקציית החיפוש ההיברידי

הגדרות אלו עודכנו בקובץ `src/backend/services/document_processor.py`.
