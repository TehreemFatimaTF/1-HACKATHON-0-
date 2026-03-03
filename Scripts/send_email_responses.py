#!/usr/bin/env python3
"""
Email Response Sender
This script sends email responses when plans are approved.
It uses the Gmail API to send emails based on approved plans.
"""

import os
import pickle
import base64
from datetime import datetime
from pathlib import Path
import sys
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Configuration
BASE_DIR = Path(__file__).parent.parent  # Project root (not Scripts/)
APPROVED_DIR = BASE_DIR / "Approved"  # Changed from 4_Approved to Approved
DONE_DIR = BASE_DIR / "Done"
LOGS_DIR = BASE_DIR / "Logs"
TOKEN_FILE = BASE_DIR / "token.pickle"
CREDENTIALS_FILE = BASE_DIR / "credentials.json"

# Create directories if they don't exist
for directory in [APPROVED_DIR, DONE_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)


class EmailResponseSender:
    """Send email responses based on approved plans"""

    def __init__(self):
        self.log_file = LOGS_DIR / "email_response_sender.log"
        self.service = None
        self.authenticate()

    def log(self, message, level="INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [EMAIL_SENDER] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load existing token
        if TOKEN_FILE.exists():
            try:
                with open(TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                self.log(f"Error loading token: {e}. Will re-authenticate.", "WARNING")
                creds = None

        # If no valid credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.log("Refreshing expired token...")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.log(f"Token refresh failed: {e}. Re-authenticating...", "WARNING")
                    # Delete corrupted token and force re-auth
                    if TOKEN_FILE.exists():
                        TOKEN_FILE.unlink()
                    creds = None

            if not creds:
                if not CREDENTIALS_FILE.exists():
                    self.log("credentials.json not found", "ERROR")
                    self.log("Please download credentials.json from Google Cloud Console", "ERROR")
                    return False

                self.log("Authentication required - please run Gmail watcher first to set up credentials", "ERROR")
                return False

            # Save token
            try:
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
                self.log("Authentication successful - token saved")
            except Exception as e:
                self.log(f"Warning: Could not save token: {e}", "WARNING")

        try:
            # Build service with credentials
            self.service = build('gmail', 'v1', credentials=creds)
            self.log("Gmail API service initialized")
            return True
        except Exception as e:
            self.log(f"Failed to build Gmail service: {e}", "ERROR")
            return False

    def extract_plan_info(self, filepath: Path) -> dict:
        """Extract plan information from the file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        plan_info = {
            'recipient': 'Unknown',
            'subject': 'Unknown',
            'body': '',
            'original_file': str(filepath)
        }

        # Extract recipient
        recipient_match = re.search(r'Recipient:\s*(.+)', content)
        if recipient_match:
            plan_info['recipient'] = recipient_match.group(1).strip()

        # Extract subject
        subject_match = re.search(r'Subject:\s*(.+)', content)
        if subject_match:
            plan_info['subject'] = subject_match.group(1).strip()

        # Extract body (try to find the response section)
        # Look for common patterns indicating the response body
        body_patterns = [
            r'\*\*Response:\*\*\s*(.+?)(?=\n\s*-{3}|\n\s*\*{2}|$)',
            r'### Action: Send Email Response.*?Body:\s*(.+?)(?=\n\s*-{3}|\n\s*\*{2}|$)',
            r'### Action: Send Email Response.*?(?:\*\*Body:\*\*|\n)\s*(.+?)(?=\n\s*-{3}|\n\s*\*{2}|$)',
            r'(?:Response:|Body:)\s*(.+?)(?=\n\s*-{3}|\n\s*\*{2}|$)',
        ]

        for pattern in body_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                plan_info['body'] = match.group(1).strip()
                break

        # If no body found yet, use everything after the main sections
        if not plan_info['body']:
            parts = content.split('---')
            if len(parts) >= 3:
                body_section = parts[2]
                # Look for the response section more specifically
                response_match = re.search(r'Dear.*?(?=##|\n-{3}|$)', body_section, re.DOTALL)
                if response_match:
                    plan_info['body'] = response_match.group(0).strip()
                else:
                    plan_info['body'] = body_section.strip()

        return plan_info

    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Send an email using Gmail API"""
        try:
            # Create message
            message = MIMEText(body)
            message['to'] = recipient
            message['subject'] = subject

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send email
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            self.log(f"Email sent successfully to {recipient}")
            self.log(f"Message ID: {sent_message['id']}")
            return True

        except Exception as e:
            self.log(f"Error sending email to {recipient}: {e}", "ERROR")
            return False

    def process_approved_plans(self):
        """Process all approved plans and send emails"""
        self.log("=== Starting Email Response Processing ===", "SYSTEM")

        if not APPROVED_DIR.exists():
            self.log("4_Approved folder not found", "ERROR")
            return

        # Get all approved plan files
        approved_files = list(APPROVED_DIR.glob("*.md"))

        if not approved_files:
            self.log("No approved plans found to process")
            return

        self.log(f"Found {len(approved_files)} approved plans to process")

        sent_count = 0
        failed_count = 0

        for plan_file in approved_files:
            try:
                self.log(f"\nProcessing: {plan_file.name}")

                # Extract plan information
                plan_info = self.extract_plan_info(plan_file)

                # Validate required fields
                if plan_info['recipient'] == 'Unknown' or plan_info['subject'] == 'Unknown':
                    self.log(f"Missing recipient or subject in {plan_file.name}", "WARNING")
                    continue

                # Send the email response
                success = self.send_email(
                    recipient=plan_info['recipient'],
                    subject=plan_info['subject'],
                    body=plan_info['body']
                )

                if success:
                    # Move to Done folder
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_filename = f"sent_{timestamp}_{plan_file.name}"
                    dest_path = DONE_DIR / new_filename
                    shutil.move(plan_file, dest_path)
                    self.log(f"Plan moved to Done: {new_filename}")
                    sent_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                self.log(f"Error processing {plan_file.name}: {e}", "ERROR")
                failed_count += 1

        # Summary
        self.log("\n=== Email Response Summary ===", "SYSTEM")
        self.log(f"Emails sent: {sent_count}")
        self.log(f"Failed: {failed_count}")

        return {"sent": sent_count, "failed": failed_count}


def main():
    """Main function to run the email response sender"""
    print("\n[AI Employee - Email Response Sender]")
    print("="*60)

    sender = EmailResponseSender()
    results = sender.process_approved_plans()

    print("\n" + "="*60)
    print("[Email response processing complete!]")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Import shutil for file operations
    import shutil
    main()