"""
Quick demo script for Facebook Watcher
Shows how to use the Facebook watcher with manual posting
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from watcher_facebook import FacebookWatcher


def demo_manual_posting():
    """Demo: Manual content creation and posting"""
    print("\n" + "="*60)
    print("FACEBOOK WATCHER - MANUAL POSTING DEMO")
    print("="*60)

    # Initialize watcher
    watcher = FacebookWatcher()

    # Sample content
    sample_content = {
        "title": "AI Automation Success Story",
        "content": "Just helped a client save 20 hours per week with AI automation! 🚀\n\nSmall businesses are discovering the power of AI employees for:\n✅ Email management\n✅ Social media posting\n✅ Customer follow-ups\n✅ Data entry\n\nThe future of work is here! What tasks would you automate first?",
        "category": "Success Story",
        "engagement_potential": "High",
        "hashtags": "#AIAutomation #SmallBusiness #Productivity #FutureOfWork",
        "post_type": "text",
        "platforms": ["facebook"]
    }

    print("\n[Sample Content]")
    print(f"   Title: {sample_content['title']}")
    print(f"   Category: {sample_content['category']}")
    print(f"   Platforms: {', '.join(sample_content['platforms'])}")

    # Create inbox file
    print("\n[*] Creating inbox file...")
    filepath = watcher.create_inbox_file(sample_content)
    print(f"   [OK] Created: {filepath}")

    # Ask if user wants to post
    response = input("\n[?] Do you want to post this to Facebook? (yes/no): ")

    if response.lower() == 'yes':
        print("\n[*] Posting to Facebook...")
        result = watcher.post_to_facebook(sample_content['content'])

        if result.get('success'):
            print(f"\n[SUCCESS] Posted successfully!")
            print(f"   Post ID: {result.get('post_id')}")
            print(f"   Post URL: {result.get('post_url')}")

            # Generate summary
            print("\n[*] Generating summary...")
            summary_file = watcher.create_summary_markdown()
            print(f"   [OK] Summary created: {summary_file}")
        else:
            print(f"\n[ERROR] Posting failed: {result.get('error')}")
    else:
        print("\n[*] Skipped posting")

    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60 + "\n")


def demo_watcher_mode():
    """Demo: Run watcher in continuous mode"""
    print("\n" + "="*60)
    print("FACEBOOK WATCHER - CONTINUOUS MODE DEMO")
    print("="*60)

    print("\n[WARNING] This will start the watcher in continuous mode")
    print("   It will create inbox files every 30 minutes")
    print("   Press Ctrl+C to stop\n")

    response = input("Start watcher? (yes/no): ")

    if response.lower() == 'yes':
        watcher = FacebookWatcher()
        watcher.start()
    else:
        print("\n[*] Skipped watcher mode")


def main():
    """Main demo menu"""
    print("\n" + "="*60)
    print("FACEBOOK WATCHER DEMO")
    print("="*60)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Check credentials
    has_facebook = bool(os.getenv("FACEBOOK_ACCESS_TOKEN") and os.getenv("FACEBOOK_PAGE_ID"))
    has_instagram = bool(os.getenv("INSTAGRAM_ACCESS_TOKEN") and os.getenv("INSTAGRAM_ACCOUNT_ID"))

    print("\n[Configuration Status]")
    print(f"   Facebook: {'[OK] Configured' if has_facebook else '[X] Not configured'}")
    print(f"   Instagram: {'[OK] Configured' if has_instagram else '[X] Not configured'}")

    if not has_facebook:
        print("\n[WARNING] Facebook credentials not found!")
        print("   Please configure FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID in .env")
        print("   See docs/FACEBOOK_INSTAGRAM_SETUP.md for instructions")

    print("\n" + "="*60)
    print("Select Demo Mode:")
    print("="*60)
    print("1. Manual Posting Demo (create and post single content)")
    print("2. Continuous Watcher Mode (monitor and create inbox files)")
    print("3. Exit")

    choice = input("\nEnter choice (1-3): ")

    if choice == "1":
        demo_manual_posting()
    elif choice == "2":
        demo_watcher_mode()
    elif choice == "3":
        print("\nGoodbye!\n")
    else:
        print("\n[ERROR] Invalid choice\n")


if __name__ == "__main__":
    main()
