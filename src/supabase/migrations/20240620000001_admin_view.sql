-- יצירת VIEW עבור מנהלים
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

-- פונקציה לבדיקה האם משתמש הוא מנהל
CREATE OR REPLACE FUNCTION is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (SELECT 1 FROM admins WHERE user_id = $1);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- פונקציה להפיכת משתמש למנהל
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

-- הגדרת פוליסות אבטחה לטבלת admins
ALTER TABLE admins ENABLE ROW LEVEL SECURITY;

-- פוליסה: מאפשרת למשתמש לראות את רשומת המנהל שלו בלבד
CREATE POLICY "Admins can view their own record"
  ON admins FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

-- פוליסה: מאפשרת למנהלים לנהל מנהלים אחרים
CREATE POLICY "Admins can manage other admins"
  ON admins FOR ALL
  TO authenticated
  USING (
    is_admin(auth.uid())
  );

-- פונקציה להסרת מנהל
CREATE OR REPLACE FUNCTION demote_admin(target_user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  -- בדיקה אם המשתמש המבצע את הפעולה הוא מנהל
  IF NOT is_admin(auth.uid()) THEN
    RAISE EXCEPTION 'Only admins can demote other admins';
  END IF;

  -- מחיקת המנהל
  DELETE FROM admins WHERE user_id = target_user_id;
  RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 