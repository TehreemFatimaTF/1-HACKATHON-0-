"""
Social Media Manager - Multi-Platform Posting
Posts content to all configured social media platforms
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

def post_to_facebook(content):
    """Post to Facebook"""
    try:
        from src.mcp.facebook_client import FacebookClient

        access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        page_id = os.getenv("FACEBOOK_PAGE_ID")

        if not access_token or not page_id:
            return {"success": False, "error": "Facebook not configured"}

        client = FacebookClient(access_token=access_token, page_id=page_id)
        result = client.post_to_page(content=content)

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def post_to_linkedin(content):
    """Post to LinkedIn"""
    try:
        from src.mcp.linkedin.linkedin_mcp import LinkedInClient

        # Check if OAuth credentials are configured
        client_id = os.getenv("LINKEDIN_CLIENT_ID")
        client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")

        if not all([client_id, client_secret, access_token]):
            return {
                "success": False,
                "error": "LinkedIn OAuth credentials not configured (need CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN)"
            }

        # Initialize LinkedIn client
        client = LinkedInClient(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token
        )

        # Post content
        result = client.post_content(content=content)

        if result and result.get("id"):
            return {
                "success": True,
                "post_id": result.get("id"),
                "post_url": f"https://www.linkedin.com/feed/update/{result.get('id')}"
            }
        else:
            return {"success": False, "error": "LinkedIn API returned no post ID"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def post_to_twitter(content):
    """Post to Twitter"""
    try:
        import requests
        from requests_oauthlib import OAuth1

        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

        if not all([api_key, api_secret, access_token, access_token_secret]):
            return {"success": False, "error": "Twitter not configured"}

        # Create OAuth1 authentication
        auth = OAuth1(api_key, api_secret, access_token, access_token_secret)

        # Post tweet
        url = "https://api.twitter.com/2/tweets"
        payload = {"text": content}

        response = requests.post(
            url,
            auth=auth,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 201:
            data = response.json()
            tweet_id = data["data"]["id"]
            return {
                "success": True,
                "post_id": tweet_id,
                "post_url": f"https://twitter.com/i/web/status/{tweet_id}"
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def post_to_all_platforms(content):
    """Post to all configured platforms"""
    print("\n" + "="*60)
    print("SOCIAL MEDIA MANAGER - MULTI-PLATFORM POSTING")
    print("="*60)

    # Remove emojis for Windows console compatibility
    safe_content = content.encode('ascii', 'ignore').decode('ascii')
    print(f"\nContent: {safe_content if safe_content else '[Contains non-ASCII characters]'}")
    print(f"Original length: {len(content)} characters")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # Post to Facebook
    print("\n[1/3] Posting to Facebook...")
    fb_result = post_to_facebook(content)
    results["Facebook"] = fb_result

    if fb_result.get("success"):
        print(f"   [SUCCESS] Posted to Facebook")
        print(f"   Post ID: {fb_result.get('post_id')}")
        print(f"   Post URL: {fb_result.get('post_url')}")
    else:
        print(f"   [FAILED] {fb_result.get('error')}")

    # Post to LinkedIn
    print("\n[2/3] Posting to LinkedIn...")
    li_result = post_to_linkedin(content)
    results["LinkedIn"] = li_result

    if li_result.get("success"):
        print(f"   [SUCCESS] Posted to LinkedIn")
        print(f"   Post ID: {li_result.get('post_id')}")
        print(f"   Post URL: {li_result.get('post_url')}")
    else:
        print(f"   [SKIPPED] {li_result.get('error')}")

    # Post to Twitter
    print("\n[3/3] Posting to Twitter...")
    tw_result = post_to_twitter(content)
    results["Twitter"] = tw_result

    if tw_result.get("success"):
        print(f"   [SUCCESS] Posted to Twitter")
        print(f"   Tweet ID: {tw_result.get('post_id')}")
        print(f"   Tweet URL: {tw_result.get('post_url')}")
    else:
        print(f"   [FAILED] {tw_result.get('error')}")

    # Summary
    print("\n" + "="*60)
    print("POSTING SUMMARY")
    print("="*60)

    successful = sum(1 for r in results.values() if r.get("success"))
    total = len(results)

    print(f"\nPlatforms attempted: {total}")
    print(f"Successful posts: {successful}")
    print(f"Failed posts: {total - successful}")

    print("\n[RESULTS BY PLATFORM]")
    for platform, result in results.items():
        status = "[OK]" if result.get("success") else "[FAILED]"
        print(f"   {status} {platform}")
        if result.get("post_url"):
            print(f"        URL: {result.get('post_url')}")

    print("\n" + "="*60 + "\n")

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python social_media_post.py 'Your content here'")
        sys.exit(1)

    content = sys.argv[1]
    results = post_to_all_platforms(content)

    # Exit with error code if all posts failed
    if not any(r.get("success") for r in results.values()):
        sys.exit(1)
