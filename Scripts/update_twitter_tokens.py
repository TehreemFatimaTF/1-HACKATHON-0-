"""
Update Twitter Access Token and Secret
Interactive script to update .env file with Twitter tokens
"""

import os

def update_twitter_tokens():
    """Update .env file with Twitter Access Token and Secret"""
    print("\n" + "="*60)
    print("TWITTER TOKEN UPDATE")
    print("="*60)

    print("\n[INFO] This script will update your .env file with:")
    print("   - Twitter Access Token")
    print("   - Twitter Access Token Secret")

    print("\n[INSTRUCTIONS]")
    print("   1. Go to: https://developer.twitter.com/en/portal/dashboard")
    print("   2. Select your app")
    print("   3. Go to 'Keys and tokens' tab")
    print("   4. Generate 'Access Token and Secret'")
    print("   5. Copy both tokens")

    print("\n" + "="*60)

    # Get tokens from user
    print("\n[STEP 1] Enter Access Token")
    print("(It looks like: 1234567890-AbCdEfGhIjKlMnOpQrStUvWxYz)")
    access_token = input("\nAccess Token: ").strip()

    if not access_token:
        print("\n[ERROR] Access Token cannot be empty")
        return False

    print("\n[STEP 2] Enter Access Token Secret")
    print("(It looks like: AbCdEfGhIjKlMnOpQrStUvWxYz1234567890AbCdEf)")
    access_token_secret = input("\nAccess Token Secret: ").strip()

    if not access_token_secret:
        print("\n[ERROR] Access Token Secret cannot be empty")
        return False

    # Update .env file
    print("\n[*] Updating .env file...")

    try:
        env_path = ".env"

        # Read current .env content
        with open(env_path, 'r') as f:
            lines = f.readlines()

        # Update tokens
        token_updated = False
        secret_updated = False

        for i, line in enumerate(lines):
            if line.startswith("TWITTER_ACCESS_TOKEN="):
                lines[i] = f"TWITTER_ACCESS_TOKEN={access_token}\n"
                token_updated = True
            elif line.startswith("TWITTER_ACCESS_TOKEN_SECRET="):
                lines[i] = f"TWITTER_ACCESS_TOKEN_SECRET={access_token_secret}\n"
                secret_updated = True

        # If not found, append them
        if not token_updated:
            lines.append(f"\nTWITTER_ACCESS_TOKEN={access_token}\n")
        if not secret_updated:
            lines.append(f"TWITTER_ACCESS_TOKEN_SECRET={access_token_secret}\n")

        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(lines)

        print(f"[SUCCESS] Updated .env file")
        print(f"\n[TOKENS SAVED]")
        print(f"   Access Token: {access_token[:20]}...")
        print(f"   Access Token Secret: {access_token_secret[:20]}...")

        print("\n[NEXT STEPS]")
        print("   1. Test connection: python setup_twitter.py")
        print("   2. Test posting: python demo_twitter_post.py")

        return True

    except Exception as e:
        print(f"\n[ERROR] Failed to update .env: {str(e)}")
        print(f"\n[MANUAL UPDATE]")
        print(f"   Add these lines to your .env file:")
        print(f"   TWITTER_ACCESS_TOKEN={access_token}")
        print(f"   TWITTER_ACCESS_TOKEN_SECRET={access_token_secret}")
        return False


if __name__ == "__main__":
    print("\n[TWITTER TOKEN UPDATE TOOL]")
    print("This tool helps you add Twitter Access Token and Secret to .env")

    success = update_twitter_tokens()

    print("\n" + "="*60)
    if success:
        print("[SUCCESS] Twitter tokens updated!")
        print("          Run 'python setup_twitter.py' to test")
    else:
        print("[FAILED] Could not update tokens")
        print("         Update .env file manually")
    print("="*60 + "\n")
