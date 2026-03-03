#!/usr/bin/env python3
"""
Orchestrator v3.0 - Complete Workflow Automation
Manages: Watchers → Needs_Action → Claude Reasoning → Pending_Approval → Human Approval → Execution → Done
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INBOX_DIR = os.path.join(BASE_DIR, "Inbox")
NEEDS_ACTION_DIR = os.path.join(BASE_DIR, "Needs_Action")
PLANS_DIR = os.path.join(BASE_DIR, "Plans")
PENDING_APPROVAL_DIR = os.path.join(BASE_DIR, "Pending_Approval")
APPROVED_DIR = os.path.join(BASE_DIR, "Approved")
DONE_DIR = os.path.join(BASE_DIR, "Done")
LOGS_DIR = os.path.join(BASE_DIR, "Logs")

# Session tracking
SESSION_FILE = os.path.join(LOGS_DIR, "orchestrator_session.json")


class Orchestrator:
    """Main orchestrator coordinating complete workflow"""

    def __init__(self, watch_mode=False, interval=60):
        self.watch_mode = watch_mode
        self.interval = interval
        self.running = False

        # Ensure directories exist
        for directory in [INBOX_DIR, NEEDS_ACTION_DIR, PLANS_DIR, PENDING_APPROVAL_DIR,
                         APPROVED_DIR, DONE_DIR, LOGS_DIR]:
            os.makedirs(directory, exist_ok=True)

        # Load session
        self.session = self.load_session()

        self.log("Orchestrator v3.0 initialized", "SYSTEM")

    def log(self, message, level="INFO"):
        """Log messages to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [ORCHESTRATOR] [{level}] {message}"
        print(log_entry)

        log_file = os.path.join(LOGS_DIR, "orchestrator.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def load_session(self):
        """Load session data from file"""
        default_session = {
            "last_run": None,
            "total_processed": 0,
            "total_approved": 0,
            "total_executed": 0,
            "emails_sent": 0,
            "linkedin_posted": 0
        }

        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_session.update(loaded)
                    return default_session
            except Exception as e:
                self.log(f"Error loading session: {e}", "WARNING")

        return default_session

    def save_session(self):
        """Save session data to file"""
        try:
            with open(SESSION_FILE, 'w') as f:
                json.dump(self.session, f, indent=2)
        except Exception as e:
            self.log(f"Error saving session: {e}", "ERROR")

    def count_files(self, directory):
        """Count files in a directory"""
        try:
            return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
        except Exception:
            return 0

    def invoke_claude_code(self, skill_name):
        """Invoke Claude Code skill using CCR code"""
        self.log(f"Invoking Claude Code skill: {skill_name}", "SYSTEM")
        try:
            # Use subprocess to invoke Claude Code
            result = subprocess.run(
                ['claude', 'skill', skill_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                self.log(f"[OK] Claude Code skill '{skill_name}' completed successfully", "SUCCESS")
                return True
            else:
                self.log(f"[WARNING] Claude Code skill '{skill_name}' had issues", "WARNING")
                if result.stderr:
                    self.log(f"Error: {result.stderr[:200]}", "WARNING")
                return False
        except subprocess.TimeoutExpired:
            self.log(f"[ERROR] Claude Code skill '{skill_name}' timed out", "ERROR")
            return False
        except Exception as e:
            self.log(f"[ERROR] Failed to invoke Claude Code: {e}", "ERROR")
            return False

    def step_reasoning(self):
        """Step 2: Claude Code Reasoning - Needs_Action -> Plans -> Pending_Approval"""
        self.log("=" * 60, "SYSTEM")
        self.log("STEP 2: Processing (Needs_Action -> Pending_Approval)", "SYSTEM")
        self.log("=" * 60, "SYSTEM")

        needs_action_count = self.count_files(NEEDS_ACTION_DIR)

        if needs_action_count == 0:
            self.log("No files in Needs_Action/ - nothing to process", "INFO")
            return 0

        self.log(f"Found {needs_action_count} files in Needs_Action/", "INFO")
        self.log("Processing via Python script...", "SYSTEM")

        # Call Python script directly instead of Claude Code
        process_script = os.path.join(BASE_DIR, "src", "process_needs_action.py")
        if os.path.exists(process_script):
            try:
                result = subprocess.run(
                    ['python', process_script],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode == 0:
                    pending_count = self.count_files(PENDING_APPROVAL_DIR)
                    self.log(f"[OK] Processing complete - {pending_count} plans in Pending_Approval/", "SUCCESS")
                    self.session['total_processed'] += needs_action_count
                    return pending_count
                else:
                    self.log("[WARNING] Processing had issues", "WARNING")
                    if result.stderr:
                        self.log(f"Error: {result.stderr[:200]}", "WARNING")
                    return 0
            except Exception as e:
                self.log(f"[ERROR] Processing error: {e}", "ERROR")
                return 0
        else:
            self.log("[ERROR] Process script not found - skipping", "ERROR")
            return 0

    def step_wait_for_approval(self):
        """Step 3: Wait for Human Approval - Pending_Approval -> Approved (manual)"""
        self.log("=" * 60, "SYSTEM")
        self.log("STEP 3: Waiting for Human Approval", "SYSTEM")
        self.log("=" * 60, "SYSTEM")

        pending_count = self.count_files(PENDING_APPROVAL_DIR)
        approved_count = self.count_files(APPROVED_DIR)

        self.log(f"Pending Approval: {pending_count} files", "INFO")
        self.log(f"Approved: {approved_count} files", "INFO")

        if pending_count > 0:
            self.log("", "INFO")
            self.log("ACTION REQUIRED: Please review and approve plans", "INFO")
            self.log(f"1. Check files in: {PENDING_APPROVAL_DIR}", "INFO")
            self.log(f"2. Move approved files to: {APPROVED_DIR}", "INFO")
            self.log("3. Run orchestrator again to execute approved plans", "INFO")
            self.log("", "INFO")

        return approved_count

    def step_execute(self):
        """Step 4: Execute Approved Plans - Approved -> Done (only on success)"""
        self.log("=" * 60, "SYSTEM")
        self.log("STEP 4: Executing Approved Plans", "SYSTEM")
        self.log("=" * 60, "SYSTEM")

        approved_count = self.count_files(APPROVED_DIR)

        if approved_count == 0:
            self.log("No approved plans in Approved/ - nothing to execute", "INFO")
            return 0

        self.log(f"Found {approved_count} approved plans in Approved/", "INFO")

        emails_sent = 0
        linkedin_posted = 0

        # Step 4: Use AUTO SENDER (actually sends emails!)
        self.log("Step 4: Running Auto Sender (ACTUAL email sending)...", "SYSTEM")
        auto_sender_script = os.path.join(BASE_DIR, "auto_sender.py")
        if os.path.exists(auto_sender_script):
            try:
                result = subprocess.run(
                    ['python', auto_sender_script],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode == 0:
                    # Check output for success
                    output = result.stdout
                    if "EMAIL SENT" in output:
                        emails_sent = output.count("EMAIL SENT")
                        self.log(f"[OK] {emails_sent} email(s) sent successfully", "SUCCESS")
                        self.session['emails_sent'] += emails_sent

                    if "LinkedIn content saved" in output or "READY" in output:
                        linkedin_posted = 1
                        self.log("[OK] LinkedIn content prepared", "SUCCESS")
                        self.session['linkedin_posted'] += linkedin_posted

                    if emails_sent == 0 and linkedin_posted == 0:
                        self.log("[INFO] No items to send or already sent", "INFO")
                else:
                    self.log("[WARNING] Auto sender had issues", "WARNING")
                    if result.stderr:
                        self.log(f"Error: {result.stderr[:200]}", "WARNING")
            except Exception as e:
                self.log(f"[WARNING] Auto sender error: {e}", "WARNING")
        else:
            self.log("[ERROR] auto_sender.py not found!", "ERROR")

        # Step 4c: Move to Done ONLY if successful
        self.log("Step 4c: Moving completed tasks to Done/...", "SYSTEM")
        moved_count = 0

        if emails_sent > 0 or linkedin_posted > 0:
            try:
                approved_files = [f for f in os.listdir(APPROVED_DIR) if f.endswith('.md')]
                for plan_file in approved_files:
                    src = os.path.join(APPROVED_DIR, plan_file)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dst = os.path.join(DONE_DIR, f"{plan_file.replace('.md', '')}_executed_{timestamp}.md")
                    os.rename(src, dst)
                    moved_count += 1
                    self.log(f"Moved to Done: {plan_file}", "INFO")

                self.session['total_executed'] += moved_count
            except Exception as e:
                self.log(f"[WARNING] Error moving files: {e}", "WARNING")
        else:
            self.log("[WARNING] No successful executions - files remain in Approved/", "WARNING")

        # Print summary
        self.log("=" * 60, "SYSTEM")
        self.log("EXECUTION SUMMARY", "SYSTEM")
        self.log("=" * 60, "SYSTEM")
        self.log(f"[OK] Emails sent: {emails_sent}", "SUCCESS" if emails_sent else "INFO")
        self.log(f"[OK] LinkedIn posts: {linkedin_posted}", "SUCCESS" if linkedin_posted else "INFO")
        self.log(f"[OK] Files moved to Done: {moved_count}", "SUCCESS" if moved_count else "INFO")
        self.log("=" * 60, "SYSTEM")

        return moved_count

    def run_complete_workflow(self):
        """Run complete workflow"""
        self.log("=" * 60, "SYSTEM")
        self.log("STARTING COMPLETE WORKFLOW", "SYSTEM")
        self.log("=" * 60, "SYSTEM")

        start_time = time.time()

        # Step 1: Watchers (running in background - not managed here)
        self.log("Step 1: Watchers running in background", "INFO")

        # Step 2: Claude Code Reasoning
        plans_created = self.step_reasoning()

        # Step 3: Wait for Human Approval
        approved_count = self.step_wait_for_approval()

        # Step 4: Execute Approved Plans
        if approved_count > 0:
            executed = self.step_execute()
        else:
            self.log("No approved plans to execute", "INFO")

        # Update session
        self.session['last_run'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_session()

        elapsed = time.time() - start_time

        self.log("=" * 60, "SYSTEM")
        self.log(f"WORKFLOW COMPLETE in {elapsed:.2f}s", "SUCCESS")
        self.log("=" * 60, "SYSTEM")

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print workflow summary"""
        print("\n" + "=" * 60)
        print("[STATS] WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"[INBOX] Needs_Action: {self.count_files(NEEDS_ACTION_DIR)} files")
        print(f"[PLANS] Pending_Approval: {self.count_files(PENDING_APPROVAL_DIR)} files")
        print(f"[OK] Approved: {self.count_files(APPROVED_DIR)} files")
        print(f"[DONE] Done: {self.count_files(DONE_DIR)} files")
        print("=" * 60)
        print(f"Total Processed: {self.session['total_processed']}")
        print(f"Total Executed: {self.session['total_executed']}")
        print(f"Emails Sent: {self.session['emails_sent']}")
        print(f"LinkedIn Posted: {self.session['linkedin_posted']}")
        print(f"Last Run: {self.session['last_run']}")
        print("=" * 60 + "\n")

    def watch_loop(self):
        """Continuous watch mode"""
        self.log(f"Starting watch mode (interval: {self.interval}s)", "SYSTEM")
        self.running = True

        try:
            while self.running:
                self.run_complete_workflow()

                if self.running:
                    self.log(f"Sleeping for {self.interval}s...", "INFO")
                    time.sleep(self.interval)
        except KeyboardInterrupt:
            self.log("Watch mode interrupted by user", "SYSTEM")
        finally:
            self.running = False

    def start(self):
        """Start orchestrator"""
        try:
            if self.watch_mode:
                self.watch_loop()
            else:
                self.run_complete_workflow()
        except KeyboardInterrupt:
            self.log("Orchestrator interrupted by user", "SYSTEM")
        finally:
            self.log("Orchestrator stopped", "SYSTEM")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Orchestrator v3.0 - Complete Workflow Automation"
    )

    parser.add_argument(
        '--watch',
        action='store_true',
        help='Run in continuous watch mode'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Watch mode interval in seconds (default: 300)'
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = Orchestrator(
        watch_mode=args.watch,
        interval=args.interval
    )

    # Run workflow
    orchestrator.start()


if __name__ == "__main__":
    main()
