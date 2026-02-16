@echo off
REM ============================================================
REM AI Employee - Start Watchers (Windows)
REM Starts the multi-threaded watcher system
REM ============================================================

echo.
echo ========================================
echo AI Employee - Starting Watcher System
echo ========================================
echo.

REM Set project directory
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

REM Check if watcher script exists
if not exist "src\watcher.py" (
    echo ERROR: watcher.py not found in src\ folder
    echo Please ensure the file exists before running this script.
    pause
    exit /b 1
)

echo Starting multi-threaded watcher system...
echo.
echo Threads:
echo   - Thread 1: Local file monitoring (continuous)
echo   - Thread 2: Gmail monitoring (5-minute intervals)
echo   - Thread 3: LinkedIn trends (1-hour intervals)
echo.
echo Press Ctrl+C to stop the watchers
echo.
echo ========================================
echo.

REM Start the watcher system
python src\watcher.py

REM If watcher exits, show message
echo.
echo ========================================
echo Watcher system stopped
echo ========================================
echo.
pause
