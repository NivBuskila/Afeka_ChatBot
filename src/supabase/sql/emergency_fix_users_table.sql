-- קובץ חירום לתיקון בעיות הרשאה בטבלת המשתמשים
-- הרצה: בממשק ה-SQL של Supabase

-- 1. ביטול RLS לחלוטין מטבלת משתמשים (באופן זמני)
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
ALTER TABLE auth.users DISABLE ROW LEVEL SECURITY;

-- 2. מחיקת כל המדיניות הקיימת
DROP POLICY IF EXISTS "Users are viewable by authenticated users" ON public.users;
DROP POLICY IF EXISTS "Users can add their own record" ON public.users;
DROP POLICY IF EXISTS "Users can update their own record" ON public.users;
DROP POLICY IF EXISTS "Users can delete their own record" ON public.users;
DROP POLICY IF EXISTS "Users can view all records" ON public.users;
DROP POLICY IF EXISTS "Users can insert their own record" ON public.users;
DROP POLICY IF EXISTS "Users are insertable by authenticated users" ON public.users;
DROP POLICY IF EXISTS "Users are updatable by authenticated users" ON public.users;
DROP POLICY IF EXISTS "Users are deletable by authenticated users" ON public.users;

-- 3. יצירת טבלת users בגיבוי אם היא לא קיימת
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        CREATE TABLE public.users (
            id UUID PRIMARY KEY REFERENCES auth.users(id),
            email TEXT NOT NULL,
            name TEXT,
            status TEXT DEFAULT 'active',
            last_sign_in TIMESTAMPTZ,
            preferred_language TEXT DEFAULT 'he',
            timezone TEXT DEFAULT 'Asia/Jerusalem',
            subscription_plan TEXT DEFAULT 'free',
            subscription_expiry TIMESTAMPTZ,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
    END IF;
END
$$;

-- 4. וידוא שטבלת המשתמשים מכילה את כל השדות הנדרשים
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS name TEXT,
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active',
ADD COLUMN IF NOT EXISTS last_sign_in TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS preferred_language TEXT DEFAULT 'he',
ADD COLUMN IF NOT EXISTS timezone TEXT DEFAULT 'Asia/Jerusalem',
ADD COLUMN IF NOT EXISTS subscription_plan TEXT DEFAULT 'free',
ADD COLUMN IF NOT EXISTS subscription_expiry TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- 5. הסרת שדה role אם הוא קיים
ALTER TABLE public.users DROP COLUMN IF EXISTS role;

-- 6. הגדרת הרשאות רחבות לטבלאות
GRANT ALL ON public.users TO anon;
GRANT ALL ON public.users TO authenticated;
GRANT ALL ON public.users TO service_role;

-- 7. מתן הרשאות לסכמות
GRANT USAGE ON SCHEMA public TO anon;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO service_role;

-- 8. מתן הרשאות למפתחות חיצוניים
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- 9. פונקציית האזנה על יצירת משתמש חדש
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- ניסיון ליצור את המשתמש בטבלת public.users
    BEGIN
        INSERT INTO public.users (id, email, name, created_at, updated_at)
        VALUES (
            NEW.id,
            NEW.email,
            COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
            NOW(),
            NOW()
        );
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'שגיאה בהוספת משתמש לטבלת public.users: %', SQLERRM;
    END;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 10. ביטול טריגר קיים והגדרת טריגר חדש
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- הודעה על השלמת השינויים
DO $$
BEGIN
    RAISE NOTICE 'תיקון חירום הושלם - כל מערכות ההרשאה הנוקשות בוטלו באופן זמני';
END
$$; 