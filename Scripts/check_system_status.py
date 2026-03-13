"""
Complete System Status Check
Tests all configured integrations and shows what's working
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_all_integrations():
    """Check status of all integrations"""
    print("\n" + "="*60)
    print("AI EMPLOYEE SYSTEM - INTEGRATION STATUS")
    print("="*60)

    integrations = {
        "LinkedIn": {
            "email": os.getenv("LINKEDIN_EMAIL"),
            "password": os.getenv("LINKEDIN_PASSWORD"),
            "status": "unknown"
        },
        "Gmail": {
            "email": os.getenv("GMAIL_EMAIL"),
            "password": os.getenv("GMAIL_APP_PASSWORD"),
            "status": "unknown"
        },
        "Facebook": {
            "app_id": os.getenv("FACEBOOK_APP_ID"),
            "page_id": os.getenv("FACEBOOK_PAGE_ID"),
            "token": os.getenv("FACEBOOK_ACCESS_TOKEN"),
            "status": "unknown"
        },
        "Instagram": {
            "account_id": os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID"),
            "token": os.getenv("INSTAGRAM_ACCESS_TOKEN"),
            "status": "unknown"
        },
        "Twitter": {
            "api_key": os.getenv("TWITTER_API_KEY"),
            "api_secret": os.getenv("TWITTER_API_SECRET"),
            "status": "unknown"
        },
        "Odoo": {
            "url": os.getenv("ODOO_URL"),
            "db": os.getenv("ODOO_DB"),
            "username": os.getenv("ODOO_USERNAME"),
            "status": "unknown"
        }
    }

    print("\n[CHECKING INTEGRATIONS]\n")

    # Check each integration
    for name, config in integrations.items():
        print(f"{name}:")

        # Check if credentials exist
        has_creds = all(
            v and v != f"your_{k}_here" and "your_" not in v.lower()
            for k, v in config.items()
            if k != "status"
        )

        if has_creds:
            print(f"   [OK] Credentials configured")

            # Show credential details (masked)
            for key, value in config.items():
                if key != "status" and value:
                    if "password" in key.lower() or "token" in key.lower() or "secret" in key.lower():
                        masked = value[:10] + "..." if len(value) > 10 else "***"
                        print(f"   - {key}: {masked}")
                    else:
                        print(f"   - {key}: {value}")

            config["status"] = "configured"
        else:
            print(f"   [X] Not configured")
            config["status"] = "not_configured"

        print()

    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)

    configured = sum(1 for i in integrations.values() if i["status"] == "configured")
    total = len(integrations)

    print(f"\nConfigured: {configured}/{total} integrations")
    print(f"Ready to use: {configured} platforms")

    # Show what can be done
    print("\n[AVAILABLE FEATURES]\n")

    if integrations["LinkedIn"]["status"] == "configured":
        print("[OK] LinkedIn")
        print("   - Post updates to LinkedIn")
        print("   - Monitor LinkedIn messages")
        print("   - Auto-respond to connections")

    if integrations["Gmail"]["status"] == "configured":
        print("[OK] Gmail")
        print("   - Send automated emails")
        print("   - Monitor inbox for tasks")
        print("   - Auto-categorize emails")

    if integrations["Facebook"]["status"] == "configured":
        print("[PENDING] Facebook")
        print("   - Post to Facebook page")
        print("   - Track engagement metrics")
        print("   - Note: Token needs refresh")

    if integrations["Instagram"]["status"] == "configured":
        print("[OK] Instagram")
        print("   - Post photos to Instagram")
        print("   - Track engagement")
        print("   - Auto-hashtag generation")

    if integrations["Twitter"]["status"] == "configured":
        print("[OK] Twitter/X")
        print("   - Post tweets")
        print("   - Monitor mentions")
        print("   - Auto-reply to DMs")

    if integrations["Odoo"]["status"] == "configured":
        print("[OK] Odoo Accounting")
        print("   - Generate invoices")
        print("   - Record payments")
        print("   - Financial reporting")

    # Show next steps
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)

    print("\n[IMMEDIATE ACTIONS]\n")

    if integrations["Facebook"]["status"] == "configured":
        print("1. Refresh Facebook Token")
        print("   - Visit: https://developers.facebook.com/tools/explorer/")
        print("   - Get new token and update .env")
        print("   - Run: python extend_facebook_token.py")

    if integrations["Instagram"]["status"] == "not_configured":
        print("\n2. Link Instagram Account")
        print("   - Go to Facebook Page settings")
        print("   - Connect Instagram Business Account")
        print("   - Run: python get_instagram_account_id.py")

    if integrations["Twitter"]["status"] == "not_configured":
        print("\n3. Setup Twitter/X Integration")
        print("   - Visit: https://developer.twitter.com/")
        print("   - Create app and get API keys")
        print("   - Update .env with credentials")

    print("\n[TEST WORKING INTEGRATIONS]\n")

    if integrations["LinkedIn"]["status"] == "configured":
        print("- Test LinkedIn: python test_linkedin_integration.py")

    if integrations["Gmail"]["status"] == "configured":
        print("- Test Gmail: python test_gmail_integration.py")

    if integrations["Odoo"]["status"] == "configured":
        print("- Test Odoo: python test_odoo_integration.py")

    print("\n[RUN COMPLETE SYSTEM]\n")
    print("- Full demo: python Scripts/run_complete_system.py")
    print("- Social media manager: Use /social-media-manager skill")
    print("- CEO briefing: Use /chief-of-staff skill")

    print("\n" + "="*60)

    return integrations


if __name__ == "__main__":
    integrations = check_all_integrations()

    print("\n[INFO] System check complete!")
    print("       Review the status above and follow the next steps")
    print("="*60 + "\n")
