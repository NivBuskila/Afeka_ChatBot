# מיגרציות Supabase

קובץ זה מכיל הנחיות ליישום המיגרציות בבסיס הנתונים של Supabase.

## סדר המיגרציות

יש לבצע את המיגרציות לפי הסדר הבא:

1. `20240320000000_initial_schema.sql` - סכמה בסיסית ראשונית
2. `20240320000005_security_events.sql` - טבלת אירועי אבטחה
3. `20240320000006_user_management.sql` - ניהול משתמשים
4. `20240320000007_document_management.sql` - ניהול מסמכים
5. `20240320000008_analytics_management.sql` - ניהול אנליטיקה
6. `20240620000000_chat_history.sql` - טבלאות לניהול היסטוריית צ'אט
7. `20240620000001_admin_view.sql` - view ופונקציות ניהול מנהלים

## ביצוע המיגרציות

ניתן ליישם את המיגרציות באחת מהדרכים הבאות:

### 1. דרך ממשק ניהול Supabase:

1. התחבר לפאנל הניהול של Supabase
2. עבור ל-SQL Editor
3. העתק-הדבק את תוכן קובץ המיגרציה
4. לחץ על "Run"

### 2. באמצעות Supabase CLI:

```bash
# התקנת Supabase CLI
npm install -g supabase

# התחברות לפרויקט
supabase login
supabase link --project-ref <PROJECT_REF>

# יישום המיגרציות
supabase db push
```

## שינויים עיקריים

### מבנה היסטוריית צ'אט

המיגרציה `20240620000000_chat_history.sql` מוסיפה:

1. שדות חדשים לטבלת משתמשים
2. טבלה חדשה `conversations` לניהול שיחות
3. טבלה חדשה `messages` לניהול הודעות בכל שיחה
4. אינדקסים ו-Row Level Security (RLS)
5. פונקציות לניהול שיחות והודעות

### View למנהלים

המיגרציה `20240620000001_admin_view.sql` מוסיפה:

1. View חדש בשם `admin_users` שמשלב מידע מטבלת `users` ו-`admins`
2. פונקציות לניהול מנהלים
3. פוליסות אבטחה לטבלת `admins`

## טיפים לשימוש

1. השתמש בפונקציות ב-SQL:

```sql
-- יצירת שיחה חדשה
SELECT create_conversation('USER_UUID');

-- הוספת הודעה
SELECT add_message('CONVERSATION_UUID', 'USER_UUID', 'תוכן ההודעה');

-- עדכון תשובה
SELECT update_response(MESSAGE_ID, 'תוכן התשובה');
```

2. השתמש בפונקציות במקום גישה ישירה לטבלאות, כדי להבטיח שכל הלוגיקה העסקית תתבצע כראוי.
