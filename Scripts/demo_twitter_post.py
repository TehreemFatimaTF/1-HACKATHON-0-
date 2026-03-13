"""
Twitter/X Posting Demo
Tests posting a tweet to your Twitter account
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_twitter_post():
    """Test posting a tweet"""
    print("\n" + "="*60)
    print("TWITTER/X POSTING DEMO")
    print("="*60)

    # Check credentials
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    print("\n[CHECKING CREDENTIALS]")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("\n[ERROR] Missing Twitter credentials")
        print("\n[REQUIRED]")
        print("   - API Key: " + ("[OK]" if api_key else "[MISSING]"))
        print("   - API Secret: " + ("[OK]" if api_secret else "[MISSING]"))
        print("   - Access Token: " + ("[OK]" if access_token and "your_" not in access_token.lower() else "[MISSING]"))
        print("   - Access Token Secret: " + ("[OK]" if access_token_secret and "your_" not in access_token_secret.lower() else "[MISSING]"))
        print("\n[ACTION] Run: python update_twitter_tokens.py")
        return False

    if "your_" in access_token.lower() or "your_" in access_token_secret.lower():
        print("\n[ERROR] Access Token/Secret not configured")
        print("   Run: python update_twitter_tokens.py")
        return False

    print("[OK] All credentials present")

    # Try to post using tweepy
    try:
        import tweepy

        print("\n[*] Initializing Twitter client...")

        # Create API client
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        # Verify credentials
        print("[*] Verifying credentials...")
        user = api.verify_credentials()

        print(f"\n[SUCCESS] Connected to Twitter!")
        print(f"   Username: @{user.screen_name}")
        print(f"   Name: {user.name}")
        print(f"   Followers: {user.followers_count}")
        print(f"   Following: {user.friends_count}")

        # Create test tweet
        tweet_text = f"""AI Employee Test Tweet

This is an automated tweet from my AI Employee system!

Posted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#AIEmployee #Automation #TestTweet"""

        print(f"\n[*] Posting tweet...")
        print(f"    Content: {tweet_text[:50]}...")

        # Post tweet
        tweet = api.update_status(tweet_text)

        print(f"\n[SUCCESS] Tweet posted!")
        print(f"   Tweet ID: {tweet.id}")
        print(f"   Tweet URL: https://twitter.com/{user.screen_name}/status/{tweet.id}")
        print(f"\n   Visit Twitter to see your tweet!")

        return True

    except ImportError:
        print("\n[ERROR] tweepy library not installed")
        print("   Install: pip install tweepy")
        return False

    except tweepy.errors.Unauthorized as e:
        print(f"\n[ERROR] Authentication failed")
        print(f"   {str(e)}")
        print("\n[POSSIBLE CAUSES]")
        print("   1. Access Token/Secret are incorrect")
        print("   2. App permissions are 'Read only' (need 'Read and Write')")
        print("   3. Tokens were regenerated but not updated in .env")
        print("\n[SOLUTION]")
        print("   1. Check app permissions in Developer Portal")
        print("   2. Regenerate Access Token and Secret")
        print("   3. Run: python update_twitter_tokens.py")
        return False

    except Exception as e:
        print(f"\n[ERROR] Failed to post tweet: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def show_twitter_info():
    """Show Twitter integration info"""
    print("\n" + "="*60)
    print("ABOUT TWITTER INTEGRATION")
    print("="*60)

    print("\n[FEATURES]")
    print("   - Post tweets automatically")
    print("   - Reply to mentions")
    print("   - Send direct messages")
    print("   - Track engagement metrics")
    print("   - Schedule tweets")

    print("\n[USAGE IN CODE]")
    print("```python")
    print("from src.mcp.twitter_client import TwitterClient")
    print("")
    print("client = TwitterClient()")
    print('result = client.post_tweet("Your tweet here #hashtag")')
    print("```")

    print("\n[USAGE WITH SKILLS]")
    print("Post to all platforms at once:")
    print('   /social-media-manager post "Your content here"')

    print("\n[RATE LIMITS]")
    print("   - Tweets: 300 per 3 hours")
    print("   - Retweets: 300 per 3 hours")
    print("   - Likes: 1000 per 24 hours")
    print("   - Follows: 400 per 24 hours")


if __name__ == "__main__":
    # Show info
    show_twitter_info()

    # Wait a moment
    print("\n[?] This will post a test tweet to your Twitter account.")
    print("    Press Ctrl+C to cancel, or wait 3 seconds to proceed...")

    import time
    try:
        time.sleep(3)
        print("\n[*] Starting Twitter posting demo...\n")

        success = test_twitter_post()

        print("\n" + "="*60)
        if success:
            print("[SUCCESS] Twitter integration is working!")
            print("\n[NEXT STEPS]")
            print("   - Use TwitterClient in your automation")
            print("   - Post to multiple platforms with /social-media-manager")
            print("   - Monitor engagement and analytics")
        else:
            print("[FAILED] Twitter posting has issues")
            print("         Follow the instructions above to fix")
        print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\n[*] Demo cancelled by user")
        print("    Run 'python demo_twitter_post.py' when ready to test")
