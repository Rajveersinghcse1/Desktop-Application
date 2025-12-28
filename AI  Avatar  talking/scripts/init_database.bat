@echo off
REM Database initialization script for Windows

echo =========================================
echo AI Avatar Studio - Database Setup
echo =========================================

REM Set default database path
if "%DATABASE_PATH%"=="" set DATABASE_PATH=.\data\database\projects.db

echo Database path: %DATABASE_PATH%

REM Create directories
mkdir data\database 2>nul
mkdir data\cache 2>nul
mkdir data\logs 2>nul
mkdir output\videos 2>nul
mkdir output\thumbnails 2>nul
mkdir models 2>nul

REM Check if database exists
if exist "%DATABASE_PATH%" (
    echo [OK] Database already exists
    
    REM Show database info
    echo.
    echo Database Statistics:
    sqlite3 "%DATABASE_PATH%" "SELECT COUNT(*) as total_projects FROM projects; SELECT COUNT(*) as total_generations FROM generations;"
) else (
    echo [INFO] Creating new database...
    
    REM Initialize database using Python
    python -c "from utils.database import DatabaseManager; import os; db = DatabaseManager(os.getenv('DATABASE_PATH', './data/database/projects.db')); print('Database initialized successfully')"
    
    if errorlevel 1 (
        echo [ERROR] Failed to initialize database
        exit /b 1
    )
    
    echo [OK] Database created successfully
)

echo.
echo [OK] Database setup complete!
echo =========================================
pause
