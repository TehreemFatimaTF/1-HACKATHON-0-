"""
Automated Facebook Watcher Demo
This script demonstrates the complete workflow without interactive prompts
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from watcher_facebook import FacebookWatcher
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def automated_demo():
    """Run automated demo of Facebook watcher"""
    print("\n" + "="*60)
    print("FACEBOOK WATCHER - AUTOMATED DEMO")
    print("="*60)

    # Check credentials
    has_facebook = bool(os.getenv("FACEBOOK_ACCESS_TOKEN") and os.getenv("FACEBOOK_PAGE_ID"))

    print("\n[Configuration Status]")
    print(f"   Facebook: {'[OK] Configured' if has_facebook else '[X] Not configured'}")

    if not has_facebook:
        print("\n[ERROR] Facebook credentials not found!")
        print("   Please run: python get_page_access_token.py")
        return False

    try:
        # Initialize watcher
        print("\n[Step 1] Initializing Facebook Watcher...")
        watcher = FacebookWatcher()
        print("   [OK] Watcher initialized")

        # Create sample content
        print("\n[Step 2] Creating sample content...")
        sample_content = {
            "title": "AI Automation Success Story",
            "content": f"""AI Automation Success Story

Just helped a client save 20 hours per week with AI automation!

Small businesses are discovering the power of AI employees for:
- Email management
- Social media posting
- Customer follow-ups
- Data entry

The future of work is here! What tasks would you automate first?

Posted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#AIAutomation #SmallBusiness #Productivity #FutureOfWork""",
            "category": "Success Story",
            "engagement_potential": "High",
            "hashtags": "#AIAutomation #SmallBusiness #Productivity #FutureOfWork",
            "post_type": "text",
            "platforms": ["facebook"]
        }
        print(f"   [OK] Content created: {sample_content['title']}")

        # Create inbox file
        print("\n[Step 3] Creating inbox file...")
        filepath = watcher.create_inbox_file(sample_content)
        print(f"   [OK] Inbox file created: {filepath}")

        # Post to Facebook
        print("\n[Step 4] Posting to Facebook...")
        result = watcher.post_to_facebook(sample_content['content'])

        if result.get('success'):
            print(f"   [SUCCESS] Posted to Facebook!")
            print(f"   Post ID: {result.get('post_id')}")
            print(f"   Post URL: {result.get('post_url')}")

            # Generate summary
            print("\n[Step 5] Generating summary report...")
            summary_file = watcher.create_summary_markdown()
            print(f"   [OK] Summary created: {summary_file}")

            print("\n" + "="*60)
            print("[SUCCESS] Complete workflow executed!")
            print("="*60)
            print("\nWhat happened:")
            print("1. Watcher initialized with Facebook credentials")
            print("2. Sample content created (AI automation post)")
            print("3. Inbox file saved for tracking")
            print("4. Content posted to Facebook page")
            print("5. Summary report generated")
            print("\nNext steps:")
            print("- Check your Facebook page to see the post")
            print("- Review the inbox file in Inbox/ directory")
            print("- Check the summary in Done/ directory")
            print("- Run this script again to post more content")
            print("="*60)

            return True
        else:
            print(f"   [ERROR] Posting failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def show_watcher_info():
    """Show information about the watcher system"""
    print("\n" + "="*60)
    print("ABOUT FACEBOOK WATCHER")
    print("="*60)
    print("\nThe Facebook Watcher is a content management system that:")
    print("\n1. Content Creation")
    print("   - Generates engaging social media content")
    print("   - Categorizes by type (success stories, tips, updates)")
    print("   - Adds relevant hashtags automatically")
    print("\n2. Inbox Management")
    print("   - Saves content to Inbox/ directory")
    print("   - Tracks metadata (category, engagement potential)")
    print("   - Organizes by timestamp")
    print("\n3. Multi-Platform Posting")
    print("   - Posts to Facebook (working)")
    print("   - Instagram support (when linked)")
    print("   - Unified posting interface")
    print("\n4. Summary Generation")
    print("   - Creates markdown summaries")
    print("   - Tracks post performance")
    print("   - Saves to Done/ directory")
    print("\n5. Continuous Monitoring (Optional)")
    print("   - Runs every 30 minutes")
    print("   - Auto-generates content")
    print("   - Auto-posts to platforms")
    print("\nUsage Modes:")
    print("- Manual: Run this script to post once")
    print("- Continuous: Run demo_facebook_watcher.py in your terminal")
    print("- Integrated: Use with social-media-manager skill")
    print("="*60)


if __name__ == "__main__":
    # Show info first
    show_watcher_info()

    # Ask if user wants to run demo
    print("\n[?] This will post a test message to your Facebook page.")
    print("    Continue? (Press Ctrl+C to cancel, or wait 5 seconds to proceed)")

    import time
    try:
        time.sleep(5)
        print("\n[*] Starting automated demo...\n")
        success = automated_demo()

        if not success:
            print("\n[FAILED] Demo encountered errors")
    except KeyboardInterrupt:
        print("\n\n[*] Demo cancelled by user")
        print("    Run 'python demo_facebook_auto.py' when ready to test")
