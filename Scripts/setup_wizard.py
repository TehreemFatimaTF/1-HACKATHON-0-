"""
Interactive API Setup Wizard for Gold Tier AI Employee

This wizard guides you through setting up all API credentials step-by-step.
It will:
1. Check current configuration status
2. Guide you through each API setup
3. Test connections as you go
4. Update .env file automatically

Usage:
    python setup_wizard.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key
from colorama import init, Fore, Style
import webbrowser

# Initialize colorama
init(autoreset=True)

# Load environment variables
ENV_FILE = Path(".env")
load_dotenv(ENV_FILE)

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text.center(70)}")
    print(f"{Fore.CYAN}{'='*70}\n")

def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠️  {text}")

def print_info(text):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ️  {text}")

def print_step(number, text):
    """Print step number"""
    print(f"\n{Fore.MAGENTA}📍 Step {number}: {text}")
    print(f"{Fore.MAGENTA}{'-'*70}")

def get_input(prompt, default=None):
    """Get user input with optional default"""
    if default:
        user_input = input(f"{Fore.YELLOW}➤ {prompt} [{default}]: {Style.RESET_ALL}")
        return user_input if user_input else default
    else:
        return input(f"{Fore.YELLOW}➤ {prompt}: {Style.RESET_ALL}")

def confirm(prompt):
    """Ask for yes/no confirmation"""
    response = input(f"{Fore.YELLOW}➤ {prompt} (y/n): {Style.RESET_ALL}").lower()
    return response in ['y', 'yes']

def save_to_env(key, value):
    """Save credential to .env file"""
    try:
        set_key(ENV_FILE, key, value)
        print_success(f"Saved {key} to .env")
        return True
    except Exception as e:
        print_error(f"Failed to save {key}: {e}")
        return False

def check_existing_config():
    """Check which APIs are already configured"""
    print_header("🔍 Checking Current Configuration")

    configs = {
        "LinkedIn": bool(os.getenv("LINKEDIN_EMAIL") and os.getenv("LINKEDIN_PASSWORD")),
        "Gmail": bool(os.getenv("GMAIL_EMAIL") and os.getenv("GMAIL_APP_PASSWORD")),
        "Twitter": bool(os.getenv("TWITTER_API_KEY") and not os.getenv("TWITTER_API_KEY", "").startswith("your_")),
        "Facebook": bool(os.getenv("FACEBOOK_APP_ID") and not os.getenv("FACEBOOK_APP_ID", "").startswith("your_")),
        "Instagram": bool(os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID") and not os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "").startswith("your_")),
        "Odoo": bool(os.getenv("ODOO_URL") and os.getenv("ODOO_USERNAME"))
    }

    for service, configured in configs.items():
        if configured:
            print_success(f"{service}: Configured")
        else:
            print_warning(f"{service}: Not configured")

    return configs

def setup_twitter():
    """Interactive Twitter API setup"""
    print_header("🐦 Twitter/X API Setup")

    print_info("You'll need a Twitter Developer account to get API credentials.")
    print_info("This will take about 10 minutes.")
    print()

    if not confirm("Do you want to set up Twitter API now?"):
        print_warning("Skipping Twitter setup")
        return False

    print_step(1, "Open Twitter Developer Portal")
    print_info("Opening https://developer.twitter.com/en/portal/dashboard")

    if confirm("Open in browser?"):
        webbrowser.open("https://developer.twitter.com/en/portal/dashboard")

    print()
    print_info("Follow these steps:")
    print("  1. Sign in with your Twitter account")
    print("  2. Click 'Create Project' or use existing project")
    print("  3. Create an app (name: sana-ai-employee-bot)")
    print("  4. Go to 'Keys and tokens' tab")
    print()

    input(f"{Fore.YELLOW}Press Enter when you have your API credentials ready...{Style.RESET_ALL}")

    print_step(2, "Enter API Credentials")

    api_key = get_input("API Key (Consumer Key)")
    if api_key:
        save_to_env("TWITTER_API_KEY", api_key)

    api_secret = get_input("API Secret (Consumer Secret)")
    if api_secret:
        save_to_env("TWITTER_API_SECRET", api_secret)

    bearer_token = get_input("Bearer Token")
    if bearer_token:
        save_to_env("TWITTER_BEARER_TOKEN", bearer_token)

    print()
    print_info("Now generate Access Token & Secret:")
    print("  1. Scroll down to 'Authentication Tokens'")
    print("  2. Click 'Generate' under 'Access Token and Secret'")
    print()

    input(f"{Fore.YELLOW}Press Enter when ready...{Style.RESET_ALL}")

    access_token = get_input("Access Token")
    if access_token:
        save_to_env("TWITTER_ACCESS_TOKEN", access_token)

    access_secret = get_input("Access Token Secret")
    if access_secret:
        save_to_env("TWITTER_ACCESS_TOKEN_SECRET", access_secret)

    print_step(3, "Testing Connection")
    try:
        from src.mcp.twitter_client import TwitterClient
        client = TwitterClient()
        if client.health_check():
            print_success("Twitter API connected successfully!")
            return True
        else:
            print_error("Connection test failed. Check your credentials.")
            return False
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False

def setup_facebook():
    """Interactive Facebook API setup"""
    print_header("📘 Facebook API Setup")

    print_info("You'll need a Facebook Developer account and a Facebook Page.")
    print_info("This will take about 15 minutes.")
    print()

    if not confirm("Do you want to set up Facebook API now?"):
        print_warning("Skipping Facebook setup")
        return False

    print_step(1, "Open Facebook Developers")
    print_info("Opening https://developers.facebook.com/apps/")

    if confirm("Open in browser?"):
        webbrowser.open("https://developers.facebook.com/apps/")

    print()
    print_info("Follow these steps:")
    print("  1. Click 'Create App'")
    print("  2. Choose 'Business' type")
    print("  3. App name: Sana AI Employee")
    print("  4. Go to Settings → Basic")
    print()

    input(f"{Fore.YELLOW}Press Enter when you have your App ID and Secret...{Style.RESET_ALL}")

    print_step(2, "Enter App Credentials")

    app_id = get_input("App ID")
    if app_id:
        save_to_env("FACEBOOK_APP_ID", app_id)

    app_secret = get_input("App Secret")
    if app_secret:
        save_to_env("FACEBOOK_APP_SECRET", app_secret)

    print_step(3, "Get Page Access Token")
    print_info("Opening Graph API Explorer...")

    if confirm("Open Graph API Explorer?"):
        webbrowser.open("https://developers.facebook.com/tools/explorer/")

    print()
    print_info("In Graph API Explorer:")
    print("  1. Select your app from dropdown")
    print("  2. Click 'Generate Access Token'")
    print("  3. Grant these permissions:")
    print("     - pages_show_list")
    print("     - pages_manage_posts")
    print("     - pages_read_engagement")
    print("  4. Copy the access token")
    print()
    print_warning("Note: This is a short-lived token. We'll convert it to long-lived.")
    print()

    input(f"{Fore.YELLOW}Press Enter when ready...{Style.RESET_ALL}")

    short_token = get_input("Short-lived Access Token")

    if short_token and app_id and app_secret:
        print_info("Converting to long-lived token...")
        try:
            import requests
            response = requests.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": app_id,
                    "client_secret": app_secret,
                    "fb_exchange_token": short_token
                }
            )
            if response.ok:
                long_token = response.json().get("access_token")
                print_success("Got long-lived token!")

                # Get page token
                print_info("Getting page access token...")
                response = requests.get(
                    "https://graph.facebook.com/v18.0/me/accounts",
                    params={"access_token": long_token}
                )
                if response.ok:
                    pages = response.json().get("data", [])
                    if pages:
                        print()
                        print_info("Your Facebook Pages:")
                        for i, page in enumerate(pages, 1):
                            print(f"  {i}. {page['name']} (ID: {page['id']})")

                        page_num = int(get_input("Select page number", "1")) - 1
                        if 0 <= page_num < len(pages):
                            page = pages[page_num]
                            save_to_env("FACEBOOK_ACCESS_TOKEN", page["access_token"])
                            save_to_env("FACEBOOK_PAGE_ID", page["id"])
                            print_success(f"Configured page: {page['name']}")
                        else:
                            print_error("Invalid page number")
                    else:
                        print_error("No pages found. Make sure you're admin of a page.")
                else:
                    print_error("Failed to get pages")
            else:
                print_error("Failed to get long-lived token")
        except Exception as e:
            print_error(f"Error: {e}")
            print_info("You can manually add FACEBOOK_ACCESS_TOKEN to .env")

    print_step(4, "Testing Connection")
    try:
        from src.mcp.facebook_client import FacebookClient
        client = FacebookClient()
        if client.health_check():
            print_success("Facebook API connected successfully!")
            return True
        else:
            print_error("Connection test failed. Check your credentials.")
            return False
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False

def setup_instagram():
    """Interactive Instagram API setup"""
    print_header("📸 Instagram API Setup")

    print_info("Instagram uses Facebook Graph API.")
    print_info("You need: Instagram Business account + Facebook Page")
    print_info("This will take about 10 minutes.")
    print()

    if not confirm("Do you want to set up Instagram API now?"):
        print_warning("Skipping Instagram setup")
        return False

    print_step(1, "Convert Instagram to Business Account")
    print_info("On your phone:")
    print("  1. Open Instagram app")
    print("  2. Go to Profile → Menu → Settings")
    print("  3. Account → Switch to Professional Account")
    print("  4. Choose 'Business' or 'Creator'")
    print()

    input(f"{Fore.YELLOW}Press Enter when done...{Style.RESET_ALL}")

    print_step(2, "Connect Instagram to Facebook Page")
    print_info("On Facebook:")
    print("  1. Go to your Facebook Page")
    print("  2. Settings → Instagram")
    print("  3. Click 'Connect Account'")
    print("  4. Log in to Instagram")
    print()

    input(f"{Fore.YELLOW}Press Enter when connected...{Style.RESET_ALL}")

    print_step(3, "Get Instagram Business Account ID")

    page_id = os.getenv("FACEBOOK_PAGE_ID")
    page_token = os.getenv("FACEBOOK_ACCESS_TOKEN")

    if page_id and page_token:
        print_info("Using Facebook credentials from previous setup...")
        try:
            import requests
            response = requests.get(
                f"https://graph.facebook.com/v18.0/{page_id}",
                params={
                    "fields": "instagram_business_account",
                    "access_token": page_token
                }
            )
            if response.ok:
                ig_account = response.json().get("instagram_business_account")
                if ig_account:
                    ig_id = ig_account["id"]
                    save_to_env("INSTAGRAM_BUSINESS_ACCOUNT_ID", ig_id)
                    save_to_env("INSTAGRAM_ACCESS_TOKEN", page_token)
                    print_success(f"Instagram Business ID: {ig_id}")
                else:
                    print_error("No Instagram account linked to this page")
                    print_info("Make sure Instagram is connected to Facebook Page")
            else:
                print_error("Failed to get Instagram account")
        except Exception as e:
            print_error(f"Error: {e}")
    else:
        print_warning("Facebook not configured. Set up Facebook first.")
        ig_id = get_input("Instagram Business Account ID (manual entry)")
        if ig_id:
            save_to_env("INSTAGRAM_BUSINESS_ACCOUNT_ID", ig_id)

    print_step(4, "Testing Connection")
    try:
        from src.mcp.instagram_client import InstagramClient
        client = InstagramClient()
        if client.health_check():
            print_success("Instagram API connected successfully!")
            return True
        else:
            print_error("Connection test failed. Check your credentials.")
            return False
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False

def main():
    """Main wizard flow"""
    print_header("🚀 Gold Tier AI Employee - API Setup Wizard")

    print(f"{Fore.CYAN}This wizard will help you set up API credentials for:")
    print(f"{Fore.CYAN}  • Twitter/X (10 min)")
    print(f"{Fore.CYAN}  • Facebook (15 min)")
    print(f"{Fore.CYAN}  • Instagram (10 min)")
    print()
    print_info("You can skip any platform and set it up later.")
    print_info("All credentials are saved to .env file.")
    print()

    if not confirm("Ready to start?"):
        print_warning("Setup cancelled")
        return

    # Check current status
    configs = check_existing_config()

    # Setup each platform
    results = {}

    if not configs["Twitter"]:
        results["Twitter"] = setup_twitter()
    else:
        print_info("Twitter already configured (skipping)")
        results["Twitter"] = True

    if not configs["Facebook"]:
        results["Facebook"] = setup_facebook()
    else:
        print_info("Facebook already configured (skipping)")
        results["Facebook"] = True

    if not configs["Instagram"]:
        results["Instagram"] = setup_instagram()
    else:
        print_info("Instagram already configured (skipping)")
        results["Instagram"] = True

    # Final summary
    print_header("📊 Setup Complete!")

    print_info("Configuration Summary:")
    for service, status in results.items():
        if status:
            print_success(f"{service}: Configured and tested")
        else:
            print_warning(f"{service}: Skipped or failed")

    print()
    print_info("Next steps:")
    print("  1. Run: python test_api_connections.py")
    print("  2. Run: demo.bat (to see full demo)")
    print("  3. Start using: python src/watcher.py")
    print()

    if confirm("Run connection tests now?"):
        print()
        os.system("python test_api_connections.py")

    print()
    print_success("Setup wizard complete! 🎉")
    print_info("Check API_SETUP_SUMMARY.md for detailed guides")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
