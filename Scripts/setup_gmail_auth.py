#!/usr/bin/env python3
"""
Gmail Authentication Setup Helper

This script helps set up Gmail API authentication for the AI Employee system.
It will guide you through the authentication process and create the necessary token file.
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# File paths
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"

def authenticate_gmail():
    """Authenticate with Gmail API and save credentials"""

    creds = None

    # Load existing token
    if os.path.exists(TOKEN_FILE):
        print(f"Loading existing token from {TOKEN_FILE}")
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, go through OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                print("Re-authenticating...")
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                creds = None

        if not creds:
            # Check if credentials file exists
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"ERROR: {CREDENTIALS_FILE} not found!")
                print("\nTo fix this:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select existing one")
                print("3. Enable the Gmail API")
                print("4. Create OAuth 2.0 credentials for a Desktop application")
                print("5. Download the JSON file and rename it to 'credentials.json'")
                print("6. Place 'credentials.json' in this directory")
                print("\nFor detailed instructions, see GMAIL_AUTH_SETUP.md")
                return False

            print("Starting OAuth flow for Gmail API...")
            print("A browser window will open for authentication.")

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE,
                    SCOPES
                )

                # Run local server for OAuth
                creds = flow.run_local_server(
                    port=8080,
                    prompt='consent',
                    authorization_prompt_message='Please visit this URL to authorize the application:'
                )

                print("Authentication successful!")

            except Exception as e:
                print(f"OAuth flow failed: {e}")
                return False

        # Save the credentials for next run
        try:
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            print(f"Credentials saved to {TOKEN_FILE}")
        except Exception as e:
            print(f"Warning: Could not save token: {e}")

    # Test the Gmail API connection
    try:
        service = build('gmail', 'v1', credentials=creds)

        # Try to fetch basic profile info
        profile = service.users().getProfile(userId='me').execute()
        print(f"Successfully connected to Gmail API!")
        print(f"Authenticated as: {profile.get('emailAddress', 'Unknown')}")

        # Check for unread emails as a test
        results = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=1
        ).execute()

        messages = results.get('messages', [])
        print(f"Test successful: Found {len(messages)} unread email(s)")

        return True

    except Exception as e:
        print(f"Failed to build Gmail service: {e}")
        return False

if __name__ == "__main__":
    print("AI Employee Gmail Authentication Setup")
    print("=" * 40)

    success = authenticate_gmail()

    if success:
        print("\nSetup complete! You can now run the Gmail watcher.")
        print("The token has been saved and will be used for future runs.")
    else:
        print("\nSetup failed. Please follow the instructions in GMAIL_AUTH_SETUP.md")