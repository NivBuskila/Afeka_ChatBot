@echo off
echo בדיקת חיבור ל-Gemini API
echo ========================

REM הפעלת הסביבה הוירטואלית אם קיימת
if exist venv\Scripts\activate.bat (
    echo הפעלת סביבה וירטואלית...
    call venv\Scripts\activate.bat
) else (
    echo לא נמצאה סביבה וירטואלית, ממשיך ללא הפעלתה
)

REM הגדרת מפתח API אם לא הוגדר קודם
if "%GEMINI_API_KEY%"=="" (
    echo הגדרת מפתח Gemini API...
    set GEMINI_API_KEY=AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s
)

REM בדיקה אם google-genai מותקן ואם לא, התקנתו
python -c "import google.genai" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo התקנת חבילת google-genai...
    pip install google-genai
)

REM הפעלת סקריפט הבדיקה
echo הפעלת בדיקת Gemini API...
python src/ai/test_gemini.py

echo.
echo סיום הבדיקה
pause 