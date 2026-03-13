"""
Simple Twitter Posting Test (No External Dependencies)
Uses requests library to post directly to Twitter API v2
"""

import os
import json
import requests
from requests_oauthlib import OAuth1
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_twitter_post_simple():
    """Test posting a tweet using Twitter API v2"""
    print("\n" + "="*60)
    print("TWITTER POSTING TEST")
    print("="*60)

    # Get credentials
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("\n[ERROR] Missing Twitter credentials")
        return False

    print("\n[OK] All credentials present")
    print(f"   API Key: {api_key[:15]}...")
    print(f"   Access Token: {access_token[:20]}...")

    try:
        # Create OAuth1 authentication
        auth = OAuth1(
            api_key,
            api_secret,
            access_token,
            access_token_secret
        )

        # Create tweet text
        tweet_text = f"""AI Employee Test Tweet

This is an automated tweet from my AI Employee system!

Posted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#AIEmployee #Automation #TestTweet"""

        print(f"\n[*] Posting tweet...")
        print(f"    Content: {tweet_text[:50]}...")

        # Post tweet using Twitter API v2
        url = "https://api.twitter.com/2/tweets"
        payload = {"text": tweet_text}

        response = requests.post(
            url,
            auth=auth,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 201:
            data = response.json()
            tweet_id = data["data"]["id"]

            print(f"\n[SUCCESS] Tweet posted!")
            print(f"   Tweet ID: {tweet_id}")
            print(f"   Tweet URL: https://twitter.com/i/web/status/{tweet_id}")
            print(f"\n   Visit Twitter to see your tweet!")
            return True
        else:
            print(f"\n[ERROR] Failed to post tweet")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n[TWITTER INTEGRATION TEST]")
    print("Testing Twitter posting with OAuth 1.0a")

    success = test_twitter_post_simple()

    print("\n" + "="*60)
    if success:
        print("[SUCCESS] Twitter integration is working!")
        print("\n[NEXT STEPS]")
        print("   - Use TwitterClient in your automation")
        print("   - Post to multiple platforms with /social-media-manager")
        print("   - Monitor engagement and analytics")
    else:
        print("[FAILED] Twitter posting has issues")
        print("         Check the error message above")
    print("="*60 + "\n")
