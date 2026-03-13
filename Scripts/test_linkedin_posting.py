"""
LinkedIn Posting Test
Simple script to test LinkedIn integration after adding credentials
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

def test_linkedin_credentials():
    """Check if LinkedIn credentials are configured"""
    print("\n" + "="*60)
    print("LINKEDIN CREDENTIAL CHECK")
    print("="*60)

    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")

    credentials = {
        "LINKEDIN_CLIENT_ID": client_id,
        "LINKEDIN_CLIENT_SECRET": client_secret,
        "LINKEDIN_ACCESS_TOKEN": access_token
    }

    all_configured = True
    for name, value in credentials.items():
        if not value or "your_" in value.lower():
            print(f"\n[X] {name}: NOT CONFIGURED")
            all_configured = False
        else:
            # Show first/last few characters only
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else value
            print(f"\n[OK] {name}: {masked}")

    if not all_configured:
        print("\n" + "="*60)
        print("[ERROR] LinkedIn credentials not configured!")
        print("="*60)
        print("\nNext steps:")
        print("1. Go to: https://www.linkedin.com/developers/apps")
        print("2. Create app and get credentials")
        print("3. Add to .env file:")
        print("   LINKEDIN_CLIENT_ID=your_client_id")
        print("   LINKEDIN_CLIENT_SECRET=your_client_secret")
        print("   LINKEDIN_ACCESS_TOKEN=your_access_token")
        print("\nSee LINKEDIN_COMPLETE_SETUP.md for detailed guide")
        print("="*60 + "\n")
        return False

    print("\n" + "="*60)
    print("[SUCCESS] All LinkedIn credentials configured!")
    print("="*60 + "\n")
    return True

def test_linkedin_posting():
    """Test posting to LinkedIn"""
    print("\n" + "="*60)
    print("LINKEDIN POSTING TEST")
    print("="*60)

    try:
        from src.mcp.linkedin.linkedin_mcp import LinkedInClient

        client_id = os.getenv("LINKEDIN_CLIENT_ID")
        client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")

        print("\n[*] Initializing LinkedIn client...")
        client = LinkedInClient(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token
        )

        print("[*] Posting test message to LinkedIn...")
        test_content = "Testing LinkedIn integration from AI Employee System! 🚀 #Automation #AIEmployee"

        result = client.post_content(content=test_content)

        if result and result.get("id"):
            print("\n" + "="*60)
            print("[SUCCESS] Posted to LinkedIn!")
            print("="*60)
            print(f"\nPost ID: {result.get('id')}")
            print(f"Post URL: https://www.linkedin.com/feed/update/{result.get('id')}")
            print("\nContent posted:")
            print(f"  {test_content}")
            print("\n" + "="*60 + "\n")
            return True
        else:
            print("\n[ERROR] LinkedIn API returned no post ID")
            print(f"Response: {result}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Failed to post to LinkedIn: {e}")
        print("\nTroubleshooting:")
        print("- Check that credentials are correct in .env")
        print("- Verify access token hasn't expired (60 days)")
        print("- Ensure w_member_social scope is approved")
        print("- Check rate limits (20 posts per 24 hours)")
        return False

def main():
    print("\n" + "="*60)
    print("LINKEDIN INTEGRATION TEST")
    print("="*60)
    print("\nThis script will:")
    print("1. Check if LinkedIn credentials are configured")
    print("2. Test posting to LinkedIn")
    print("3. Verify the integration is working")

    # Check credentials
    if not test_linkedin_credentials():
        sys.exit(1)

    # Test posting
    print("\n[*] Credentials verified. Ready to test posting.")
    input("\nPress Enter to post a test message to LinkedIn (or Ctrl+C to cancel)...")

    success = test_linkedin_posting()

    if success:
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n[1] Post to multiple platforms at once:")
        print("    python social_media_post.py 'Your content'")
        print("\n[2] Use LinkedIn client in your scripts:")
        print("    from src.mcp.linkedin.linkedin_mcp import LinkedInClient")
        print("\n[3] Check system status:")
        print("    python verify_system.py")
        print("\n" + "="*60 + "\n")
        sys.exit(0)
    else:
        print("\n[FAILED] LinkedIn posting test failed")
        print("See error messages above for troubleshooting")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Test cancelled by user")
        sys.exit(0)
