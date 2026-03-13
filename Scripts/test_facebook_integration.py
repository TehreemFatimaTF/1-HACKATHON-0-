"""
Test script for Facebook & Instagram integration
Verifies credentials and tests posting functionality
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp.facebook_client import FacebookClient
from src.mcp.instagram_client import InstagramClient


def test_facebook_connection():
    """Test Facebook API connection"""
    print("\n" + "="*60)
    print("Testing Facebook Connection")
    print("="*60)

    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")

    if not access_token:
        print("❌ FACEBOOK_ACCESS_TOKEN not found in environment")
        return False

    if not page_id:
        print("❌ FACEBOOK_PAGE_ID not found in environment")
        return False

    try:
        client = FacebookClient(
            access_token=access_token,
            page_id=page_id
        )

        # Test health check
        health = client.health_check()
        print(f"\n✅ Facebook Connection: {health['status']}")
        print(f"   Authenticated: {health.get('authenticated', False)}")
        print(f"   Rate Limit: {health.get('rate_limit', 'N/A')}")

        return health['status'] == 'healthy'

    except Exception as e:
        print(f"\n❌ Facebook connection failed: {str(e)}")
        return False


def test_instagram_connection():
    """Test Instagram API connection"""
    print("\n" + "="*60)
    print("Testing Instagram Connection")
    print("="*60)

    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

    if not access_token:
        print("❌ INSTAGRAM_ACCESS_TOKEN not found in environment")
        return False

    if not account_id:
        print("❌ INSTAGRAM_ACCOUNT_ID not found in environment")
        return False

    try:
        client = InstagramClient(
            access_token=access_token,
            instagram_account_id=account_id
        )

        # Test health check
        health = client.health_check()
        print(f"\n✅ Instagram Connection: {health['status']}")
        print(f"   Authenticated: {health.get('authenticated', False)}")
        print(f"   Rate Limit: {health.get('rate_limit', 'N/A')}")

        return health['status'] == 'healthy'

    except Exception as e:
        print(f"\n❌ Instagram connection failed: {str(e)}")
        return False


def test_facebook_post():
    """Test posting to Facebook (optional)"""
    print("\n" + "="*60)
    print("Testing Facebook Post")
    print("="*60)

    response = input("\nDo you want to test posting to Facebook? (yes/no): ")
    if response.lower() != 'yes':
        print("⏭️  Skipping Facebook post test")
        return True

    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")

    try:
        client = FacebookClient(
            access_token=access_token,
            page_id=page_id
        )

        # Create test post
        test_content = f"🤖 Test post from AI Employee - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n#AIEmployee #TestPost"

        print(f"\nPosting to Facebook: {test_content[:50]}...")
        result = client.post_to_page(content=test_content)

        if result.get('success'):
            print(f"\n✅ Post successful!")
            print(f"   Post ID: {result.get('post_id')}")
            print(f"   Post URL: {result.get('post_url')}")
            return True
        else:
            print(f"\n❌ Post failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"\n❌ Facebook post test failed: {str(e)}")
        return False


def test_instagram_post():
    """Test posting to Instagram (optional)"""
    print("\n" + "="*60)
    print("Testing Instagram Post")
    print("="*60)

    print("\n⚠️  Instagram requires an image URL for posting")
    response = input("Do you want to test posting to Instagram? (yes/no): ")
    if response.lower() != 'yes':
        print("⏭️  Skipping Instagram post test")
        return True

    image_url = input("Enter a publicly accessible image URL: ")
    if not image_url:
        print("❌ Image URL is required for Instagram")
        return False

    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

    try:
        client = InstagramClient(
            access_token=access_token,
            instagram_account_id=account_id
        )

        # Create test post
        test_content = f"🤖 Test post from AI Employee"
        test_hashtags = ["#AIEmployee", "#TestPost", "#Automation"]

        print(f"\nPosting to Instagram...")
        result = client.post_to_instagram(
            content=test_content,
            hashtags=test_hashtags,
            image_url=image_url
        )

        if result.get('success'):
            print(f"\n✅ Post successful!")
            print(f"   Post ID: {result.get('post_id')}")
            print(f"   Post URL: {result.get('post_url')}")
            return True
        else:
            print(f"\n❌ Post failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"\n❌ Instagram post test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FACEBOOK & INSTAGRAM INTEGRATION TEST")
    print("="*60)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    results = {
        "facebook_connection": False,
        "instagram_connection": False,
        "facebook_post": None,
        "instagram_post": None
    }

    # Test connections
    results["facebook_connection"] = test_facebook_connection()
    results["instagram_connection"] = test_instagram_connection()

    # Test posting (optional)
    if results["facebook_connection"]:
        results["facebook_post"] = test_facebook_post()

    if results["instagram_connection"]:
        results["instagram_post"] = test_instagram_post()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    print(f"\n✅ Facebook Connection: {'PASS' if results['facebook_connection'] else 'FAIL'}")
    print(f"✅ Instagram Connection: {'PASS' if results['instagram_connection'] else 'FAIL'}")

    if results['facebook_post'] is not None:
        print(f"✅ Facebook Post: {'PASS' if results['facebook_post'] else 'FAIL'}")

    if results['instagram_post'] is not None:
        print(f"✅ Instagram Post: {'PASS' if results['instagram_post'] else 'FAIL'}")

    # Overall status
    all_passed = results['facebook_connection'] and results['instagram_connection']
    if results['facebook_post'] is not None:
        all_passed = all_passed and results['facebook_post']
    if results['instagram_post'] is not None:
        all_passed = all_passed and results['instagram_post']

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED - Check configuration")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
