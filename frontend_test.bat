@echo off
echo Running Frontend Component Tests...
cd src\frontend
echo Checking if test command is available...
call npm list vitest >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing vitest...
    call npm install --save-dev vitest
)

echo Setting up test environment...
call npm install --no-save @testing-library/react @testing-library/jest-dom jsdom
echo Running tests for frontend components...
call npx vitest run --reporter verbose
if %ERRORLEVEL% EQU 0 (
    echo Frontend tests completed successfully!
) else (
    echo Some frontend tests failed with code %ERRORLEVEL%.
)
cd ..\..
echo Test execution completed. 