-- פתרון לבעיית RLS של טבלת messages
-- File: src/supabase/sql/fix_messages_rls.sql

-- הסרת מדיניות RLS הקיימת
DROP POLICY IF EXISTS "User can view own messages" ON messages;
DROP POLICY IF EXISTS "User can insert own messages" ON messages;
DROP POLICY IF EXISTS "User can update own messages" ON messages;
DROP POLICY IF EXISTS "User can delete own messages" ON messages;
DROP POLICY IF EXISTS "Enable all operations for authenticated users on messages" ON messages;
DROP POLICY IF EXISTS "Enable all operations for anonymous users on messages" ON messages;

-- יצירת מדיניות רחבה יותר לשלב הפיתוח
CREATE POLICY "Enable all operations for authenticated users on messages"
ON messages
FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);

-- הוספת enable anon כדי לאפשר למשתמשים לא מאומתים להשתמש במערכת בשלב הפיתוח
CREATE POLICY "Enable all operations for anonymous users on messages"
ON messages
FOR ALL
TO anon
USING (true)
WITH CHECK (true); 