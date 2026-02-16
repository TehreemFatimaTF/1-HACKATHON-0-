#!/bin/bash
# ============================================================
# AI Employee - Start Watchers (Unix/Linux/Mac)
# Starts the multi-threaded watcher system
# ============================================================

echo ""
echo "========================================"
echo "AI Employee - Starting Watcher System"
echo "========================================"
echo ""

# Set project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Check if watcher script exists
if [ ! -f "src/watcher.py" ]; then
    echo "ERROR: watcher.py not found in src/ folder"
    echo "Please ensure the file exists before running this script."
    exit 1
fi

echo "Starting multi-threaded watcher system..."
echo ""
echo "Threads:"
echo "  - Thread 1: Local file monitoring (continuous)"
echo "  - Thread 2: Gmail monitoring (5-minute intervals)"
echo "  - Thread 3: LinkedIn trends (1-hour intervals)"
echo ""
echo "Press Ctrl+C to stop the watchers"
echo ""
echo "========================================"
echo ""

# Start the watcher system
python3 src/watcher.py

# If watcher exits, show message
echo ""
echo "========================================"
echo "Watcher system stopped"
echo "========================================"
echo ""
