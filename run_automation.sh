#!/bin/bash
# ============================================================
# AI Employee - Master Automation Script (Unix/Linux/Mac)
# Runs periodic tasks every 30 minutes
# ============================================================

echo ""
echo "========================================"
echo "AI Employee - Automation Cycle Starting"
echo "========================================"
echo "Time: $(date)"
echo ""

# Set project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Create logs directory if not exists
mkdir -p Logs

# Set log file
LOG_FILE="Logs/automation_cycle.log"

# Log start time
echo "[$(date)] === Automation Cycle Started ===" >> "$LOG_FILE"

# ============================================================
# STEP A: Check if Watchers are Running (Optional)
# ============================================================
echo "[STEP A] Checking watcher status..."
echo "[$(date)] [STEP A] Checking watcher status" >> "$LOG_FILE"

# Check if watcher process is running
if pgrep -f "watcher.py" > /dev/null; then
    echo "  - Watchers: RUNNING"
    echo "[$(date)] [STEP A] Watchers are running" >> "$LOG_FILE"
else
    echo "  - Watchers: NOT DETECTED"
    echo "[$(date)] [STEP A] WARNING: Watchers not detected" >> "$LOG_FILE"
fi

# ============================================================
# STEP B: Process Needs_Action (if script exists)
# ============================================================
echo ""
echo "[STEP B] Processing Needs_Action folder..."
echo "[$(date)] [STEP B] Processing Needs_Action" >> "$LOG_FILE"

if [ -f "src/process_needs_action.py" ]; then
    python3 src/process_needs_action.py >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        echo "  - Status: SUCCESS"
        echo "[$(date)] [STEP B] Process Needs_Action completed successfully" >> "$LOG_FILE"
    else
        echo "  - Status: FAILED"
        echo "[$(date)] [STEP B] ERROR: Process Needs_Action failed" >> "$LOG_FILE"
    fi
else
    echo "  - Status: SKIPPED (script not found)"
    echo "[$(date)] [STEP B] SKIPPED: process_needs_action.py not found" >> "$LOG_FILE"
fi

# ============================================================
# STEP C: Generate Marketing Posts (Weekly - Check day)
# ============================================================
echo ""
echo "[STEP C] Checking if marketing posts needed..."
echo "[$(date)] [STEP C] Checking marketing generation" >> "$LOG_FILE"

# Get day of week (1=Monday, 7=Sunday)
DAY_OF_WEEK=$(date +%u)

# Run marketing generation only on Mondays (1)
if [ "$DAY_OF_WEEK" -eq 1 ]; then
    echo "  - Day: Monday - Generating marketing posts"
    echo "[$(date)] [STEP C] Monday detected - generating marketing posts" >> "$LOG_FILE"

    # Note: This requires Claude Code CLI or manual execution
    echo "  - Status: MANUAL EXECUTION REQUIRED"
    echo "  - Run: /generate-marketing via Claude Code"
    echo "[$(date)] [STEP C] Marketing generation requires manual execution" >> "$LOG_FILE"
else
    echo "  - Day: Not Monday - Skipping marketing generation"
    echo "[$(date)] [STEP C] Not Monday - skipping marketing generation" >> "$LOG_FILE"
fi

# ============================================================
# STEP D: Execute Approved Actions
# ============================================================
echo ""
echo "[STEP D] Executing approved actions..."
echo "[$(date)] [STEP D] Executing approved actions" >> "$LOG_FILE"

if [ -f "src/action_executor.py" ]; then
    python3 src/action_executor.py >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        echo "  - Status: SUCCESS"
        echo "[$(date)] [STEP D] Action execution completed successfully" >> "$LOG_FILE"
    else
        echo "  - Status: FAILED"
        echo "[$(date)] [STEP D] ERROR: Action execution failed" >> "$LOG_FILE"
    fi
else
    echo "  - Status: SKIPPED (script not found)"
    echo "[$(date)] [STEP D] SKIPPED: action_executor.py not found" >> "$LOG_FILE"
fi

# ============================================================
# STEP E: Update Dashboard (if script exists)
# ============================================================
echo ""
echo "[STEP E] Updating dashboard..."
echo "[$(date)] [STEP E] Updating dashboard" >> "$LOG_FILE"

if [ -f "src/update_dashboard.py" ]; then
    python3 src/update_dashboard.py >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        echo "  - Status: SUCCESS"
        echo "[$(date)] [STEP E] Dashboard update completed successfully" >> "$LOG_FILE"
    else
        echo "  - Status: FAILED"
        echo "[$(date)] [STEP E] ERROR: Dashboard update failed" >> "$LOG_FILE"
    fi
else
    echo "  - Status: SKIPPED (script not found)"
    echo "[$(date)] [STEP E] SKIPPED: update_dashboard.py not found" >> "$LOG_FILE"
fi

# ============================================================
# Summary
# ============================================================
echo ""
echo "========================================"
echo "Automation Cycle Complete"
echo "========================================"
echo "Time: $(date)"
echo "Check Logs/automation_cycle.log for details"
echo ""

echo "[$(date)] === Automation Cycle Completed ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Exit
exit 0
