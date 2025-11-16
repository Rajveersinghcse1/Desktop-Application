@echo off
REM OpenUP Launch Script for Windows
REM Automates setup and launching

echo ====================================
echo OpenUP - Quick Launch
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo.
echo Checking dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Launch application
echo.
echo Launching OpenUP...
python main.py %*

REM Deactivate virtual environment
deactivate

pause
