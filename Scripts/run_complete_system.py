#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER ORCHESTRATOR - Complete Automation
Runs everything: Watchers → Processing → Auto Sending
"""
import os
import sys
import io
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime

# Fix Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).parent.parent  # Project root (go up from Scripts/)

def log(message, component="MASTER"):
    """Simple logging"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{timestamp}] [{component}] {message}')

def run_watcher():
    """Run the watcher in background"""
    log("Starting watcher...", "WATCHER")
    try:
        subprocess.Popen([sys.executable, 'src/watcher.py'],
                        cwd=BASE_DIR,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
        log("Watcher started", "WATCHER")
    except Exception as e:
        log(f"Failed to start watcher: {e}", "WATCHER")

def run_auto_sender():
    """Run auto sender in watch mode"""
    log("Starting auto sender...", "SENDER")
    try:
        # Run in same process so we can see output
        subprocess.run([sys.executable, 'auto_sender.py', '--watch'],
                      cwd=BASE_DIR)
    except KeyboardInterrupt:
        log("Auto sender stopped", "SENDER")
    except Exception as e:
        log(f"Auto sender error: {e}", "SENDER")

def check_dependencies():
    """Check if all required files exist"""
    import glob

    required_files = [
        'auto_sender.py',
        'src/watcher.py'
    ]

    # Check for client_secret file
    client_secret_files = glob.glob('client_secret_*.json')

    missing = []
    for file in required_files:
        if not (BASE_DIR / file).exists():
            missing.append(file)

    if not client_secret_files:
        missing.append('client_secret_*.json (Google OAuth credentials)')

    if missing:
        log(f"Missing files: {', '.join(missing)}", "ERROR")
        return False

    return True

def main():
    log("=" * 60)
    log("AI EMPLOYEE - COMPLETE AUTOMATION SYSTEM")
    log("=" * 60)

    # Check dependencies
    if not check_dependencies():
        log("Please ensure all required files are present", "ERROR")
        return

    log("System ready!")
    log("")
    log("What's running:")
    log("  1. Watcher - Monitors Gmail, LinkedIn, Local files")
    log("  2. Auto Sender - Sends emails from 4_Approved folder")
    log("")
    log("How it works:")
    log("  - Drop files in 4_Approved folder")
    log("  - Auto sender will ACTUALLY send them")
    log("  - Emails go via Gmail API")
    log("  - LinkedIn posts saved for manual posting")
    log("")
    log("Press Ctrl+C to stop")
    log("=" * 60)
    log("")

    # Start watcher in background
    watcher_thread = threading.Thread(target=run_watcher, daemon=True)
    watcher_thread.start()

    # Give watcher time to start
    time.sleep(2)

    # Run auto sender in foreground (so we see output)
    try:
        run_auto_sender()
    except KeyboardInterrupt:
        log("\nShutting down...")
        log("System stopped")

if __name__ == '__main__':
    main()
