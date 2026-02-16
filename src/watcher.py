import time
import threading
import os
from datetime import datetime

# Import individual watchers
from watcher_local import LocalFileWatcher
from watcher_gmail import GmailWatcher
from watcher_linkedin import LinkedInWatcher

# Configuration
LOGS_DIR = os.path.join(os.getcwd(), "Logs")

# Multi-Source Configuration
SOURCES_CONFIG = {
    "local_files": True,      # Always enabled
    "gmail": True,            # Gmail API enabled
    "linkedin": True          # Simulated for demo
}

class MultiSourceWatcher:
    """Orchestrates multiple watchers running concurrently"""

    def __init__(self):
        self.running = False
        self.threads = []
        self.watchers = {}
        self.log_file = os.path.join(LOGS_DIR, "watcher_main.log")

    def log(self, message, level="INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [MAIN] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def start_watcher(self, name, watcher_class):
        """Start a watcher in a separate thread"""
        try:
            watcher = watcher_class()
            self.watchers[name] = watcher

            thread = threading.Thread(target=watcher.start, daemon=True, name=name)
            thread.start()
            self.threads.append(thread)

            self.log(f"Started {name} watcher")
            return True
        except Exception as e:
            self.log(f"Failed to start {name} watcher: {e}", "ERROR")
            return False

    def start(self):
        """Start all enabled watchers"""
        self.running = True

        print("\n" + "="*60)
        print("PERSONAL AI EMPLOYEE - MULTI-SOURCE WATCHER")
        print("="*60)
        self.log("=== Multi-Source Watcher Starting ===", "SYSTEM")

        # Start enabled watchers
        started_count = 0

        if SOURCES_CONFIG["local_files"]:
            if self.start_watcher("Local Files", LocalFileWatcher):
                started_count += 1

        if SOURCES_CONFIG["gmail"]:
            if self.start_watcher("Gmail", GmailWatcher):
                started_count += 1
        else:
            self.log("Gmail watcher disabled (set gmail=True in config to enable)")

        if SOURCES_CONFIG["linkedin"]:
            if self.start_watcher("LinkedIn", LinkedInWatcher):
                started_count += 1

        # Summary
        print("\n" + "-"*60)
        print(f"[OK] Active Watchers: {started_count}")
        print(f"[INFO] Monitoring Sources: {[k for k, v in SOURCES_CONFIG.items() if v]}")
        print(f"[INFO] Logs Directory: {LOGS_DIR}")
        print("-"*60)
        print("\n[TIP] Press Ctrl+C to stop all watchers\n")

        self.log(f"Successfully started {started_count} watchers", "SYSTEM")

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop all watchers gracefully"""
        print("\n" + "="*60)
        self.log("=== Shutting down all watchers ===", "SYSTEM")

        # Stop all watchers
        for name, watcher in self.watchers.items():
            try:
                watcher.stop()
                self.log(f"Stopped {name} watcher")
            except Exception as e:
                self.log(f"Error stopping {name} watcher: {e}", "ERROR")

        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=2)

        self.running = False
        self.log("All watchers stopped", "SYSTEM")
        print("="*60)
        print("Multi-Source Watcher stopped successfully")
        print("="*60 + "\n")

if __name__ == "__main__":
    print("\n[STARTING] Personal AI Employee Watcher System...\n")
    watcher = MultiSourceWatcher()
    watcher.start()
