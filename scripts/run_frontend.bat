@echo off
SETLOCAL EnableDelayedExpansion

echo =======================================
echo Starting User Interface with AI Service Connection
echo =======================================

REM Setting environment variables
set GEMINI_API_KEY=AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s
set AI_SERVICE_PORT=5000
set FRONTEND_PORT=5173

REM Activating virtual environment for AI service
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Installing Python packages for AI service
cd src\ai
echo Installing Python packages for AI service...
pip install -r requirements.txt

REM Checking if google-genai is installed
python -c "import google.genai" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Installing google-genai package...
    pip install google-genai
)

REM Running AI service in background
echo Starting AI service...
START "AI Service" cmd /c "python app.py"
echo AI service will run at http://localhost:%AI_SERVICE_PORT%

REM Waiting for AI service to start
echo Waiting for AI service...
timeout /t 5 /nobreak > NUL

REM Returning to root directory
cd ..\..

REM Checking if Node.js is installed
node --version >NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed. Please install Node.js to run the frontend.
    echo Download from: https://nodejs.org/
    goto :END
)

REM Starting the frontend
cd src\frontend
echo Installing Node.js packages...
npm install

echo Starting Frontend service...
echo.
echo When the browser opens, log in with existing credentials
echo and then navigate to the chat page to use Gemini.
echo.
npm run dev

:END
ENDLOCAL 