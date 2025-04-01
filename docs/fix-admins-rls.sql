-- Fix script for RLS and duplicate issues

-- תיקון פוליסת ה-RLS בטבלת המנהלים
ALTER TABLE admins ENABLE ROW LEVEL SECURITY;

-- מחיקת הפוליסה הקיימת שגורמת לרקורסיה אינסופית
DROP POLICY IF EXISTS admins_manage_admins ON admins;

-- פוליסה חדשה: מאפשרת למשתמש לראות את רשומת המנהל שלו בלבד
DROP POLICY IF EXISTS admins_self_access ON admins;
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

-- וידוא שהפונקציה is_admin קיימת ונכונה
CREATE OR REPLACE FUNCTION is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (SELECT 1 FROM admins WHERE user_id = $1);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- שיפור פונקציית promote_to_admin לטיפול במצבי כפילות
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

-- ניקוי רשומות כפולות אם קיימות (מתבצע רק אם יש צורך)
-- אפשר להחליף את ה-VALUES עם ה-user_id האמיתי שגורם לשגיאה
/*
DELETE FROM admins 
WHERE id NOT IN (
  SELECT MIN(id) 
  FROM admins 
  GROUP BY user_id
);
*/ 