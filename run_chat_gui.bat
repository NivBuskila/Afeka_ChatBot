@echo off
echo =========================================
echo הפעלת ממשק צ'אט Gemini גרפי
echo =========================================

REM הגדרת מפתח API אם לא הוגדר קודם
set GEMINI_API_KEY=AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s

REM הפעלת הסביבה הוירטואלית אם קיימת
if exist venv\Scripts\activate.bat (
    echo הפעלת סביבה וירטואלית...
    call venv\Scripts\activate.bat
) else (
    echo לא נמצאה סביבה וירטואלית, ממשיך ללא הפעלתה
)

REM בדיקה אם google-genai מותקן ואם לא, התקנתו
python -c "import google.genai" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo התקנת חבילת google-genai...
    pip install google-genai
)

REM בדיקה אם tkinter מותקן (בא מובנה עם רוב התקנות של פייתון)
python -c "import tkinter" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo שגיאה: ספריית tkinter לא מותקנת עם פייתון שלך.
    echo אנא התקן גרסת פייתון שכוללת את tkinter.
    echo.
    echo להורדת פייתון: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM הפעלת ממשק הצ'אט הגרפי
echo הפעלת ממשק הצ'אט...
python src\ai\simple_chat.py

echo.
echo ממשק הצ'אט נסגר.
pause 