"""
Get Instagram Business Account ID
This script retrieves your Instagram Business Account ID linked to your Facebook Page
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_instagram_account_id():
    """Get Instagram Business Account ID from Facebook Page"""
    print("\n" + "="*60)
    print("INSTAGRAM BUSINESS ACCOUNT ID RETRIEVAL")
    print("="*60)

    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")

    if not access_token or not page_id:
        print("\n[ERROR] Missing Facebook credentials in .env")
        return None

    try:
        # Get Instagram Business Account linked to the page
        print(f"\n[*] Checking Facebook Page {page_id} for linked Instagram account...")
        url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {
            "fields": "instagram_business_account",
            "access_token": access_token
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "instagram_business_account" not in data:
            print("\n[WARNING] No Instagram Business Account linked to this Facebook Page")
            print("\n[INSTRUCTIONS] To link Instagram:")
            print("   1. Go to your Facebook Page settings")
            print("   2. Click 'Instagram' in the left menu")
            print("   3. Click 'Connect Account'")
            print("   4. Log in to your Instagram Business account")
            print("   5. Make sure it's a Business or Creator account (not Personal)")
            print("\n   Then run this script again.")
            return None

        instagram_account_id = data["instagram_business_account"]["id"]

        print(f"\n[SUCCESS] Instagram Business Account found!")
        print(f"   Instagram Account ID: {instagram_account_id}")

        # Get Instagram account details
        print("\n[*] Fetching Instagram account details...")
        url = f"https://graph.facebook.com/v18.0/{instagram_account_id}"
        params = {
            "fields": "username,name,profile_picture_url,followers_count,follows_count,media_count",
            "access_token": access_token
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        ig_data = response.json()

        print(f"\n[INSTAGRAM ACCOUNT DETAILS]")
        print(f"   Username: @{ig_data.get('username', 'N/A')}")
        print(f"   Name: {ig_data.get('name', 'N/A')}")
        print(f"   Followers: {ig_data.get('followers_count', 'N/A')}")
        print(f"   Following: {ig_data.get('follows_count', 'N/A')}")
        print(f"   Posts: {ig_data.get('media_count', 'N/A')}")

        # Update .env file
        print("\n[*] Updating .env file...")
        update_env_file(instagram_account_id, access_token)

        return instagram_account_id

    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] Failed to get Instagram account: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        return None


def update_env_file(instagram_account_id, access_token):
    """Update .env file with Instagram credentials"""
    try:
        env_path = ".env"

        # Read current .env content
        with open(env_path, 'r') as f:
            lines = f.readlines()

        # Update Instagram credentials
        account_id_updated = False
        token_updated = False

        for i, line in enumerate(lines):
            if line.startswith("INSTAGRAM_BUSINESS_ACCOUNT_ID="):
                lines[i] = f"INSTAGRAM_BUSINESS_ACCOUNT_ID={instagram_account_id}\n"
                account_id_updated = True
            elif line.startswith("INSTAGRAM_ACCESS_TOKEN="):
                lines[i] = f"INSTAGRAM_ACCESS_TOKEN={access_token}\n"
                token_updated = True

        # If not found, append them
        if not account_id_updated:
            lines.append(f"\nINSTAGRAM_BUSINESS_ACCOUNT_ID={instagram_account_id}\n")
        if not token_updated:
            lines.append(f"INSTAGRAM_ACCESS_TOKEN={access_token}\n")

        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(lines)

        print(f"[SUCCESS] Updated .env file with Instagram credentials")
        print("\n[NEXT STEPS]")
        print("   1. Run: python test_instagram_integration.py")
        print("   2. Test posting to Instagram")

    except Exception as e:
        print(f"\n[ERROR] Failed to update .env: {str(e)}")
        print(f"\n[MANUAL STEP] Please update your .env file:")
        print(f"   INSTAGRAM_BUSINESS_ACCOUNT_ID={instagram_account_id}")
        print(f"   INSTAGRAM_ACCESS_TOKEN={access_token}")


if __name__ == "__main__":
    account_id = get_instagram_account_id()

    print("\n" + "="*60)
    if account_id:
        print("[SUCCESS] Instagram integration ready!")
    else:
        print("[INFO] Instagram not linked yet")
        print("   Follow the instructions above to link your Instagram account")
    print("="*60 + "\n")
