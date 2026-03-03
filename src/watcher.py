import time
import threading
import os
from datetime import datetime
from pathlib import Path

# Import individual watchers
from watcher_local import LocalFileWatcher
from watcher_gmail import GmailWatcher
from watcher_linkedin import LinkedInWatcher
from watcher_whatsapp import WhatsAppWatcher

# Import Gold Tier autonomous engine
try:
    from engine_gold import RalphWiggumLoopEngine
    GOLD_TIER_AVAILABLE = True
except ImportError:
    GOLD_TIER_AVAILABLE = False
    print("[WARNING] Gold Tier engine not available - running in Silver Tier mode")

# Configuration
LOGS_DIR = os.path.join(os.getcwd(), "Logs")

# Multi-Source Configuration
SOURCES_CONFIG = {
    "local_files": True,      # Always enabled
    "gmail": True,            # Gmail API enabled
    "linkedin": True,         # Simulated for demo
    "whatsapp": True          # WhatsApp Web monitoring via Playwright
}

# Gold Tier Autonomous Mode Configuration
GOLD_TIER_CONFIG = {
    "enabled": False,  # Set to True to enable autonomous execution
    "autonomous_whitelist": [
        # Actions that can be executed autonomously without human approval
        "detect_trend",
        "create_social_post",
        "log_marketing_expense",
        "sync_contacts",
        "fetch_engagement_metrics",
        "analyze_sentiment",
        "update_dashboard",
    ],
    "require_approval_for": [
        # Actions that always require human approval (P0/P1 critical operations)
        "create_invoice",
        "approve_expense",
        "send_client_email",
        "delete_data",
        "modify_accounting_records",
    ],
    "auto_approve_threshold": {
        # Automatic approval thresholds for financial operations
        "expense_amount": 500.0,  # Expenses >= $500 require approval
        "invoice_amount": 1000.0,  # Invoices >= $1000 require approval
    }
}

class MultiSourceWatcher:
    """Orchestrates multiple watchers running concurrently"""

    def __init__(self):
        self.running = False
        self.threads = []
        self.watchers = {}
        self.log_file = os.path.join(LOGS_DIR, "watcher_main.log")

        # Initialize Gold Tier engine if enabled
        self.gold_tier_engine = None
        self.autonomous_mode = GOLD_TIER_CONFIG["enabled"]

        if self.autonomous_mode and GOLD_TIER_AVAILABLE:
            try:
                self.gold_tier_engine = RalphWiggumLoopEngine()
                self.log("Gold Tier autonomous engine initialized", "SYSTEM")
            except Exception as e:
                self.log(f"Failed to initialize Gold Tier engine: {e}", "ERROR")
                self.autonomous_mode = False

    def log(self, message, level="INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [MAIN] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def is_action_autonomous(self, action_name: str) -> bool:
        """
        Check if an action can be executed autonomously without human approval

        Args:
            action_name: Name of the action to check

        Returns:
            True if action is whitelisted for autonomous execution
        """
        if not self.autonomous_mode:
            return False

        # Check if action requires approval
        if action_name in GOLD_TIER_CONFIG["require_approval_for"]:
            return False

        # Check if action is whitelisted
        return action_name in GOLD_TIER_CONFIG["autonomous_whitelist"]

    def requires_financial_approval(self, action_type: str, amount: float) -> bool:
        """
        Check if a financial action requires human approval based on amount threshold

        Args:
            action_type: Type of financial action (e.g., "expense", "invoice")
            amount: Transaction amount

        Returns:
            True if amount exceeds threshold and requires approval
        """
        thresholds = GOLD_TIER_CONFIG["auto_approve_threshold"]

        if action_type == "expense":
            return amount >= thresholds["expense_amount"]
        elif action_type == "invoice":
            return amount >= thresholds["invoice_amount"]

        return False  # Unknown action types don't require approval by default

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

        if SOURCES_CONFIG["whatsapp"]:
            if self.start_watcher("WhatsApp", WhatsAppWatcher):
                started_count += 1
        else:
            self.log("WhatsApp watcher disabled (set whatsapp=True in config to enable)")

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
