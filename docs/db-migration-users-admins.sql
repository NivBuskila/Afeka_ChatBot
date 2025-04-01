-- SQL Migration script for separating users and admins
-- Run this in the Supabase SQL Editor

-- 1. Back up the existing users table
CREATE TABLE IF NOT EXISTS users_backup AS SELECT * FROM users;

-- 2. Update the users table schema (remove role column)
ALTER TABLE users 
  ADD COLUMN IF NOT EXISTS name TEXT,
  ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active',
  ADD COLUMN IF NOT EXISTS last_sign_in TIMESTAMPTZ;

-- 3. Create the admins table
CREATE TABLE IF NOT EXISTS admins (
  id SERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  permissions TEXT[] DEFAULT ARRAY['read', 'write'],
  department TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_user_id UNIQUE (user_id)
);

-- 4. Create a view to get admin users with their user info
CREATE OR REPLACE VIEW admin_users AS
  SELECT 
    u.id,
    u.email,
    u.name,
    u.created_at,
    u.updated_at,
    u.last_sign_in,
    u.status,
    a.id as admin_id,
    a.permissions,
    a.department
  FROM users u
  JOIN admins a ON u.id = a.user_id;

-- 5. Migrate existing admin users to the new structure
INSERT INTO admins (user_id)
SELECT id FROM users_backup WHERE role = 'admin' OR role = 'administrator'
ON CONFLICT (user_id) DO NOTHING;

-- 6. Create triggers to auto-update the updated_at field
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_timestamp_admins
BEFORE UPDATE ON admins
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- 7. Setup RLS (Row Level Security) policies
-- Ensure users can only access their own data
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_self_access ON users
  FOR ALL
  USING (auth.uid() = id);

-- Allow admins to see all users
CREATE POLICY admins_see_all_users ON users
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM admins WHERE user_id = auth.uid()
    )
  );

-- Only allow admins to manage admins
ALTER TABLE admins ENABLE ROW LEVEL SECURITY;

-- שינוי הפוליסה למניעת רקורסיה אינסופית
DROP POLICY IF EXISTS admins_manage_admins ON admins;

-- פוליסה חדשה: מאפשרת למשתמש לראות את רשומת המנהל שלו בלבד
CREATE POLICY admins_self_access ON admins
  FOR SELECT
  USING (user_id = auth.uid());
  
-- פוליסה נוספת: מאפשרת למנהלים לראות ולנהל את כל המנהלים
-- השינוי פה: אנחנו משתמשים בפונקציה is_admin במקום קריאה ישירה לטבלה שגורמת לרקורסיה
CREATE POLICY admins_manage_admins ON admins
  FOR ALL
  USING (
    is_admin(auth.uid())
  );

-- 8. Create helper functions for user management
CREATE OR REPLACE FUNCTION is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (SELECT 1 FROM admins WHERE user_id = $1);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION promote_to_admin(user_id UUID, department TEXT DEFAULT NULL)
RETURNS BOOLEAN AS $$
BEGIN
  -- בדיקה אם המשתמש כבר מנהל
  IF EXISTS (SELECT 1 FROM admins WHERE user_id = $1) THEN
    -- אם כן, נעדכן רק את המחלקה אם צוינה
    IF $2 IS NOT NULL THEN
      UPDATE admins SET department = $2 WHERE user_id = $1;
    END IF;
    RETURN TRUE;
  END IF;

  -- אם המשתמש אינו מנהל, נוסיף אותו
  INSERT INTO admins (user_id, department)
  VALUES ($1, $2);
  RETURN TRUE;
EXCEPTION
  WHEN unique_violation THEN
    -- אם קיימת הפרת unique במהלך הוספה, נתעלם מהשגיאה
    RETURN TRUE;
  WHEN OTHERS THEN 
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 