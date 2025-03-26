-- ביטול מדיניות RLS של האחסון ויצירת מדיניות חדשה

-- ביטול מדיניות ה-RLS הקיימת
DROP POLICY IF EXISTS "Documents are publicly accessible" ON storage.objects;
DROP POLICY IF EXISTS "Documents are uploadable by authenticated users" ON storage.objects;
DROP POLICY IF EXISTS "Documents are deletable by authenticated users" ON storage.objects;

-- יצירת מדיניות פתוחה לגמרי לצורכי פיתוח
CREATE POLICY "Allow public access to document storage"
  ON storage.objects FOR SELECT
  USING (true);

CREATE POLICY "Allow authenticated users to upload to document storage"
  ON storage.objects FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update document storage" 
  ON storage.objects FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow authenticated users to delete from document storage"
  ON storage.objects FOR DELETE
  USING (true);
  
-- וידוא שה-bucket אכן קיים וציבורי
UPDATE storage.buckets
SET public = true
WHERE id = 'documents'; 