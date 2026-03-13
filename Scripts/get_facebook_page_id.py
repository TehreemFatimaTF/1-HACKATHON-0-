"""
Simple script to fetch your Facebook Page ID
Uses your access token to list all pages you manage
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_facebook_pages():
    """Fetch all Facebook pages associated with the access token"""
    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")

    if not access_token:
        print("[ERROR] FACEBOOK_ACCESS_TOKEN not found in .env file")
        return

    print("\n" + "="*60)
    print("FETCHING YOUR FACEBOOK PAGES")
    print("="*60)

    try:
        # Call Facebook Graph API to get pages
        url = f"https://graph.facebook.com/v18.0/me/accounts"
        params = {
            "access_token": access_token
        }

        print("\n[*] Fetching pages from Facebook...")
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if "data" in data and len(data["data"]) > 0:
            print(f"\n[SUCCESS] Found {len(data['data'])} page(s):\n")

            for idx, page in enumerate(data["data"], 1):
                print(f"{idx}. Page Name: {page.get('name')}")
                print(f"   Page ID: {page.get('id')}")
                print(f"   Category: {page.get('category', 'N/A')}")
                print(f"   Access Token: {page.get('access_token', 'N/A')[:20]}...")
                print()

            # If only one page, suggest using it
            if len(data["data"]) == 1:
                page_id = data["data"][0]["id"]
                page_name = data["data"][0]["name"]
                print("="*60)
                print(f"[SUCCESS] Use this Page ID in your .env file:")
                print(f"   FACEBOOK_PAGE_ID={page_id}")
                print("="*60)

                # Offer to update .env automatically
                response = input("\n[?] Do you want me to update your .env file automatically? (yes/no): ")
                if response.lower() == 'yes':
                    update_env_file(page_id)
            else:
                print("="*60)
                print("[NOTE] Copy the Page ID you want to use and add it to your .env file:")
                print("   FACEBOOK_PAGE_ID=<your_page_id>")
                print("="*60)
        else:
            print("\n[ERROR] No pages found!")
            print("   Make sure your access token has 'pages_manage_posts' permission")
            print("   and that you manage at least one Facebook page")

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Error fetching pages: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")


def update_env_file(page_id):
    """Update .env file with the Page ID"""
    try:
        env_path = ".env"

        # Read current .env content
        with open(env_path, 'r') as f:
            lines = f.readlines()

        # Update FACEBOOK_PAGE_ID line
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("FACEBOOK_PAGE_ID="):
                lines[i] = f"FACEBOOK_PAGE_ID={page_id}\n"
                updated = True
                break

        # If not found, append it
        if not updated:
            lines.append(f"\nFACEBOOK_PAGE_ID={page_id}\n")

        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(lines)

        print(f"\n[SUCCESS] Updated .env file with Page ID: {page_id}")
        print("\n[NEXT STEPS]")
        print("   1. Run: python test_facebook_integration.py")
        print("   2. Test posting to your Facebook page")

    except Exception as e:
        print(f"\n[ERROR] Error updating .env file: {str(e)}")
        print(f"   Please manually add: FACEBOOK_PAGE_ID={page_id}")


if __name__ == "__main__":
    get_facebook_pages()
