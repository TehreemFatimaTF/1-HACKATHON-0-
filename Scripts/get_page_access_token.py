"""
Get Facebook Page Access Token
This script retrieves the page access token needed for posting
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_page_access_token():
    """Get page access token from user token"""
    print("\n" + "="*60)
    print("FACEBOOK PAGE ACCESS TOKEN RETRIEVAL")
    print("="*60)

    user_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")

    if not user_token:
        print("\n[ERROR] FACEBOOK_ACCESS_TOKEN not found in .env")
        return None

    try:
        # Get all pages managed by this user
        print("\n[*] Fetching pages and their access tokens...")
        url = "https://graph.facebook.com/v18.0/me/accounts"
        params = {
            "access_token": user_token
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "data" not in data or len(data["data"]) == 0:
            print("\n[ERROR] No pages found!")
            print("   Make sure your access token has 'pages_manage_posts' permission")
            return None

        print(f"\n[SUCCESS] Found {len(data['data'])} page(s):\n")

        # Find the page we're looking for
        target_page = None
        for page in data["data"]:
            page_name = page.get("name")
            page_id_found = page.get("id")
            page_token = page.get("access_token")

            print(f"   - {page_name} (ID: {page_id_found})")

            if page_id and page_id_found == page_id:
                target_page = page
            elif not page_id:
                target_page = page  # Use first page if no specific page ID

        if not target_page:
            print(f"\n[ERROR] Page with ID {page_id} not found")
            return None

        page_token = target_page.get("access_token")
        page_name = target_page.get("name")
        page_id_found = target_page.get("id")

        print("\n" + "="*60)
        print("[SUCCESS] Page Access Token Retrieved!")
        print("="*60)
        print(f"\nPage Name: {page_name}")
        print(f"Page ID: {page_id_found}")
        print(f"Page Token: {page_token[:30]}...")

        # Update .env file
        print("\n[*] Updating .env file...")
        update_env_file(page_token, page_id_found)

        return page_token

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Failed to get page token: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        return None


def update_env_file(page_token, page_id):
    """Update .env file with page access token"""
    try:
        env_path = ".env"

        # Read current .env content
        with open(env_path, 'r') as f:
            lines = f.readlines()

        # Update FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID
        token_updated = False
        page_id_updated = False

        for i, line in enumerate(lines):
            if line.startswith("FACEBOOK_ACCESS_TOKEN="):
                lines[i] = f"FACEBOOK_ACCESS_TOKEN={page_token}\n"
                token_updated = True
            elif line.startswith("FACEBOOK_PAGE_ID="):
                lines[i] = f"FACEBOOK_PAGE_ID={page_id}\n"
                page_id_updated = True

        # If not found, append them
        if not token_updated:
            lines.append(f"\nFACEBOOK_ACCESS_TOKEN={page_token}\n")
        if not page_id_updated:
            lines.append(f"FACEBOOK_PAGE_ID={page_id}\n")

        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(lines)

        print(f"[SUCCESS] Updated .env file with page access token")
        print("\n[NEXT STEPS]")
        print("   1. Run: python demo_facebook_post.py")
        print("   2. Your post should now work!")

    except Exception as e:
        print(f"\n[ERROR] Failed to update .env: {str(e)}")
        print(f"\n[MANUAL STEP] Please update your .env file:")
        print(f"   FACEBOOK_ACCESS_TOKEN={page_token}")
        print(f"   FACEBOOK_PAGE_ID={page_id}")


if __name__ == "__main__":
    token = get_page_access_token()

    print("\n" + "="*60)
    if token:
        print("[SUCCESS] Page access token retrieved and saved!")
    else:
        print("[FAILED] Could not get page access token")
    print("="*60 + "\n")
