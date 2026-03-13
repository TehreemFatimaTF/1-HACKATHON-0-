"""
Demo: Post to Facebook automatically
This script posts a test message to your Facebook page
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

def post_to_facebook():
    """Post a test message to Facebook"""
    print("\n" + "="*60)
    print("FACEBOOK AUTO-POST DEMO")
    print("="*60)

    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")

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

        # Create test post content
        test_content = f"""AI Employee Test Post

This is an automated post from my AI Employee system!

Posted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#AIEmployee #Automation #TestPost #Hackathon"""

        print(f"\n[*] Posting to Facebook page 'Hackathon-0'...")
        print(f"    Content: AI Employee Test Post...")

        # Post to Facebook
        result = client.post_to_page(content=test_content)

        if result.get('success'):
            print(f"\n[SUCCESS] Post published successfully!")
            print(f"   Post ID: {result.get('post_id')}")
            print(f"   Post URL: {result.get('post_url')}")
            print(f"\n   Visit your Facebook page to see the post:")
            print(f"   https://facebook.com/{page_id}")
            return True
        else:
            print(f"\n[ERROR] Post failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Failed to post: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = post_to_facebook()

    print("\n" + "="*60)
    if success:
        print("[SUCCESS] Facebook posting is working!")
        print("\nNext steps:")
        print("1. Check your Facebook page to see the post")
        print("2. Use the FacebookClient in your automation scripts")
        print("3. Integrate with the watcher system for auto-posting")
    else:
        print("[FAILED] Facebook posting has issues")
    print("="*60 + "\n")
