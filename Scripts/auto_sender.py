#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO SENDER - Monitors 4_Approved and ACTUALLY sends
No more MD files, just REAL ACTIONS
"""
import os
import sys
import io
import json
import base64
import time
import shutil
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Directories
APPROVED_DIR = Path('4_Approved')
DONE_DIR = Path('Done')
LOGS_DIR = Path('Logs')

def log(message):
    """Simple logging"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{timestamp}] {message}')

def get_gmail_service():
    """Get authenticated Gmail service"""
    creds = None
    token_file = 'token.pickle'

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Look for any client_secret_*.json file
            import glob
            client_secret_files = glob.glob('client_secret_*.json')
            if not client_secret_files:
                raise FileNotFoundError("No client_secret_*.json file found. Please download from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_files[0],
                SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def send_email_now(service, to, subject, body):
    """ACTUALLY send email via Gmail API"""
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {'raw': raw}

        result = service.users().messages().send(userId='me', body=send_message).execute()
        log(f'[OK] EMAIL SENT to {to}: {subject}')
        return True, result['id']
    except Exception as e:
        log(f'[ERROR] EMAIL FAILED: {e}')
        return False, str(e)

def parse_email_file(filepath):
    """Extract email details from approved file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    to = None
    subject = None
    body_lines = []

    lines = content.split('\n')
    in_body = False

    for i, line in enumerate(lines):
        # Extract To
        if 'To:' in line or 'Recipient:' in line:
            parts = line.split(':', 1)
            if len(parts) > 1:
                to = parts[1].strip().strip('*').strip()

        # Extract Subject
        if 'Subject:' in line and not in_body:
            parts = line.split(':', 1)
            if len(parts) > 1:
                subject = parts[1].strip().strip('*').strip()

        # Extract Body
        if '## Email Body' in line or 'Email Body' in line:
            in_body = True
            continue

        if in_body:
            if line.startswith('---') or line.startswith('##'):
                break
            if line.strip():
                body_lines.append(line)

    body = '\n'.join(body_lines).strip()
    return to, subject, body

def parse_linkedin_file(filepath):
    """Extract LinkedIn content"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    post_lines = []
    in_content = False

    for line in content.split('\n'):
        if '## Post Content' in line:
            in_content = True
            continue
        if in_content and line.startswith('---'):
            break
        if in_content and line.strip():
            post_lines.append(line)

    return '\n'.join(post_lines).strip()

def process_approved_folder(gmail_service):
    """Process all files in 4_Approved folder"""
    if not APPROVED_DIR.exists():
        log('4_Approved folder not found')
        return

    files = list(APPROVED_DIR.glob('*.md'))
    if not files:
        log('No files in 4_Approved folder')
        return

    log(f'Found {len(files)} files to process')

    for file in files:
        log(f'\nProcessing: {file.name}')

        try:
            # Determine file type
            if 'email' in file.name.lower():
                # Process email
                to, subject, body = parse_email_file(file)

                if not to or not subject:
                    log('[ERROR] Could not parse email details')
                    continue

                log(f'  To: {to}')
                log(f'  Subject: {subject}')

                # ACTUALLY SEND
                success, result = send_email_now(gmail_service, to, subject, body)

                if success:
                    # Move to Done with SENT marker
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    new_name = file.stem + f'_SENT_{timestamp}.md'
                    dest = DONE_DIR / new_name
                    shutil.move(str(file), str(dest))
                    log(f'[OK] Moved to Done: {new_name}')

            elif 'linkedin' in file.name.lower():
                # Process LinkedIn
                content = parse_linkedin_file(file)

                if not content:
                    log('[ERROR] Could not parse LinkedIn content')
                    continue

                # Save for manual posting (OAuth not configured)
                linkedin_file = Path('linkedin_post_ready.txt')
                with open(linkedin_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                log('[OK] LinkedIn content saved to linkedin_post_ready.txt')
                log('  (Manual posting required - OAuth not configured)')

                # Move to Done
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_name = file.stem + f'_READY_{timestamp}.md'
                dest = DONE_DIR / new_name
                shutil.move(str(file), str(dest))
                log(f'[OK] Moved to Done: {new_name}')

            else:
                # Unknown type - just move to Done
                log('[INFO] Unknown file type - moving to Done')
                dest = DONE_DIR / file.name
                shutil.move(str(file), str(dest))

        except Exception as e:
            log(f'[ERROR] processing {file.name}: {e}')

def watch_mode():
    """Continuously watch 4_Approved folder"""
    log('=' * 60)
    log('AUTO SENDER - Watching 4_Approved folder')
    log('Press Ctrl+C to stop')
    log('=' * 60)

    # Initialize Gmail
    try:
        gmail_service = get_gmail_service()
        log('[OK] Gmail authenticated')
    except Exception as e:
        log(f'[ERROR] Gmail authentication failed: {e}')
        gmail_service = None

    while True:
        try:
            process_approved_folder(gmail_service)
            time.sleep(10)  # Check every 10 seconds
        except KeyboardInterrupt:
            log('\nStopping auto sender...')
            break
        except Exception as e:
            log(f'[ERROR] Error in watch loop: {e}')
            time.sleep(10)

def run_once():
    """Run once and exit"""
    log('=' * 60)
    log('AUTO SENDER - Processing 4_Approved folder')
    log('=' * 60)

    # Initialize Gmail
    try:
        gmail_service = get_gmail_service()
        log('[OK] Gmail authenticated')
    except Exception as e:
        log(f'[ERROR] Gmail authentication failed: {e}')
        return

    process_approved_folder(gmail_service)
    log('\n' + '=' * 60)
    log('Processing complete')
    log('=' * 60)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--watch':
        watch_mode()
    else:
        run_once()
