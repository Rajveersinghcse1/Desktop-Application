@echo off
REM Quick launcher for OpenUP with LAS file support
echo =========================================
echo   OpenUP - File Viewer
echo =========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then activate and install dependencies
    pause
    exit /b 1
)

REM Launch application
echo Starting OpenUP...
echo.
"venv\Scripts\python.exe" main.py %*

if errorlevel 1 (
    echo.
    echo [ERROR] Application crashed or exited with error
    pause
)
