"""
Simple Facebook integration test (Windows-compatible, no emojis)
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp.facebook_client import FacebookClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_facebook():
    """Test Facebook connection and posting"""
    print("\n" + "="*60)
    print("FACEBOOK INTEGRATION TEST")
    print("="*60)

    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")

    print(f"\nAccess Token: {access_token[:20]}..." if access_token else "Access Token: NOT FOUND")
    print(f"Page ID: {page_id}")

    if not access_token or not page_id:
        print("\n[ERROR] Missing credentials in .env file")
        return False

    try:
        # Initialize client
        print("\n[*] Initializing Facebook client...")
        client = FacebookClient(
            access_token=access_token,
            page_id=page_id
        )

        # Test health check
        print("[*] Testing connection...")
        health = client.health_check()

        print(f"\n[SUCCESS] Facebook Connection: {health['status']}")
        print(f"   Authenticated: {health.get('authenticated', False)}")
        print(f"   Rate Limit: {health.get('rate_limit', 'N/A')}")

        # Ask if user wants to test posting
        print("\n" + "="*60)
        print("TEST POSTING (Optional)")
        print("="*60)

        response = input("\nDo you want to test posting to Facebook? (yes/no): ")

        if response.lower() == 'yes':
            test_content = f"Test post from AI Employee - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n#AIEmployee #TestPost"

            print(f"\n[*] Posting to Facebook...")
            print(f"    Content: {test_content[:50]}...")

            result = client.post_to_page(content=test_content)

            if result.get('success'):
                print(f"\n[SUCCESS] Post published!")
                print(f"   Post ID: {result.get('post_id')}")
                print(f"   Post URL: {result.get('post_url')}")
                return True
            else:
                print(f"\n[ERROR] Post failed: {result.get('error')}")
                return False
        else:
            print("\n[*] Skipped posting test")
            return True

    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_facebook()

    print("\n" + "="*60)
    if success:
        print("[SUCCESS] Facebook integration is working!")
    else:
        print("[FAILED] Facebook integration has issues")
    print("="*60 + "\n")
