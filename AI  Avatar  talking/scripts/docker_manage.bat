@echo off
REM Docker setup and management script for Windows

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

echo =========================================
echo AI Avatar Studio - Docker Management
echo =========================================

REM Check if Docker is installed
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed
    exit /b 1
)

where docker-compose >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not installed
    exit /b 1
)

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="setup" goto :setup
if "%1"=="build" goto :build
if "%1"=="start" goto :start
if "%1"=="stop" goto :stop
if "%1"=="restart" goto :restart
if "%1"=="logs" goto :logs
if "%1"=="status" goto :status
if "%1"=="backup" goto :backup
if "%1"=="cleanup" goto :cleanup
if "%1"=="shell" goto :shell

echo Unknown command: %1
goto :help

:setup
echo [INFO] Setting up Docker volumes...
mkdir "%PROJECT_ROOT%\docker_volumes\data\database" 2>nul
mkdir "%PROJECT_ROOT%\docker_volumes\data\cache" 2>nul
mkdir "%PROJECT_ROOT%\docker_volumes\data\logs" 2>nul
mkdir "%PROJECT_ROOT%\docker_volumes\models" 2>nul
mkdir "%PROJECT_ROOT%\docker_volumes\output\videos" 2>nul
mkdir "%PROJECT_ROOT%\docker_volumes\output\thumbnails" 2>nul
mkdir "%PROJECT_ROOT%\local_output" 2>nul
echo [OK] Volume directories created

echo.
echo [INFO] Building Docker image...
cd "%PROJECT_ROOT%"
docker-compose build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build Docker image
    exit /b 1
)
echo [OK] Docker image built

echo.
echo [INFO] Starting containers...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start containers
    exit /b 1
)
echo [OK] Containers started

echo.
echo [OK] Setup complete! Application is running.
goto :end

:build
echo [INFO] Building Docker image...
cd "%PROJECT_ROOT%"
docker-compose build
echo [OK] Build complete
goto :end

:start
echo [INFO] Starting containers...
cd "%PROJECT_ROOT%"
docker-compose up -d
echo [OK] Containers started
echo.
docker-compose ps
goto :end

:stop
echo [INFO] Stopping containers...
cd "%PROJECT_ROOT%"
docker-compose down
echo [OK] Containers stopped
goto :end

:restart
echo [INFO] Restarting containers...
cd "%PROJECT_ROOT%"
docker-compose restart
echo [OK] Containers restarted
goto :end

:logs
cd "%PROJECT_ROOT%"
docker-compose logs -f
goto :end

:status
echo Container Status:
cd "%PROJECT_ROOT%"
docker-compose ps

echo.
echo Database Status:
if exist "%PROJECT_ROOT%\docker_volumes\data\database\projects.db" (
    for %%A in ("%PROJECT_ROOT%\docker_volumes\data\database\projects.db") do echo Database Size: %%~zA bytes
    echo [OK] Database exists
) else (
    echo [INFO] Database not yet created
)
goto :end

:backup
echo [INFO] Creating database backup...
set "BACKUP_DIR=%PROJECT_ROOT%\backups"
mkdir "%BACKUP_DIR%" 2>nul

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/: " %%a in ('time /t') do (set mytime=%%a%%b)
set "TIMESTAMP=%mydate%_%mytime%"

set "BACKUP_FILE=%BACKUP_DIR%\projects_backup_%TIMESTAMP%.db"

if exist "%PROJECT_ROOT%\docker_volumes\data\database\projects.db" (
    copy "%PROJECT_ROOT%\docker_volumes\data\database\projects.db" "%BACKUP_FILE%"
    echo [OK] Backup created: %BACKUP_FILE%
) else (
    echo [ERROR] Database file not found
    exit /b 1
)
goto :end

:cleanup
echo [INFO] Cleaning up old data...
cd "%PROJECT_ROOT%"

REM Clean old cache files (older than 7 days)
forfiles /P "docker_volumes\data\cache" /S /D -7 /C "cmd /c del @path" 2>nul

REM Clean old logs (older than 30 days)
forfiles /P "docker_volumes\data\logs" /S /M *.log /D -30 /C "cmd /c del @path" 2>nul

REM Docker cleanup
docker system prune -f

echo [OK] Cleanup completed
goto :end

:shell
echo Opening shell in container...
cd "%PROJECT_ROOT%"
docker-compose exec ai-avatar-studio /bin/bash
goto :end

:help
echo Usage: %~nx0 [command]
echo.
echo Commands:
echo   setup       - Initial setup (create volumes, build image)
echo   build       - Build Docker image
echo   start       - Start containers
echo   stop        - Stop containers
echo   restart     - Restart containers
echo   logs        - View container logs
echo   status      - Show container and database status
echo   backup      - Backup database
echo   cleanup     - Clean up old files and Docker cache
echo   shell       - Open shell in container
echo   help        - Show this help message
echo.
echo Examples:
echo   %~nx0 setup      # First-time setup
echo   %~nx0 start      # Start the application
echo   %~nx0 logs       # View logs
echo   %~nx0 backup     # Backup database
goto :end

:end
endlocal
