@echo off
REM ============================================================
REM AI Employee - Master Automation Script (Windows)
REM Runs periodic tasks every 30 minutes
REM ============================================================

echo.
echo ========================================
echo AI Employee - Automation Cycle Starting
echo ========================================
echo Time: %date% %time%
echo.

REM Set project directory
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

REM Create logs directory if not exists
if not exist "Logs" mkdir Logs

REM Set log file
set LOG_FILE=Logs\automation_cycle.log

REM Log start time
echo [%date% %time%] === Automation Cycle Started === >> "%LOG_FILE%"

REM ============================================================
REM STEP A: Check if Watchers are Running (Optional)
REM ============================================================
echo [STEP A] Checking watcher status...
echo [%date% %time%] [STEP A] Checking watcher status >> "%LOG_FILE%"

REM Note: Watchers should be running as a separate background process
REM This step just logs the status
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *watcher*" 2>nul | find /I "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo   - Watchers: RUNNING
    echo [%date% %time%] [STEP A] Watchers are running >> "%LOG_FILE%"
) else (
    echo   - Watchers: NOT DETECTED
    echo [%date% %time%] [STEP A] WARNING: Watchers not detected >> "%LOG_FILE%"
)

REM ============================================================
REM STEP B: Process Needs_Action (if script exists)
REM ============================================================
echo.
echo [STEP B] Processing Needs_Action folder...
echo [%date% %time%] [STEP B] Processing Needs_Action >> "%LOG_FILE%"

REM Check if process script exists
if exist "src\process_needs_action.py" (
    python src\process_needs_action.py >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   - Status: SUCCESS
        echo [%date% %time%] [STEP B] Process Needs_Action completed successfully >> "%LOG_FILE%"
    ) else (
        echo   - Status: FAILED
        echo [%date% %time%] [STEP B] ERROR: Process Needs_Action failed >> "%LOG_FILE%"
    )
) else (
    echo   - Status: SKIPPED (script not found)
    echo [%date% %time%] [STEP B] SKIPPED: process_needs_action.py not found >> "%LOG_FILE%"
)

REM ============================================================
REM STEP C: Generate Marketing Posts (Weekly - Check day)
REM ============================================================
echo.
echo [STEP C] Checking if marketing posts needed...
echo [%date% %time%] [STEP C] Checking marketing generation >> "%LOG_FILE%"

REM Get day of week (1=Monday, 7=Sunday)
for /f "tokens=1" %%a in ('powershell -Command "(Get-Date).DayOfWeek.value__"') do set DAY_OF_WEEK=%%a

REM Run marketing generation only on Mondays (1)
if "%DAY_OF_WEEK%"=="1" (
    echo   - Day: Monday - Generating marketing posts
    echo [%date% %time%] [STEP C] Monday detected - generating marketing posts >> "%LOG_FILE%"

    REM Note: This requires Claude Code CLI or manual execution
    echo   - Status: MANUAL EXECUTION REQUIRED
    echo   - Run: /generate-marketing via Claude Code
    echo [%date% %time%] [STEP C] Marketing generation requires manual execution >> "%LOG_FILE%"
) else (
    echo   - Day: Not Monday - Skipping marketing generation
    echo [%date% %time%] [STEP C] Not Monday - skipping marketing generation >> "%LOG_FILE%"
)

REM ============================================================
REM STEP D: Execute Approved Actions
REM ============================================================
echo.
echo [STEP D] Executing approved actions...
echo [%date% %time%] [STEP D] Executing approved actions >> "%LOG_FILE%"

if exist "src\action_executor.py" (
    python src\action_executor.py >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   - Status: SUCCESS
        echo [%date% %time%] [STEP D] Action execution completed successfully >> "%LOG_FILE%"
    ) else (
        echo   - Status: FAILED
        echo [%date% %time%] [STEP D] ERROR: Action execution failed >> "%LOG_FILE%"
    )
) else (
    echo   - Status: SKIPPED (script not found)
    echo [%date% %time%] [STEP D] SKIPPED: action_executor.py not found >> "%LOG_FILE%"
)

REM ============================================================
REM STEP E: Update Dashboard (if script exists)
REM ============================================================
echo.
echo [STEP E] Updating dashboard...
echo [%date% %time%] [STEP E] Updating dashboard >> "%LOG_FILE%"

if exist "src\update_dashboard.py" (
    python src\update_dashboard.py >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   - Status: SUCCESS
        echo [%date% %time%] [STEP E] Dashboard update completed successfully >> "%LOG_FILE%"
    ) else (
        echo   - Status: FAILED
        echo [%date% %time%] [STEP E] ERROR: Dashboard update failed >> "%LOG_FILE%"
    )
) else (
    echo   - Status: SKIPPED (script not found)
    echo [%date% %time%] [STEP E] SKIPPED: update_dashboard.py not found >> "%LOG_FILE%"
)

REM ============================================================
REM Summary
REM ============================================================
echo.
echo ========================================
echo Automation Cycle Complete
echo ========================================
echo Time: %date% %time%
echo Check Logs\automation_cycle.log for details
echo.

echo [%date% %time%] === Automation Cycle Completed === >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Exit
exit /b 0
