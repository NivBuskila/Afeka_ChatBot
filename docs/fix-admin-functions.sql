-- סקריפט לתיקון פונקציות המנהל בעלות בעיית עמודה דו-משמעית

-- תיקון פונקציית is_admin - הוספת שם טבלה מפורש לעמודת user_id
CREATE OR REPLACE FUNCTION is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (SELECT 1 FROM admins a WHERE a.user_id = $1);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- תיקון פונקציית promote_to_admin - הוספת שם טבלה מפורש לעמודת user_id
CREATE OR REPLACE FUNCTION promote_to_admin(user_id UUID, department TEXT DEFAULT NULL)
RETURNS BOOLEAN AS $$
BEGIN
  -- בדיקה אם המשתמש כבר מנהל
  IF EXISTS (SELECT 1 FROM admins a WHERE a.user_id = $1) THEN
    -- אם כן, נעדכן רק את המחלקה אם צוינה
    IF $2 IS NOT NULL THEN
      UPDATE admins SET department = $2 WHERE admins.user_id = $1;
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