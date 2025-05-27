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
