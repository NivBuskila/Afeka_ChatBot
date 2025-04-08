-- פתרון לבעיית RLS של טבלת conversations
-- File: src/supabase/sql/fix_conversations_rls.sql

-- הסרת מדיניות RLS הקיימת
DROP POLICY IF EXISTS "User can view own conversations" ON conversations;
DROP POLICY IF EXISTS "User can insert own conversations" ON conversations;
DROP POLICY IF EXISTS "User can update own conversations" ON conversations;
DROP POLICY IF EXISTS "User can delete own conversations" ON conversations;
DROP POLICY IF EXISTS "Enable all operations for authenticated users on conversations" ON conversations;
DROP POLICY IF EXISTS "Enable all operations for anonymous users on conversations" ON conversations;

-- יצירת מדיניות רחבה יותר לשלב הפיתוח
CREATE POLICY "Enable all operations for authenticated users on conversations"
ON conversations
FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);

-- מתן הרשאות לשימוש בפונקציות ב-RPC
GRANT EXECUTE ON FUNCTION create_conversation(UUID, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION add_message(UUID, UUID, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION update_response(BIGINT, TEXT, TEXT, INTEGER, JSONB) TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_conversations(UUID, INTEGER, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION get_conversation_messages(UUID, INTEGER, INTEGER) TO authenticated;

-- הוספת enable anon כדי לאפשר למשתמשים לא מאומתים להשתמש במערכת בשלב הפיתוח
CREATE POLICY "Enable all operations for anonymous users on conversations"
ON conversations
FOR ALL
TO anon
USING (true)
WITH CHECK (true);

-- מתן הרשאות לשימוש בפונקציות ב-RPC לאנונימיים
GRANT EXECUTE ON FUNCTION create_conversation(UUID, TEXT, TEXT) TO anon;
GRANT EXECUTE ON FUNCTION add_message(UUID, UUID, TEXT, TEXT) TO anon;
GRANT EXECUTE ON FUNCTION update_response(BIGINT, TEXT, TEXT, INTEGER, JSONB) TO anon;
GRANT EXECUTE ON FUNCTION get_user_conversations(UUID, INTEGER, INTEGER) TO anon;
GRANT EXECUTE ON FUNCTION get_conversation_messages(UUID, INTEGER, INTEGER) TO anon; 