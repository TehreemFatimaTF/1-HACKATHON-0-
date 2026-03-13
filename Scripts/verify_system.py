"""
Complete System Verification
Checks all platform credentials and provides setup guidance
"""

import os
from dotenv import load_dotenv

load_dotenv()

def check_credential(name, required_vars):
    """Check if credentials are configured"""
    missing = []
    configured = []

    for var in required_vars:
        value = os.getenv(var)
        if not value or "your_" in value.lower():
            missing.append(var)
        else:
            configured.append(var)

    return {
        "configured": len(configured),
        "total": len(required_vars),
        "missing": missing,
        "complete": len(missing) == 0
    }

def print_status(platform, status, priority="MEDIUM"):
    """Print platform status"""
    if status["complete"]:
        icon = "[OK]"
        color = "READY"
    elif status["configured"] > 0:
        icon = "[~]"
        color = "PARTIAL"
    else:
        icon = "[X]"
        color = "NOT CONFIGURED"

    print(f"\n{icon} {platform}")
    print(f"    Status: {color}")
    print(f"    Configured: {status['configured']}/{status['total']} credentials")

    if status["missing"]:
        print(f"    Missing: {', '.join(status['missing'])}")
        print(f"    Priority: {priority}")

def main():
    print("\n" + "="*70)
    print("  AI EMPLOYEE SYSTEM - CREDENTIAL VERIFICATION")
    print("="*70)

    platforms = {
        "Facebook": {
            "vars": ["FACEBOOK_APP_ID", "FACEBOOK_PAGE_ID", "FACEBOOK_ACCESS_TOKEN"],
            "priority": "HIGH",
            "guide": "REFRESH_FACEBOOK_TOKEN.md",
            "time": "2 minutes",
            "action": "Get new token from Graph API Explorer"
        },
        "LinkedIn": {
            "vars": ["LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET", "LINKEDIN_ACCESS_TOKEN"],
            "priority": "HIGH",
            "guide": "LINKEDIN_COMPLETE_SETUP.md",
            "time": "10 minutes",
            "action": "Get OAuth credentials from Developer Portal"
        },
        "Twitter": {
            "vars": ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET"],
            "priority": "MEDIUM",
            "guide": "TWITTER_SETUP_GUIDE.md",
            "time": "2 minutes",
            "action": "Redeem voucher: ALLA-HPAK-JAN"
        },
        "Gmail": {
            "vars": ["GMAIL_EMAIL", "GMAIL_APP_PASSWORD"],
            "priority": "NONE",
            "guide": None,
            "time": "0 minutes",
            "action": "Already configured"
        },
        "Odoo": {
            "vars": ["ODOO_URL", "ODOO_DB", "ODOO_USERNAME", "ODOO_PASSWORD"],
            "priority": "NONE",
            "guide": None,
            "time": "0 minutes",
            "action": "Already configured"
        },
        "Instagram": {
            "vars": ["INSTAGRAM_BUSINESS_ACCOUNT_ID", "INSTAGRAM_ACCESS_TOKEN"],
            "priority": "LOW",
            "guide": None,
            "time": "5 minutes",
            "action": "Link Instagram Business Account (optional)"
        }
    }

    # Check all platforms
    results = {}
    for platform, info in platforms.items():
        results[platform] = check_credential(platform, info["vars"])

    # Print status
    print("\n" + "="*70)
    print("  PLATFORM STATUS")
    print("="*70)

    for platform, info in platforms.items():
        print_status(platform, results[platform], info["priority"])

    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)

    total = len(platforms)
    ready = sum(1 for r in results.values() if r["complete"])
    partial = sum(1 for r in results.values() if r["configured"] > 0 and not r["complete"])
    not_configured = sum(1 for r in results.values() if r["configured"] == 0)

    completion = (ready / total) * 100

    print(f"\n  Total Platforms: {total}")
    print(f"  Ready: {ready}")
    print(f"  Partial: {partial}")
    print(f"  Not Configured: {not_configured}")
    print(f"  Completion: {completion:.0f}%")

    # Next steps
    print("\n" + "="*70)
    print("  RECOMMENDED NEXT STEPS")
    print("="*70)

    steps = []
    for platform, info in platforms.items():
        if not results[platform]["complete"] and info["priority"] != "NONE":
            steps.append({
                "platform": platform,
                "priority": info["priority"],
                "time": info["time"],
                "action": info["action"],
                "guide": info["guide"]
            })

    # Sort by priority
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    steps.sort(key=lambda x: priority_order.get(x["priority"], 3))

    if steps:
        for i, step in enumerate(steps, 1):
            print(f"\n  [{i}] {step['platform']} ({step['time']})")
            print(f"      Priority: {step['priority']}")
            print(f"      Action: {step['action']}")
            if step['guide']:
                print(f"      Guide: {step['guide']}")
    else:
        print("\n  [SUCCESS] All platforms configured!")
        print("  You're ready to start using your AI Employee!")

    # Quick actions
    print("\n" + "="*70)
    print("  QUICK ACTIONS")
    print("="*70)

    if results["Facebook"]["complete"]:
        print("\n  [1] Test Facebook posting")
        print("      python social_media_post.py 'Test post'")

    if results["LinkedIn"]["complete"]:
        print("\n  [2] Test LinkedIn posting")
        print("      python social_media_post.py 'Test post'")

    if results["Twitter"]["complete"]:
        print("\n  [3] Test Twitter posting")
        print("      python social_media_post.py 'Test post'")

    if results["Gmail"]["complete"]:
        print("\n  [4] Test email automation")
        print("      Use Gmail client in Python scripts")

    if results["Odoo"]["complete"]:
        print("\n  [5] Test invoice generation")
        print("      Use Odoo client in Python scripts")

    print("\n  [6] View live dashboard")
    print("      python dashboard.py")

    print("\n  [7] Check detailed status")
    print("      python final_system_status.py")

    # What's working
    print("\n" + "="*70)
    print("  WHAT YOU CAN DO RIGHT NOW")
    print("="*70)

    working = [p for p, r in results.items() if r["complete"]]

    if working:
        print(f"\n  You have {len(working)} platform(s) ready:")
        for platform in working:
            print(f"    - {platform}")

        if "Gmail" in working and "Odoo" in working:
            print("\n  [WORKFLOW] Automated invoicing:")
            print("    1. Generate invoice (Odoo)")
            print("    2. Email to client (Gmail)")
            print("    3. Schedule payment reminders (Gmail)")

        if any(p in working for p in ["Facebook", "LinkedIn", "Twitter"]):
            social = [p for p in ["Facebook", "LinkedIn", "Twitter"] if p in working]
            print(f"\n  [WORKFLOW] Social media posting:")
            print(f"    Post to {', '.join(social)} with one command")
            print("    python social_media_post.py 'Your content'")
    else:
        print("\n  No platforms fully configured yet.")
        print("  Follow the recommended next steps above to get started!")

    print("\n" + "="*70)
    print(f"  System Completion: {completion:.0f}%")
    print(f"  Platforms Ready: {ready}/{total}")
    print(f"  Time to 100%: {sum(int(s['time'].split()[0]) for s in steps if s['time'] != '0 minutes')} minutes")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
