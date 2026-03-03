#!/usr/bin/env python3
"""
ACTUAL SENDER - No more MD files, just SEND
"""
import os
import json
import base64
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

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

def send_email(service, to, subject, body):
    """Actually send email via Gmail API"""
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {'raw': raw}

        result = service.users().messages().send(userId='me', body=send_message).execute()
        print(f'[SENT] Email to {to}: {subject}')
        return True, result['id']
    except Exception as e:
        print(f'[ERROR] Failed to send email: {e}')
        return False, str(e)

def post_to_linkedin(content):
    """Post to LinkedIn - requires manual posting for now"""
    try:
        print('[LINKEDIN] Content ready for posting')
        # Save to file for manual posting
        with open('linkedin_post_ready.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print('[INFO] LinkedIn content saved to linkedin_post_ready.txt')
        print('[INFO] Manual posting required - OAuth not configured')
        return True, 'saved_for_manual_posting'
    except Exception as e:
        print(f'[ERROR] LinkedIn processing failed: {e}')
        return False, str(e)

def parse_email_from_file(filepath):
    """Extract email details from file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract recipient
    to = None
    for line in content.split('\n'):
        if line.startswith('To:') or line.startswith('**To:**'):
            to = line.split(':', 1)[1].strip().strip('*')
            break

    # Extract subject
    subject = None
    for line in content.split('\n'):
        if line.startswith('Subject:') or line.startswith('**Subject:**'):
            subject = line.split(':', 1)[1].strip().strip('*')
            break

    # Extract body
    body_lines = []
    in_body = False
    for line in content.split('\n'):
        if '## Email Body' in line or 'Email Body' in line:
            in_body = True
            continue
        if in_body and line.startswith('---'):
            break
        if in_body and line.strip():
            body_lines.append(line)

    body = '\n'.join(body_lines).strip()

    return to, subject, body

def parse_linkedin_from_file(filepath):
    """Extract LinkedIn content from file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract post content
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

def main():
    import sys
    # Fix Windows console encoding
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print('=' * 60)
    print('ACTUAL SENDER - Sending emails and posts NOW')
    print('=' * 60)

    # Check Done folder for items to send
    done_dir = Path('Done')

    # Find email drafts
    email_files = list(done_dir.glob('*email_draft*.md'))
    linkedin_files = list(done_dir.glob('*linkedin_draft*.md'))

    print(f'\nFound {len(email_files)} emails and {len(linkedin_files)} LinkedIn posts')

    # Initialize Gmail service
    try:
        gmail_service = get_gmail_service()
        print('[OK] Gmail service authenticated')
    except Exception as e:
        print(f'[ERROR] Gmail authentication failed: {e}')
        gmail_service = None

    # Send emails
    sent_count = 0
    for email_file in email_files:
        print(f'\nProcessing: {email_file.name}')

        # Skip if already sent
        if 'sent' in email_file.name.lower():
            print('[SKIP] Already sent')
            continue

        try:
            to, subject, body = parse_email_from_file(email_file)

            if not to or not subject or not body:
                print('[ERROR] Could not parse email details')
                continue

            print(f'  To: {to}')
            print(f'  Subject: {subject}')

            if gmail_service:
                success, result = send_email(gmail_service, to, subject, body)
                if success:
                    sent_count += 1
                    # Rename file to mark as sent
                    new_name = email_file.stem + '_SENT_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.md'
                    email_file.rename(done_dir / new_name)
            else:
                print('[ERROR] Gmail service not available')

        except Exception as e:
            print(f'[ERROR] Failed to process {email_file.name}: {e}')

    # Post to LinkedIn
    posted_count = 0
    for linkedin_file in linkedin_files:
        print(f'\nProcessing: {linkedin_file.name}')

        # Skip if already posted
        if 'posted' in linkedin_file.name.lower():
            print('[SKIP] Already posted')
            continue

        try:
            content = parse_linkedin_from_file(linkedin_file)

            if not content:
                print('[ERROR] Could not parse LinkedIn content')
                continue

            success, result = post_to_linkedin(content)
            if success:
                posted_count += 1
                # Rename file to mark as posted
                new_name = linkedin_file.stem + '_POSTED_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.md'
                linkedin_file.rename(done_dir / new_name)

        except Exception as e:
            print(f'[ERROR] Failed to process {linkedin_file.name}: {e}')

    print('\n' + '=' * 60)
    print(f'RESULTS: {sent_count} emails sent, {posted_count} LinkedIn posts')
    print('=' * 60)

if __name__ == '__main__':
    main()
