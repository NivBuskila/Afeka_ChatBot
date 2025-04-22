@echo off
SETLOCAL EnableDelayedExpansion

echo ======================================
echo הפעלת ממשק גרפי לצ'אט עם Gemini
echo ======================================

REM הגדרת משתני סביבה
set GEMINI_API_KEY=AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s

REM יצירת סביבה וירטואלית אם לא קיימת
if not exist venv (
    echo יוצר סביבה וירטואלית...
    python -m venv venv
)

REM הפעלת הסביבה הוירטואלית
echo הפעלת סביבה וירטואלית...
call venv\Scripts\activate.bat

REM כניסה לתיקיית ה-AI
cd src\ai

REM התקנת חבילות Python
echo התקנת חבילות Python...
pip install -r requirements.txt

REM בדיקה אם יש צורך להתקין חבילות לממשק גרפי
python -c "import tkinter" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo שגיאה: חבילת tkinter לא מותקנת. 
    echo אנא התקן Python עם תמיכה ב-tkinter.
    goto :END
)

REM בדיקה אם יש צורך להתקין חבילת Gemini
python -c "import google.genai" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo התקנת חבילת google-genai...
    pip install google-genai
)

REM הפעלת מבשק הצ'אט
echo הפעלת ממשק צ'אט גרפי...
python simple_chat.py

:END
cd ..\..
ENDLOCAL 