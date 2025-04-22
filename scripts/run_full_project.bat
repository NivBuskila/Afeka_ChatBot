@echo off
SETLOCAL EnableDelayedExpansion

echo =========================================
echo הפעלת פרויקט Afeka ChatBot
echo =========================================

REM הגדרת משתני סביבה
set GEMINI_API_KEY=AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s
set AI_SERVICE_PORT=5000
set BACKEND_PORT=8000
set FRONTEND_PORT=5173

REM יצירת תיקיית סביבה וירטואלית אם לא קיימת
if not exist venv (
    echo יוצר סביבה וירטואלית...
    python -m venv venv
)

REM הפעלת הסביבה הוירטואלית
echo הפעלת סביבה וירטואלית...
call venv\Scripts\activate.bat

REM התקנת חבילות Python נדרשות
cd src\ai
echo התקנת חבילות Python לשירות ה-AI...
pip install -r requirements.txt

REM בדיקה אם יש צורך להתקין חבילות נוספות
python -c "import google.genai" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo התקנת חבילת google-genai...
    pip install google-genai
)

echo.
echo =========================================
echo הפעלת שירות ה-AI
echo =========================================

REM הפעלת שירות ה-AI ברקע
START "Gemini AI Service" cmd /c "python app.py"
echo שירות ה-AI פועל בכתובת http://localhost:%AI_SERVICE_PORT%

REM המתנה לעליית השירות
echo המתנה להפעלת שירות ה-AI...
timeout /t 5 /nobreak > NUL

REM חזרה לתיקייה הראשית
cd ..\..

REM בדיקת חיבור בסיסית לשירות ה-AI
curl -s http://localhost:%AI_SERVICE_PORT% > NUL
if %ERRORLEVEL% NEQ 0 (
    echo שגיאה: לא ניתן להתחבר לשירות ה-AI
    echo בדוק אם התיקייה src\ai קיימת והאם הקובץ app.py תקין
    goto :END
) else (
    echo שירות ה-AI פעיל!
)

echo.
echo =======================================================
echo עכשיו אפשר לבדוק את שירות הצ'אט!
echo =======================================================
echo.
echo שירות ה-AI פעיל בכתובת: http://localhost:%AI_SERVICE_PORT%
echo.
echo דוגמה לשימוש (באמצעות curl):
echo curl -X POST -H "Content-Type: application/json" -d "{\"message\":\"שלום, מה שלומך?\"}" http://localhost:%AI_SERVICE_PORT%/chat
echo.
echo ניתן לבדוק את השירות גם באמצעות כלים כמו Postman
echo.
echo הערה: אם תרצה להפעיל את כל הפרויקט כולל frontend ו-backend,
echo יש להתקין Node.js ולהפעיל את השירותים הנוספים

echo.
echo האם ברצונך לבדוק את ה-AI באמצעות ממשק טקסטואלי פשוט? (כ/ל)
set /p TEST_AI=

if /I "!TEST_AI!"=="כ" (
    echo הפעלת בדיקת צ'אט טקסטואלית...
    python src\ai\test_gemini.py
)

echo.
echo האם ברצונך לנסות להפעיל גם את ה-frontend? (זה ידרוש התקנת Node.js) (כ/ל)
set /p RUN_FRONTEND=

if /I "!RUN_FRONTEND!"=="כ" (
    echo.
    echo =========================================
    echo הפעלת שירות ה-Frontend
    echo =========================================

    echo בדיקה אם Node.js מותקן...
    node --version >NUL 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo שגיאה: Node.js לא מותקן. אנא התקן Node.js לפני הפעלת ה-frontend.
        echo ניתן להוריד מ: https://nodejs.org/
        goto :END
    )
    
    cd src\frontend
    echo התקנת חבילות Node.js...
    npm install
    
    echo הפעלת שירות ה-frontend...
    START "Frontend Service" cmd /c "npm run dev"
    
    echo שירות ה-frontend יהיה זמין בקרוב בכתובת http://localhost:%FRONTEND_PORT%
    
    REM חזרה לתיקייה הראשית
    cd ..\..
)

echo.
echo =======================================================
echo מידע שימושי:
echo =======================================================
echo - לסיום הפעלת השירותים, סגור את חלונות הפקודה
echo - אם אתה נתקל בבעיות, בדוק את הלוגים בחלונות הפקודה של כל שירות
echo.
echo תודה שהשתמשת במערכת!

:END
ENDLOCAL 