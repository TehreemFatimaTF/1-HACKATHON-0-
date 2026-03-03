import time
import os
import pickle
import ssl
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX_DIR = os.path.join(BASE_DIR, "Inbox")  # Keep for backward compatibility
NEEDS_ACTION_DIR = os.path.join(BASE_DIR, "Needs_Action")
LOGS_DIR = os.path.join(BASE_DIR, "Logs")
TOKEN_FILE = os.path.join(BASE_DIR, "token.pickle")
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Ensure directories exist
for directory in [INBOX_DIR, NEEDS_ACTION_DIR, LOGS_DIR]:  # Added NEEDS_ACTION_DIR
    if not os.path.exists(directory):
        os.makedirs(directory)


class GmailWatcher:
    """Monitors Gmail inbox for new emails"""

    def __init__(self):
        self.running = False
        self.log_file = os.path.join(LOGS_DIR, "watcher_gmail.log")
        self.check_interval = 300
        self.service = None
        self.processed_emails = set()

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [GMAIL] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def authenticate(self):
        creds = None

        # Load existing token
        if os.path.exists(TOKEN_FILE):
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
                    # Refresh using standard Request object
                    creds.refresh(Request())
                except Exception as e:
                    self.log(f"Token refresh failed: {e}. Re-authenticating...", "WARNING")
                    # Delete corrupted token and force re-auth
                    if os.path.exists(TOKEN_FILE):
                        os.remove(TOKEN_FILE)
                    creds = None

            if not creds:
                if not os.path.exists(CREDENTIALS_FILE):
                    self.log("credentials.json not found", "ERROR")
                    self.log("Please follow the instructions in GMAIL_AUTH_SETUP.md to set up Gmail authentication", "ERROR")
                    self.log("You need to create a Google Cloud project and download credentials.json", "ERROR")
                    return False

                self.log("Starting OAuth flow...")

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE,
                        SCOPES
                    )

                    # Run local server with error handling
                    creds = flow.run_local_server(port=8080, prompt='consent')
                except Exception as e:
                    self.log(f"OAuth flow failed: {e}", "ERROR")
                    return False

            # Save token
            try:
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
                self.log("Authentication successful - token saved")
            except Exception as e:
                self.log(f"Warning: Could not save token: {e}", "WARNING")

        try:
            # Build service with credentials only (http is mutually exclusive)
            self.service = build('gmail', 'v1', credentials=creds)
            self.log("Gmail API service initialized")
            return True
        except Exception as e:
            self.log(f"Failed to build Gmail service: {e}", "ERROR")
            return False

    def get_email_body(self, message):
        try:
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                for part in parts:
                    if part['mimeType'] in ['text/plain', 'text/html']:
                        data = part['body'].get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                data = message['payload']['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
        except Exception as e:
            self.log(f"Error extracting body: {e}", "ERROR")

        return "Could not extract email body"

    def create_inbox_file(self, sender, subject, body, email_id, date):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        clean_subject = "".join(c for c in subject[:30] if c.isalnum() or c in " -_")
        filename = f"Gmail_{timestamp}_{clean_subject}.md"
        filepath = os.path.join(NEEDS_ACTION_DIR, filename)

        metadata = f"""---
Source: Gmail
Email_ID: {email_id}
From: {sender}
Subject: {subject}
Detected_At: {timestamp}
Status: Unprocessed
Tags: #email
---

"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(metadata)
            f.write(f"# Email: {subject}\n\n")
            f.write(f"**From:** {sender}\n\n")
            f.write(f"**Date:** {date}\n\n")
            f.write(f"**Received:** {timestamp}\n\n")
            f.write("---\n\n")
            f.write(body)

        self.log(f"Created: {filename}")
        return filepath

    def fetch_new_emails(self):
        if not self.service:
            self.log("Gmail service not initialized", "ERROR")
            return

        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                self.log("No new emails")
                return

            new_count = 0

            for msg in messages:
                msg_id = msg['id']

                if msg_id in self.processed_emails:
                    continue

                message = self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()

                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

                body = self.get_email_body(message)
                self.create_inbox_file(sender, subject, body, msg_id, date)

                self.processed_emails.add(msg_id)
                new_count += 1

            if new_count > 0:
                self.log(f"Processed {new_count} new emails")

        except ssl.SSLError as e:
            self.log(f"SSL Error: {e}. Attempting to re-authenticate...", "ERROR")
            # Try to re-authenticate on SSL errors
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            self.authenticate()
        except Exception as e:
            self.log(f"Error fetching emails: {e}", "ERROR")

    def start(self):
        self.running = True
        self.log("=== Gmail Watcher Starting ===", "SYSTEM")
        self.log(f"Check interval: {self.check_interval} seconds")
        self.log(f"Output to: {INBOX_DIR}")

        if not self.authenticate():
            self.log("Authentication failed", "ERROR")
            self.running = False
            return

        self.log("Gmail API authenticated successfully")

        try:
            while self.running:
                self.fetch_new_emails()
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.log("=== Shutting down Gmail watcher ===", "SYSTEM")
        self.running = False


if __name__ == "__main__":
    watcher = GmailWatcher()
    watcher.start()
