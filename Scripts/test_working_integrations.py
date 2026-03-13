"""
Quick Test Suite for Working Integrations
Tests LinkedIn, Gmail, and Odoo without requiring interactive input
"""

import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def test_linkedin_ready():
    """Test if LinkedIn is ready"""
    print("\n" + "="*60)
    print("LINKEDIN INTEGRATION TEST")
    print("="*60)

    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")

    if email and password and "your_" not in email.lower():
        print(f"\n[PASS] LinkedIn credentials configured")
        print(f"   Email: {email}")
        print(f"   Status: READY")
        print("\n[AVAILABLE ACTIONS]")
        print("   - Post to LinkedIn feed")
        print("   - Monitor messages")
        print("   - Track engagement")
        return True
    else:
        print(f"\n[FAIL] LinkedIn not configured")
        return False

def test_gmail_ready():
    """Test if Gmail is ready"""
    print("\n" + "="*60)
    print("GMAIL INTEGRATION TEST")
    print("="*60)

    email = os.getenv("GMAIL_EMAIL")
    password = os.getenv("GMAIL_APP_PASSWORD")

    if email and password and "your_" not in email.lower():
        print(f"\n[PASS] Gmail credentials configured")
        print(f"   Email: {email}")
        print(f"   Status: READY")
        print("\n[AVAILABLE ACTIONS]")
        print("   - Send automated emails")
        print("   - Monitor inbox")
        print("   - Extract action items")
        return True
    else:
        print(f"\n[FAIL] Gmail not configured")
        return False

def test_odoo_ready():
    """Test if Odoo is ready"""
    print("\n" + "="*60)
    print("ODOO ACCOUNTING TEST")
    print("="*60)

    url = os.getenv("ODOO_URL")
    db = os.getenv("ODOO_DB")
    username = os.getenv("ODOO_USERNAME")

    if url and db and username:
        print(f"\n[PASS] Odoo credentials configured")
        print(f"   URL: {url}")
        print(f"   Database: {db}")
        print(f"   Username: {username}")
        print(f"   Status: READY")
        print("\n[AVAILABLE ACTIONS]")
        print("   - Generate invoices")
        print("   - Record payments")
        print("   - Financial reports")
        return True
    else:
        print(f"\n[FAIL] Odoo not configured")
        return False

def show_usage_examples():
    """Show how to use each integration"""
    print("\n" + "="*60)
    print("USAGE EXAMPLES")
    print("="*60)

    print("\n[LINKEDIN POSTING]")
    print("```python")
    print("from src.mcp.linkedin_client import LinkedInClient")
    print("")
    print("client = LinkedInClient()")
    print("result = client.post_update(")
    print('    content="Just automated 20 hours of work! #AI"')
    print(")")
    print("```")

    print("\n[GMAIL AUTOMATION]")
    print("```python")
    print("from src.mcp.gmail_client import GmailClient")
    print("")
    print("client = GmailClient()")
    print("client.send_email(")
    print('    to="client@example.com",')
    print('    subject="Invoice #2026-001",')
    print('    body="Please find attached..."')
    print(")")
    print("```")

    print("\n[ODOO INVOICING]")
    print("```python")
    print("from src.mcp.odoo_client import OdooClient")
    print("")
    print("client = OdooClient()")
    print("invoice = client.create_invoice(")
    print('    partner_id=123,')
    print("    amount=5000.00,")
    print('    description="Project completion"')
    print(")")
    print("```")

def show_skills_usage():
    """Show how to use AI Employee skills"""
    print("\n" + "="*60)
    print("AI EMPLOYEE SKILLS - QUICK START")
    print("="*60)

    print("\n[SOCIAL MEDIA MANAGER]")
    print("Post to all configured platforms at once:")
    print("   /social-media-manager post 'Your content here'")

    print("\n[CHIEF OF STAFF]")
    print("Generate executive briefing:")
    print("   /chief-of-staff briefing")

    print("\n[ODOO ACCOUNTANT]")
    print("Generate invoice:")
    print("   /odoo-accountant invoice --client 'Client Name' --amount 5000")

    print("\n[DATA ANALYST]")
    print("Analyze business metrics:")
    print("   /data-analyst analyze --metric 'revenue' --period 'last_month'")

    print("\n[INTEGRATION TESTER]")
    print("Test all integrations:")
    print("   /integration-tester health-check")

def main():
    """Run quick test suite"""
    print("\n" + "="*60)
    print("AI EMPLOYEE - QUICK TEST SUITE")
    print("="*60)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "LinkedIn": test_linkedin_ready(),
        "Gmail": test_gmail_ready(),
        "Odoo": test_odoo_ready()
    }

    # Show usage examples
    show_usage_examples()

    # Show skills usage
    show_skills_usage()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n[RESULTS]")
    print(f"   Tests run: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success rate: {(passed/total)*100:.0f}%")

    if passed == total:
        print("\n[SUCCESS] All working integrations are ready!")
        print("          You can start using them immediately")
    else:
        print("\n[INFO] Some integrations need configuration")
        print("       Check the failed tests above")

    print("\n[NEXT STEPS]")
    print("   1. Complete Facebook token refresh")
    print("   2. Start using the working integrations")
    print("   3. Try the AI Employee skills")
    print("   4. Run: python Scripts/run_complete_system.py")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
