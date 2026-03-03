#!/usr/bin/env python3
"""
Handle approval/rejection of plans in the Pending_Approval folder.
This script scans for files with approval/rejection checkboxes and processes them accordingly.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import json
import sys
import re
from typing import Dict, Any, Optional

# Add the project root to sys.path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.action_executor import ActionExecutor

# Configuration
BASE_DIR = Path(__file__).parent.parent
PENDING_APPROVAL_DIR = BASE_DIR / "Pending_Approval"
APPROVED_DIR = BASE_DIR / "4_Approved"  # Existing folder used for approved plans
REJECTED_DIR = BASE_DIR / "Rejected"    # New folder for rejected plans
DONE_DIR = BASE_DIR / "Done"
LOGS_DIR = BASE_DIR / "Logs"

# Create directories if they don't exist
for directory in [PENDING_APPROVAL_DIR, APPROVED_DIR, REJECTED_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)


class ApprovalHandler:
    """Handle approval/rejection of plans in Pending_Approval folder"""

    def __init__(self):
        self.log_file = LOGS_DIR / "approval_handler.log"
        self.action_executor = ActionExecutor()

    def log(self, message, level="INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [APPROVAL] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def check_approval_status(self, filepath: Path) -> str:
        """Check if the file has approval or rejection status"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for approval checkboxes in the format: - [x] Approve or - [x] Reject
        approve_pattern = r'-\s*\[x\].*?(Approve|APPROVE|approve)'
        reject_pattern = r'-\s*\[x\].*?(Reject|REJECT|reject)'

        if re.search(approve_pattern, content, re.IGNORECASE):
            return 'approved'
        elif re.search(reject_pattern, content, re.IGNORECASE):
            return 'rejected'
        else:
            return 'pending'

    def extract_email_info_from_plan(self, filepath: Path) -> Dict[str, Any]:
        """Extract email information from the plan file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        email_info = {
            'recipient': 'Unknown',
            'subject': 'Unknown',
            'original_email_id': 'Unknown',
            'original_file': 'Unknown'
        }

        # Extract recipient from metadata
        recipient_match = re.search(r'Recipient:\s*(.+)', content)
        if recipient_match:
            email_info['recipient'] = recipient_match.group(1).strip()

        # Extract subject from metadata
        subject_match = re.search(r'Subject:\s*(.+)', content)
        if subject_match:
            email_info['subject'] = subject_match.group(1).strip()

        # Extract original email ID
        email_id_match = re.search(r'Original_Email_ID:\s*(.+)', content)
        if email_id_match:
            email_info['original_email_id'] = email_id_match.group(1).strip()

        # Extract original file path
        original_file_match = re.search(r'Original_File:\s*(.+)', content)
        if original_file_match:
            email_info['original_file'] = original_file_match.group(1).strip()

        return email_info

    def handle_approved_plan(self, filepath: Path):
        """Handle approved plan - move to 4_Approved for execution"""
        filename = filepath.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"approved_{timestamp}_{filename}"
        dest_path = APPROVED_DIR / new_filename

        shutil.move(filepath, dest_path)
        self.log(f"Plan approved and moved to 4_Approved: {new_filename}")

        # Log the approval
        email_info = self.extract_email_info_from_plan(dest_path)
        approval_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "plan_file": str(dest_path),
            "recipient": email_info['recipient'],
            "subject": email_info['subject'],
            "status": "approved",
            "action": "moved_to_execution"
        }

        # Try to execute the plan immediately
        try:
            self.action_executor.scan_and_execute()
        except Exception as e:
            self.log(f"Error executing approved plan: {e}", "ERROR")

    def handle_rejected_plan(self, filepath: Path):
        """Handle rejected plan - move to Rejected folder"""
        filename = filepath.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"rejected_{timestamp}_{filename}"
        dest_path = REJECTED_DIR / new_filename

        shutil.move(filepath, dest_path)
        self.log(f"Plan rejected and moved to Rejected: {new_filename}")

        # Log the rejection
        email_info = self.extract_email_info_from_plan(dest_path)
        rejection_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "plan_file": str(dest_path),
            "recipient": email_info['recipient'],
            "subject": email_info['subject'],
            "status": "rejected",
            "action": "moved_to_rejected"
        }

    def scan_and_process_approvals(self):
        """Scan Pending_Approval folder and process approvals/rejections"""
        self.log("=== Starting Approval Scan ===", "SYSTEM")

        if not PENDING_APPROVAL_DIR.exists():
            self.log("Pending_Approval folder not found", "ERROR")
            return

        # Get all markdown files in Pending_Approval
        pending_files = list(PENDING_APPROVAL_DIR.glob("*.md"))

        if not pending_files:
            self.log("No pending approval files found")
            return

        self.log(f"Found {len(pending_files)} pending approval files")

        approved_count = 0
        rejected_count = 0
        pending_count = 0

        for file_path in pending_files:
            try:
                self.log(f"\nProcessing: {file_path.name}")

                status = self.check_approval_status(file_path)
                self.log(f"Status: {status}")

                if status == 'approved':
                    self.handle_approved_plan(file_path)
                    approved_count += 1
                elif status == 'rejected':
                    self.handle_rejected_plan(file_path)
                    rejected_count += 1
                else:
                    pending_count += 1
                    self.log(f"File still pending: {file_path.name}")

            except Exception as e:
                self.log(f"Error processing {file_path.name}: {e}", "ERROR")

        # Summary
        self.log("\n=== Approval Summary ===", "SYSTEM")
        self.log(f"Approved: {approved_count}")
        self.log(f"Rejected: {rejected_count}")
        self.log(f"Still pending: {pending_count}")

        return {
            "approved": approved_count,
            "rejected": rejected_count,
            "pending": pending_count
        }


def main():
    """Main function to run the approval handler"""
    print("\n[AI Employee - Approval Handler]")
    print("="*60)

    handler = ApprovalHandler()
    results = handler.scan_and_process_approvals()

    print("\n" + "="*60)
    print("[Approval scan complete!]")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()