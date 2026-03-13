"""
Extend Facebook Access Token to Long-Lived Token (60 days)
This script converts a short-lived token to a long-lived token
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extend_facebook_token():
    """Extend short-lived token to long-lived token (60 days)"""
    print("\n" + "="*60)
    print("FACEBOOK TOKEN EXTENSION")
    print("="*60)

    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    short_token = os.getenv("FACEBOOK_ACCESS_TOKEN")

    if not all([app_id, app_secret, short_token]):
        print("\n[ERROR] Missing credentials in .env file")
        print("   Required: FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_ACCESS_TOKEN")
        return None

    try:
        print("\n[*] Extending access token to 60 days...")

        # Call Facebook API to extend token
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "access_token" not in data:
            print("\n[ERROR] Failed to extend token")
            print(f"   Response: {data}")
            return None

        long_lived_token = data["access_token"]
        expires_in = data.get("expires_in", "Unknown")

        print(f"\n[SUCCESS] Token extended!")
        print(f"   Expires in: {expires_in} seconds (~{int(expires_in)//86400} days)")
        print(f"   New token: {long_lived_token[:30]}...")

        # Update .env file
        print("\n[*] Updating .env file...")
        update_env_file(long_lived_token)

        # Now get page token
        print("\n[*] Getting page access token...")
        from get_page_access_token import get_page_access_token
        get_page_access_token()

        return long_lived_token

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Failed to extend token: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        return None


def update_env_file(token):
    """Update .env file with new token"""
    try:
        env_path = ".env"

        # Read current .env content
        with open(env_path, 'r') as f:
            lines = f.readlines()

        # Update FACEBOOK_ACCESS_TOKEN
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("FACEBOOK_ACCESS_TOKEN="):
                lines[i] = f"FACEBOOK_ACCESS_TOKEN={token}\n"
                updated = True
                break

        if not updated:
            lines.append(f"\nFACEBOOK_ACCESS_TOKEN={token}\n")

        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(lines)

        print(f"[SUCCESS] Updated .env file with long-lived token")

    except Exception as e:
        print(f"\n[ERROR] Failed to update .env: {str(e)}")
        print(f"\n[MANUAL STEP] Please update your .env file:")
        print(f"   FACEBOOK_ACCESS_TOKEN={token}")


if __name__ == "__main__":
    print("\n[INFO] This script extends your Facebook access token to 60 days")
    print("       You need a valid short-lived token in your .env file first")
    print("\n[STEPS]")
    print("   1. Get a new token from: https://developers.facebook.com/tools/explorer/")
    print("   2. Update FACEBOOK_ACCESS_TOKEN in .env file")
    print("   3. Run this script to extend it to 60 days")
    print("\n" + "="*60)

    token = extend_facebook_token()

    print("\n" + "="*60)
    if token:
        print("[SUCCESS] Token extended to 60 days!")
        print("\n[NEXT STEPS]")
        print("   1. Test: python demo_facebook_auto.py")
        print("   2. Your token will now last 60 days")
    else:
        print("[FAILED] Could not extend token")
        print("   Make sure you have a valid token in .env first")
    print("="*60 + "\n")
