@echo off
SETLOCAL EnableDelayedExpansion

echo =======================================================
echo מרכז הפעלה - Afeka ChatBot
echo =======================================================
echo.
echo בחר את הסקריפט שברצונך להפעיל:
echo.
echo 1. הפעלת הפרויקט המלא (AI + frontend)
echo 2. הפעלת הפרונטאנד בלבד
echo 3. הפעלת ממשק צ'אט גרפי
echo 4. בדיקת חיבור ל-Gemini API
echo 5. הפעלה באמצעות Docker
echo 0. יציאה
echo.

set /p CHOICE="בחירתך (0-5): "

if "%CHOICE%"=="1" (
    call scripts\run_full_project.bat
) else if "%CHOICE%"=="2" (
    call scripts\run_frontend.bat
) else if "%CHOICE%"=="3" (
    call scripts\run_chat_gui.bat
) else if "%CHOICE%"=="4" (
    call scripts\run_gemini_test.bat
) else if "%CHOICE%"=="5" (
    echo.
    echo בחר את סביבת ה-Docker:
    echo 1. סביבת פיתוח (dev)
    echo 2. סביבת ייצור (production)
    echo.
    set /p DOCKER_ENV="בחירתך (1-2): "
    
    if "!DOCKER_ENV!"=="1" (
        docker-compose -f docker\docker-compose.dev.yml up
    ) else if "!DOCKER_ENV!"=="2" (
        docker-compose -f docker\docker-compose.yml up
    ) else (
        echo בחירה לא תקינה.
    )
) else if "%CHOICE%"=="0" (
    echo יציאה...
) else (
    echo בחירה לא תקינה.
)

ENDLOCAL 