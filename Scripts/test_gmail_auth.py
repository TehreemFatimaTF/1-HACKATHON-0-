#!/usr/bin/env python3
"""Test Gmail authentication and email fetching"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from watcher_gmail import GmailWatcher

def main():
    print("="*60)
    print("Gmail Authentication & Email Fetch Test")
    print("="*60)

    watcher = GmailWatcher()

    print("\n[1/3] Authenticating with Gmail API...")
    if not watcher.authenticate():
        print("[ERROR] Authentication failed!")
        return False

    print("[OK] Authentication successful!")

    print("\n[2/3] Fetching unread emails...")
    watcher.fetch_new_emails()

    print("\n[3/3] Checking Needs_Action folder...")
    needs_action_dir = os.path.join(os.path.dirname(__file__), "Needs_Action")
    if os.path.exists(needs_action_dir):
        files = [f for f in os.listdir(needs_action_dir) if f.startswith("Gmail_")]
        print(f"[OK] Found {len(files)} Gmail files in Needs_Action folder")
        if files:
            print("\nRecent Gmail files:")
            for f in files[-5:]:
                print(f"  - {f}")
    else:
        print("[WARNING] Needs_Action folder not found")

    print("\n" + "="*60)
    print("[OK] Gmail integration test complete!")
    print("="*60)

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
