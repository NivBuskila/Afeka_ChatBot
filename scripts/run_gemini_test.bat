@echo off
SETLOCAL EnableDelayedExpansion

echo ================================
echo בדיקת חיבור ל-Gemini API
echo ================================

REM הגדרת מפתח API (יש להחליף עם המפתח שלך)
set GEMINI_API_KEY=AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s

REM הפעלת הסביבה הוירטואלית
if exist venv\Scripts\activate.bat (
    echo הפעלת סביבה וירטואלית...
    call venv\Scripts\activate.bat
) else (
    echo יצירת סביבה וירטואלית...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM התקנת חבילות נדרשות
cd src\ai
echo התקנת חבילות Python...
pip install -r requirements.txt

REM בדיקה אם יש צורך להתקין את Gemini
python -c "import google.genai" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo התקנת google-genai...
    pip install google-genai
)

REM הפעלת בדיקה
echo בדיקת חיבור ל-Gemini...
python test_gemini.py

cd ..\..
ENDLOCAL 