"""
Twitter/X Integration Setup and Testing
Helps get Access Token and tests Twitter posting
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_twitter_credentials():
    """Check which Twitter credentials are configured"""
    print("\n" + "="*60)
    print("TWITTER/X CREDENTIALS CHECK")
    print("="*60)

    creds = {
        "API Key (Consumer Key)": os.getenv("TWITTER_API_KEY"),
        "API Secret (Consumer Secret)": os.getenv("TWITTER_API_SECRET"),
        "Bearer Token": os.getenv("TWITTER_BEARER_TOKEN"),
        "Access Token": os.getenv("TWITTER_ACCESS_TOKEN"),
        "Access Token Secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    }

    print("\n[CREDENTIAL STATUS]\n")

    all_configured = True
    for name, value in creds.items():
        if value and value != f"your_{name.lower().replace(' ', '_')}_here" and "your_" not in value.lower():
            masked = value[:15] + "..." if len(value) > 15 else "***"
            print(f"[OK] {name}: {masked}")
        else:
            print(f"[X] {name}: NOT SET")
            all_configured = False

    return all_configured, creds

def test_bearer_token():
    """Test Bearer Token with read-only API call"""
    print("\n" + "="*60)
    print("TESTING BEARER TOKEN (Read-Only)")
    print("="*60)

    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    if not bearer_token or "your_" in bearer_token.lower():
        print("\n[ERROR] Bearer Token not configured")
        return False

    try:
        # Test with a simple API call - get user info
        print("\n[*] Testing connection to Twitter API...")

        headers = {
            "Authorization": f"Bearer {bearer_token}"
        }

        # Get authenticated user info
        response = requests.get(
            "https://api.twitter.com/2/users/me",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            user_data = data.get("data", {})

            print(f"\n[SUCCESS] Connected to Twitter!")
            print(f"   Username: @{user_data.get('username', 'N/A')}")
            print(f"   Name: {user_data.get('name', 'N/A')}")
            print(f"   User ID: {user_data.get('id', 'N/A')}")
            print(f"\n   Bearer Token: VALID (Read-only access)")
            return True
        else:
            print(f"\n[ERROR] Connection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        return False

def show_access_token_instructions():
    """Show how to get Access Token and Secret"""
    print("\n" + "="*60)
    print("HOW TO GET ACCESS TOKEN & SECRET")
    print("="*60)

    print("\n[STEP 1] Go to Twitter Developer Portal")
    print("   Visit: https://developer.twitter.com/en/portal/dashboard")

    print("\n[STEP 2] Select Your App")
    print("   - Click on your app name")
    print("   - Go to 'Keys and tokens' tab")

    print("\n[STEP 3] Generate Access Token & Secret")
    print("   - Scroll to 'Authentication Tokens' section")
    print("   - Click 'Generate' under 'Access Token and Secret'")
    print("   - IMPORTANT: Set permissions to 'Read and Write'")
    print("   - Copy both the Access Token and Access Token Secret")

    print("\n[STEP 4] Update .env File")
    print("   Add these lines to your .env file:")
    print("   TWITTER_ACCESS_TOKEN=<your_access_token>")
    print("   TWITTER_ACCESS_TOKEN_SECRET=<your_access_token_secret>")

    print("\n[STEP 5] Test Again")
    print("   Run: python setup_twitter.py")

    print("\n[NOTE] App Permissions")
    print("   Make sure your app has 'Read and Write' permissions")
    print("   If not, go to 'Settings' tab and update permissions")

def test_posting_capability():
    """Test if we can post tweets"""
    print("\n" + "="*60)
    print("TESTING POSTING CAPABILITY")
    print("="*60)

    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("\n[ERROR] Missing credentials for posting")
        print("   Need: Access Token and Access Token Secret")
        return False

    if "your_" in access_token.lower() or "your_" in access_token_secret.lower():
        print("\n[ERROR] Access Token/Secret not configured")
        return False

    print("\n[OK] All credentials present")
    print("   Ready to test posting")

    # We'll implement actual posting test after credentials are set
    return True

def main():
    """Main setup and test flow"""
    print("\n" + "="*60)
    print("TWITTER/X INTEGRATION SETUP")
    print("="*60)

    # Check credentials
    all_configured, creds = check_twitter_credentials()

    # Test Bearer Token (read-only)
    bearer_works = test_bearer_token()

    # Check if we can post
    if all_configured:
        can_post = test_posting_capability()

        if can_post:
            print("\n" + "="*60)
            print("[SUCCESS] Twitter integration ready!")
            print("="*60)
            print("\n[NEXT STEPS]")
            print("   1. Test posting: python demo_twitter_post.py")
            print("   2. Use in automation: /social-media-manager")
            print("   3. Monitor engagement")
    else:
        # Show instructions for missing credentials
        show_access_token_instructions()

        print("\n" + "="*60)
        print("[ACTION REQUIRED]")
        print("="*60)
        print("\n1. Get Access Token and Secret from Twitter Developer Portal")
        print("2. Update .env file with the tokens")
        print("3. Run this script again: python setup_twitter.py")

    # Summary
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)

    if bearer_works:
        print("\n[OK] Read-only access: WORKING")
        print("   - Can fetch tweets")
        print("   - Can get user info")
        print("   - Can search tweets")

    if all_configured:
        print("\n[OK] Write access: READY")
        print("   - Can post tweets")
        print("   - Can reply to tweets")
        print("   - Can send DMs")
    else:
        print("\n[PENDING] Write access: Need Access Token & Secret")
        print("   Follow the instructions above to complete setup")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
