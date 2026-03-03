#!/usr/bin/env python3
"""
Process files from Needs_Action folder and create plans with approval/rejection options.
This script reads email files from the Needs_Action folder, creates plans using Claude,
and places them in Pending_Approval folder with checkboxes for approval/rejection.
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

# Note: Claude MCP integration would be handled by Claude itself using MCP tools
# This script prepares files for Claude processing with proper metadata
from src.action_executor import ActionExecutor

# Configuration
BASE_DIR = Path(__file__).parent.parent
NEEDS_ACTION_DIR = BASE_DIR / "Needs_Action"
PLANS_DIR = BASE_DIR / "Plans"  # Plans create hote hain yahan
PENDING_APPROVAL_DIR = BASE_DIR / "Pending_Approval"  # Plans yahan move hote hain
DONE_DIR = BASE_DIR / "Done"
LOGS_DIR = BASE_DIR / "Logs"

# Create directories if they don't exist
for directory in [NEEDS_ACTION_DIR, PLANS_DIR, PENDING_APPROVAL_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)


class ProcessNeedsAction:
    """Process files from Needs_Action and create plans for approval"""

    def __init__(self):
        self.log_file = LOGS_DIR / "process_needs_action.log"
        self.claude_client = None  # We'll use Claude MCP tools when available

    def log(self, message, level="INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [PROCESS_NA] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def extract_email_info(self, filepath: Path) -> Dict[str, Any]:
        """Extract email information from the file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        email_info = {
            'subject': 'Unknown',
            'sender': 'Unknown',
            'body': '',
            'email_id': 'Unknown',
            'original_file': str(filepath)
        }

        # Extract subject and sender from the metadata
        subject_match = re.search(r'Subject:\s*(.+)', content)
        if subject_match:
            email_info['subject'] = subject_match.group(1).strip()

        sender_match = re.search(r'From:\s*(.+)', content)
        if sender_match:
            email_info['sender'] = sender_match.group(1).strip()

        # Extract email body after the metadata sections
        parts = content.split('---')
        if len(parts) >= 3:
            # Look for the body section after the second ---
            body_section = parts[2] if len(parts) > 2 else ''
            email_info['body'] = body_section.strip()

        # Extract email ID if available
        email_id_match = re.search(r'Email_ID:\s*(.+)', content)
        if email_id_match:
            email_info['email_id'] = email_id_match.group(1).strip()

        return email_info

    def create_plan_with_claude(self, email_info: Dict[str, Any]) -> str:
        """Create a plan using Claude based on email content"""
        # This is a mock implementation - in reality we would use Claude MCP tools
        # For now, we'll return a template plan that includes approval options

        plan_content = f"""---
Source: AI_Planning_Engine
Original_Email_ID: {email_info['email_id']}
Original_File: {email_info['original_file']}
Status: Pending_Approval
Created_At: {datetime.now().strftime('%Y-%m-%d_%H%M%S')}
Action_Type: Email_Response
Recipient: {email_info['sender']}
Subject: Re: {email_info['subject']}
---

# Plan for Email: {email_info['subject']}

## Original Email Content:
**From:** {email_info['sender']}
**Subject:** {email_info['subject']}

{email_info['body']}

## Suggested Response Plan:

### Action: Send Email Response

**Recipient:** {email_info['sender']}
**Subject:** Re: {email_info['subject']}

**Body:**
Thank you for your email regarding "{email_info['subject']}". We have reviewed your request and will get back to you shortly with a detailed response.

Best regards,
AI Employee

---

## Approval Options

- [ ] **Approve** - Execute this plan and send the email response
- [ ] **Reject** - Reject this plan and mark as handled

**Reviewer Notes:**
- Review the suggested response before approving
- Modify if needed before approval
- Contact supervisor if unsure about the response

"""
        return plan_content

    def create_plan_in_plans_folder(self, original_file: Path, plan_content: str):
        """Create plan in Plans/ folder first"""
        # Create a new filename based on the original
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        original_name = original_file.stem
        new_filename = f"plan_{timestamp}_{original_name}.md"
        new_filepath = PLANS_DIR / new_filename

        with open(new_filepath, 'w', encoding='utf-8') as f:
            f.write(plan_content)

        self.log(f"Created plan in Plans/: {new_filename}")
        return new_filepath

    def move_to_pending_approval(self, plan_file: Path):
        """Move plan from Plans/ to Pending_Approval/ folder"""
        new_filepath = PENDING_APPROVAL_DIR / plan_file.name

        # Move the file
        plan_file.rename(new_filepath)

        self.log(f"Moved to Pending_Approval/: {plan_file.name}")
        return new_filepath

    def process_needs_action_files(self):
        """Process all files in Needs_Action folder"""
        self.log("=== Starting Process Needs Action ===", "SYSTEM")

        if not NEEDS_ACTION_DIR.exists():
            self.log("Needs_Action folder not found", "ERROR")
            return

        # Get all markdown files in Needs_Action
        needs_action_files = list(NEEDS_ACTION_DIR.glob("*.md"))

        if not needs_action_files:
            self.log("No files in Needs_Action folder to process")
            return

        self.log(f"Found {len(needs_action_files)} files to process")

        processed_count = 0

        for file_path in needs_action_files:
            try:
                self.log(f"\nProcessing: {file_path.name}")

                # Extract email info
                email_info = self.extract_email_info(file_path)

                # Create plan with Claude
                plan_content = self.create_plan_with_claude(email_info)

                # Step 1: Create plan in Plans/ folder
                plan_file = self.create_plan_in_plans_folder(file_path, plan_content)

                # Step 2: Move plan to Pending_Approval/ folder
                self.move_to_pending_approval(plan_file)

                # Step 3: Mark original file as processed
                timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                processed_suffix = f"_processed_{timestamp}"
                processed_file = file_path.parent / f"{file_path.stem}{processed_suffix}{file_path.suffix}"
                file_path.rename(processed_file)
                self.log(f"Marked original file as processed: {processed_file.name}")

                processed_count += 1

            except Exception as e:
                self.log(f"Error processing {file_path.name}: {e}", "ERROR")

        # Summary
        self.log("\n=== Processing Summary ===", "SYSTEM")
        self.log(f"Successfully processed: {processed_count}")

        return processed_count


def main():
    """Main function to run the process"""
    print("\n[AI Employee - Process Needs Action]")
    print("="*60)

    processor = ProcessNeedsAction()
    results = processor.process_needs_action_files()

    print("\n" + "="*60)
    print("[Process complete!]")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()