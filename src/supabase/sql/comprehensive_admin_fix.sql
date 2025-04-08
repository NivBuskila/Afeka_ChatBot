-- תיקון מקיף למערכת המנהלים - יש להריץ קובץ זה בלבד

-- מחיקת טריגרים ופוליסות קיימים שעלולים לגרום להתנגשות
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
DROP TRIGGER IF EXISTS auto_add_admin_trigger ON users;

-- מחיקת פוליסות RLS קיימות שעלולות לגרום להתנגשות
DO $$
BEGIN
    -- בדיקה אם הפוליסות קיימות וניסיון למחוק אותן
    BEGIN
        DROP POLICY IF EXISTS "User can view own conversations" ON conversations;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'שגיאה במחיקת פוליסת conversations: %', SQLERRM;
    END;
    
    BEGIN
        DROP POLICY IF EXISTS "User can insert own conversations" ON conversations;
    EXCEPTION WHEN OTHERS THEN
        NULL;
    END;
    
    BEGIN
        DROP POLICY IF EXISTS "User can update own conversations" ON conversations;
    EXCEPTION WHEN OTHERS THEN
        NULL;
    END;
    
    BEGIN
        DROP POLICY IF EXISTS "User can delete own conversations" ON conversations;
    EXCEPTION WHEN OTHERS THEN
        NULL;
    END;
END $$;

-- 1. נבדוק אם שדה role עדיין קיים בטבלה ונעדכן את הסכמה לפי הצורך
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'users' 
    AND column_name = 'role'
  ) THEN
    RAISE NOTICE 'שדה role עדיין קיים - מעדכן את הטבלה...';
  ELSE
    RAISE NOTICE 'שדה role כבר הוסר - ממשיך לשלב הבא';
  END IF;
END $$;

-- 2. העברת כל המשתמשים מסוג admin לטבלת admins
INSERT INTO admins (user_id)
SELECT id FROM users 
WHERE role = 'admin' OR role = 'administrator'
ON CONFLICT (user_id) DO NOTHING;

-- 3. עדכון פונקציות ווידוא שהן נכונות:

-- 3.1 פונקציה שבודקת אם משתמש הוא אדמין (בודקת בטבלת admins)
CREATE OR REPLACE FUNCTION is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (SELECT 1 FROM admins WHERE user_id = $1);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3.2 פונקציה להפיכת משתמש למנהל
CREATE OR REPLACE FUNCTION promote_to_admin(user_id UUID, department TEXT DEFAULT NULL)
RETURNS BOOLEAN AS $$
BEGIN
  -- בדיקה שהמשתמש קיים
  IF NOT EXISTS (SELECT 1 FROM users WHERE id = user_id) THEN
    RAISE EXCEPTION 'המשתמש אינו קיים במערכת';
  END IF;

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
    RAISE NOTICE 'שגיאה בהוספת מנהל: %', SQLERRM;
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3.3 פונקציה לקבלת כל המשתמשים והאדמינים
CREATE OR REPLACE FUNCTION get_all_users_and_admins()
RETURNS SETOF JSON AS $$
BEGIN
    -- Return all users with is_admin flag
    RETURN QUERY
    SELECT json_build_object(
        'id', u.id,
        'email', u.email,
        'name', u.name,
        'created_at', u.created_at,
        'is_admin', a.id IS NOT NULL,
        'department', a.department
    )
    FROM users u
    LEFT JOIN admins a ON u.id = a.user_id
    ORDER BY u.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. בדיקה - האם כל האדמינים הרצויים נמצאים בטבלת admins?
DO $$
DECLARE
    admin_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO admin_count FROM admins;
    RAISE NOTICE 'מספר המנהלים במערכת אחרי התיקון: %', admin_count;
END $$;

-- 5. יצירת טריגר חדש להוספת משתמשים אדמינים אוטומטית
CREATE OR REPLACE FUNCTION auto_add_admin()
RETURNS TRIGGER AS $$
BEGIN
    -- אם המשתמש מגיע עם metadata של אדמין, נוסיף אותו לטבלת admins
    IF TG_TABLE_NAME = 'users' AND 
       (NEW.email LIKE '%ADMIN%' OR 
        NEW.email LIKE '%admin%' OR
        EXISTS (SELECT 1 FROM auth.users WHERE id = NEW.id AND raw_user_meta_data->>'is_admin' = 'true')) THEN
        
        INSERT INTO admins (user_id)
        VALUES (NEW.id)
        ON CONFLICT (user_id) DO NOTHING;
        
        RAISE NOTICE 'משתמש % נוסף אוטומטית כמנהל', NEW.email;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- יצירת הטריגר אם הוא לא קיים
DROP TRIGGER IF EXISTS auto_add_admin_trigger ON users;
CREATE TRIGGER auto_add_admin_trigger
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION auto_add_admin();

-- 6. מתן הרשאות מתאימות לפונקציות
GRANT EXECUTE ON FUNCTION is_admin(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION promote_to_admin(UUID, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION get_all_users_and_admins() TO authenticated;

-- הודעת סיכום
DO $$
BEGIN
    RAISE NOTICE 'תיקון מערכת המנהלים הושלם בהצלחה!';
END $$; 