"""
LinkedIn OAuth Token Generator
Helps you get an access token for LinkedIn API
"""

import os
from dotenv import load_dotenv

load_dotenv()

def generate_auth_url():
    """Generate LinkedIn OAuth authorization URL"""
    client_id = os.getenv("LINKEDIN_CLIENT_ID")

    if not client_id or "your_" in client_id:
        print("\n[ERROR] Please add LINKEDIN_CLIENT_ID to .env file first!")
        print("Get it from: https://www.linkedin.com/developers/apps")
        print("Go to Auth tab and copy the Client ID")
        return

    # OAuth parameters
    redirect_uri = "https://localhost"
    scope = "w_member_social r_liteprofile"
    state = "random_state_string_123"

    # Build authorization URL
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
        f"&state={state}"
    )

    print("\n" + "="*60)
    print("LINKEDIN OAUTH TOKEN GENERATOR")
    print("="*60)

    print("\n[STEP 1] Open this URL in your browser:")
    print(f"\n{auth_url}\n")

    print("[STEP 2] Click 'Allow' to authorize the app")
    print("[STEP 3] You'll be redirected to: https://localhost?code=...")
    print("[STEP 4] Copy the 'code' parameter from the URL")
    print("[STEP 5] Run this script again and paste the code when prompted")

    print("\n" + "="*60)
    print("\nAlternatively, use LinkedIn's token generator:")
    print("https://www.linkedin.com/developers/tools/oauth/token-generator")
    print("="*60 + "\n")

def exchange_code_for_token():
    """Exchange authorization code for access token"""
    import requests

    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("\n[ERROR] Please add LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET to .env file!")
        return

    code = input("\nPaste the authorization code from the URL: ").strip()

    if not code:
        print("[ERROR] No code provided!")
        return

    # Exchange code for token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "https://localhost"
    }

    print("\n[*] Exchanging code for access token...")

    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 0)

        print("\n" + "="*60)
        print("[SUCCESS] Access token retrieved!")
        print("="*60)
        print(f"\nAccess Token: {access_token}")
        print(f"Expires in: {expires_in} seconds ({expires_in // 86400} days)")

        print("\n[NEXT STEP] Add this to your .env file:")
        print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
        print("\n" + "="*60 + "\n")

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Failed to get token: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    import sys

    print("\n" + "="*60)
    print("LINKEDIN OAUTH SETUP HELPER")
    print("="*60)

    print("\nChoose an option:")
    print("1. Generate authorization URL (if you don't have a code yet)")
    print("2. Exchange authorization code for token (if you have a code)")
    print("3. Use LinkedIn's token generator (easiest - opens in browser)")

    choice = input("\nEnter choice (1/2/3): ").strip()

    if choice == "1":
        generate_auth_url()
    elif choice == "2":
        exchange_code_for_token()
    elif choice == "3":
        print("\n[*] Opening LinkedIn token generator...")
        print("URL: https://www.linkedin.com/developers/tools/oauth/token-generator")
        print("\nSteps:")
        print("1. Select your app")
        print("2. Select scopes: w_member_social, r_liteprofile")
        print("3. Click 'Request access token'")
        print("4. Copy the token and add to .env file")

        # Try to open in browser
        try:
            import webbrowser
            webbrowser.open("https://www.linkedin.com/developers/tools/oauth/token-generator")
        except:
            pass
    else:
        print("\n[ERROR] Invalid choice!")
