@echo off
REM Quick Start Script for Silver Tier Demo
echo.
echo ========================================
echo   AI EMPLOYEE - SILVER TIER DEMO
echo ========================================
echo.

REM Check if already running
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *watcher*" 2>nul | find /I "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Watcher system is already running
    echo.
    goto :show_status
)

REM Start watcher system
echo [STEP 1] Starting watcher system...
start "AI Employee Watchers" python src\watcher.py
timeout /t 3 >nul

:show_status
echo.
echo [STEP 2] System Status:
echo.

REM Show watcher status
echo [WATCHERS]
tail -3 Logs\watcher_main.log 2>nul || echo   - Starting up...

echo.
echo [TASKS]
dir /b Needs_Action 2>nul | find /c /v "" && echo   tasks in Needs_Action folder

echo.
echo [PLANS]
dir /b Plans 2>nul | find /c /v "" && echo   plans generated

echo.
echo [COMPLETED]
dir /b Done 2>nul | find /c /v "" && echo   tasks completed

echo.
echo ========================================
echo   System is ready for demonstration!
echo ========================================
echo.
echo Next Steps:
echo   1. Process tasks: claude skill process-needs-action
echo   2. Approve plans: claude skill request-approval
echo   3. Execute actions: claude skill execute-approved-task
echo   4. View dashboard: Open Dashboard.md in Obsidian
echo.
pause
