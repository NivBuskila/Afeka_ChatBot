-- סקריפט לניקוי מסד הנתונים ממשתמשים ומנהלים

-- ניתוק האילוצים באופן זמני כדי למנוע שגיאות של FOREIGN KEY
ALTER TABLE admins DISABLE TRIGGER ALL;
ALTER TABLE users DISABLE TRIGGER ALL;

-- מחיקת כל המנהלים מטבלת admins
TRUNCATE admins CASCADE;

-- מחיקת כל המשתמשים מטבלת users
TRUNCATE users CASCADE;

-- ניקוי טבלת auth.users של סופאבייס (דורש הרשאות מיוחדות)
-- אם הפקודה נכשלת, נסה להריץ את הסקריפט דרך חשבון סופאבייס בעל הרשאות גבוהות
DELETE FROM auth.users;

-- חיבור מחדש של האילוצים
ALTER TABLE admins ENABLE TRIGGER ALL;
ALTER TABLE users ENABLE TRIGGER ALL;

-- אם יש טבלאות נוספות שמקושרות למשתמשים, יש לנקות גם אותן
-- לדוגמה, אם יש טבלאות נתונים נוספות:
-- TRUNCATE user_profiles CASCADE;
-- TRUNCATE user_settings CASCADE;

-- אם יש אינדקסים שצריך לבנות מחדש:
-- REINDEX TABLE users;
-- REINDEX TABLE admins;

-- לא לשכוח שאחרי ניקוי המסד, יהיה צורך לייצר מחדש משתמשים ומנהלים
-- אפשר לעשות זאת דרך הרישום באפליקציה או על ידי הכנסה ידנית של רשומות 