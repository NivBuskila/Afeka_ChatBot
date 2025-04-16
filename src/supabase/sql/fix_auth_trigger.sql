-- SQL לתיקון הטריגר של Auth שאחראי על יצירת משתמשים חדשים
-- קובץ זה מתקן את הבעיה בטבלת 'users' שלא מתעדכנת כראוי בעת רישום משתמש חדש

-- ראשית, יש לבטל את הטריגר הקיים אם הוא קיים
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- מחיקת פונקציית הטריגר הקיימת אם היא קיימת
DROP FUNCTION IF EXISTS public.handle_new_user();

-- יצירת פונקציית טריגר חדשה שמתאימה את עצמה לסכמה החדשה של טבלת המשתמשים
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- בדיקה אם המשתמש כבר קיים בטבלה (למנוע הוספה כפולה)
    IF EXISTS (SELECT 1 FROM public.users WHERE id = NEW.id) THEN
        RAISE NOTICE 'משתמש כבר קיים בטבלת משתמשים: %', NEW.email;
        RETURN NEW;
    END IF;

    -- הוספת המשתמש לטבלת users עם כל השדות הנדרשים
    INSERT INTO public.users (
        id,
        email,
        name,
        status,
        last_sign_in,
        preferred_language,
        timezone,
        created_at,
        updated_at
    )
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
        'active',
        NOW(),
        COALESCE(NEW.raw_user_meta_data->>'preferred_language', 'he'),
        COALESCE(NEW.raw_user_meta_data->>'timezone', 'Asia/Jerusalem'),
        NOW(),
        NOW()
    );
    
    -- בדיקה אם צריך להוסיף את המשתמש גם לטבלת מנהלים
    IF (NEW.raw_user_meta_data->>'is_admin' = 'true') OR 
       (NEW.raw_user_meta_data->>'role' = 'admin') OR
       (NEW.email LIKE '%admin%') THEN
        
        INSERT INTO public.admins (user_id)
        VALUES (NEW.id)
        ON CONFLICT (user_id) DO NOTHING;
        
        RAISE NOTICE 'משתמש % נוסף כמנהל', NEW.email;
    END IF;

    RAISE NOTICE 'נוצר משתמש חדש בהצלחה: %', NEW.email;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- יצירת הטריגר מחדש
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- יצירת פונקציה נוספת לטיפול במקרה שמשתמש מתחבר אבל לא קיים בטבלת users
CREATE OR REPLACE FUNCTION public.handle_user_login()
RETURNS TRIGGER AS $$
BEGIN
    -- בדיקה אם המשתמש קיים בטבלת users
    IF NOT EXISTS (SELECT 1 FROM public.users WHERE id = NEW.id) THEN
        -- אם המשתמש לא קיים, יוצרים אותו
        INSERT INTO public.users (
            id,
            email,
            name,
            status,
            last_sign_in,
            preferred_language,
            timezone,
            created_at,
            updated_at
        )
        VALUES (
            NEW.id,
            NEW.email,
            COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
            'active',
            NOW(),
            COALESCE(NEW.raw_user_meta_data->>'preferred_language', 'he'),
            COALESCE(NEW.raw_user_meta_data->>'timezone', 'Asia/Jerusalem'),
            NOW(),
            NOW()
        );
        
        RAISE NOTICE 'משתמש נוצר בעת התחברות ראשונה: %', NEW.email;
        
        -- בדיקה אם צריך להוסיף את המשתמש גם לטבלת מנהלים
        IF (NEW.raw_user_meta_data->>'is_admin' = 'true') OR 
           (NEW.raw_user_meta_data->>'role' = 'admin') OR
           (NEW.email LIKE '%admin%') THEN
            
            INSERT INTO public.admins (user_id)
            VALUES (NEW.id)
            ON CONFLICT (user_id) DO NOTHING;
            
            RAISE NOTICE 'משתמש % נוסף כמנהל בעת התחברות ראשונה', NEW.email;
        END IF;
    ELSE
        -- עדכון זמן התחברות אחרון
        UPDATE public.users
        SET last_sign_in = NOW(), updated_at = NOW()
        WHERE id = NEW.id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- יצירת טריגר למקרה של התחברות
DROP TRIGGER IF EXISTS on_auth_user_login ON auth.sessions;
CREATE TRIGGER on_auth_user_login
AFTER INSERT ON auth.sessions
FOR EACH ROW EXECUTE FUNCTION public.handle_user_login();

-- הוספת הרשאות נדרשות
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL ROUTINES IN SCHEMA public TO postgres, anon, authenticated, service_role;

-- וידוא שטבלת המשתמשים מכילה את כל השדות הנדרשים
DO $$
BEGIN
    -- הוספת שדות חסרים לטבלת users אם הם לא קיימים
    ALTER TABLE public.users
    ADD COLUMN IF NOT EXISTS name TEXT,
    ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active',
    ADD COLUMN IF NOT EXISTS last_sign_in TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS preferred_language TEXT DEFAULT 'he',
    ADD COLUMN IF NOT EXISTS timezone TEXT DEFAULT 'Asia/Jerusalem';
    
    -- הסרת שדה role אם הוא קיים (שדה ישן שגורם לבעיות)
    BEGIN
        ALTER TABLE public.users DROP COLUMN IF EXISTS role;
        RAISE NOTICE 'שדה role הוסר אם היה קיים';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'לא היה צורך להסיר שדה role';
    END;
END $$;

-- הודעה על השלמת התיקון
DO $$
BEGIN
    RAISE NOTICE 'תיקון טריגרי Auth הושלם בהצלחה!';
END $$; 