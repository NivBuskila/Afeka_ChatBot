-- סקריפט לתיקון בעיית רשומות המנהלים

-- בדיקת קיום המשתמש הספציפי שגורם לבעיה
DO $$
DECLARE
  problem_user_id UUID := 'c1884271-a539-4dc4-934b-faeb8cd315a2';
  user_exists BOOLEAN;
  admin_exists BOOLEAN;
BEGIN
  -- בדיקה אם המשתמש קיים בטבלת users
  SELECT EXISTS(SELECT 1 FROM users WHERE id = problem_user_id) INTO user_exists;
  
  -- בדיקה אם המשתמש כבר קיים בטבלת admins
  SELECT EXISTS(SELECT 1 FROM admins WHERE user_id = problem_user_id) INTO admin_exists;
  
  -- הצגת מידע על המשתמש
  RAISE NOTICE 'User % exists: %', problem_user_id, user_exists;
  RAISE NOTICE 'User is admin: %', admin_exists;
  
  -- אם המשתמש קיים בטבלת משתמשים אך לא בטבלת מנהלים, נוסיף אותו לטבלת המנהלים
  IF user_exists AND NOT admin_exists THEN
    INSERT INTO admins (user_id) VALUES (problem_user_id);
    RAISE NOTICE 'User % added to admins table', problem_user_id;
  END IF;
  
  -- אם המשתמש לא קיים בטבלת משתמשים, נציג הודעה
  IF NOT user_exists THEN
    RAISE NOTICE 'User % does not exist in users table, cannot add to admins', problem_user_id;
  END IF;
  
  -- אם המשתמש כבר קיים בטבלת מנהלים, נציג הודעה
  IF admin_exists THEN
    RAISE NOTICE 'User % already exists in admins table', problem_user_id;
  END IF;
END $$;

-- פתרון אחר: אם יש שגיאות של הפרת unique_user_id, ניתן לנקות כפילויות
-- (אופציונלי - אפשר להריץ רק במקרה הצורך)
DELETE FROM admins a
USING (
  SELECT user_id, MIN(id) as min_id
  FROM admins
  GROUP BY user_id
  HAVING COUNT(*) > 1
) b
WHERE a.user_id = b.user_id AND a.id <> b.min_id;

-- לאחר הניקוי, בדיקה נוספת לוודא שאין כפילויות
DO $$
DECLARE
  duplicate_count INTEGER;
BEGIN
  SELECT COUNT(*) - COUNT(DISTINCT user_id) INTO duplicate_count FROM admins;
  RAISE NOTICE 'Duplicate count in admins table: %', duplicate_count;
  
  IF duplicate_count > 0 THEN
    RAISE NOTICE 'There are still duplicates in the admins table';
  ELSE
    RAISE NOTICE 'No duplicates found in the admins table';
  END IF;
END $$; 