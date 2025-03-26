-- קודם כל מוחקים את המדיניות הקיימת
DROP POLICY IF EXISTS "Users are insertable by authenticated users" ON users;
DROP POLICY IF EXISTS "Users are updatable by authenticated users" ON users;
DROP POLICY IF EXISTS "Users are deletable by authenticated users" ON users;
DROP POLICY IF EXISTS "Users can add their own record" ON users;
DROP POLICY IF EXISTS "Users can update their own record" ON users;
DROP POLICY IF EXISTS "Users can delete their own record" ON users;
DROP POLICY IF EXISTS "Admins can manage all users" ON users;

-- פוליסה פשוטה להרשמה - כל משתמש מאומת יכול להכניס רשומה עם המזהה שלו
CREATE POLICY "Users can insert their own record"
  ON users FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

-- פוליסה פשוטה לקריאה - כל משתמש מאומת יכול לראות את כל הרשומות
CREATE POLICY "Users can view all records"
  ON users FOR SELECT
  TO authenticated
  USING (true);

-- פוליסה פשוטה לעדכון - כל משתמש מאומת יכול לעדכן רק את הרשומה שלו
CREATE POLICY "Users can update their own record"
  ON users FOR UPDATE
  TO authenticated
  USING (auth.uid() = id);

-- פוליסה פשוטה למחיקה - כל משתמש מאומת יכול למחוק רק את הרשומה שלו
CREATE POLICY "Users can delete their own record"
  ON users FOR DELETE
  TO authenticated
  USING (auth.uid() = id);

-- בדיקה אם הטריגר לעדכון העמודה updated_at קיים
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger
    WHERE tgname = 'update_users_updated_at'
  ) THEN
    CREATE TRIGGER update_users_updated_at
      BEFORE UPDATE ON users
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  END IF;
END $$; 