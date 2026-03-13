"""
Quick Facebook Token Refresh
Gets a new Facebook access token in 2 minutes
"""

print("\n" + "="*60)
print("FACEBOOK TOKEN REFRESH - QUICK GUIDE")
print("="*60)

print("\n[STEP 1] Open this URL in your browser:")
print("https://developers.facebook.com/tools/explorer/")

print("\n[STEP 2] Select your Facebook App from the dropdown")

print("\n[STEP 3] Click 'Generate Access Token' button")

print("\n[STEP 4] Grant these permissions when asked:")
print("  - pages_show_list")
print("  - pages_read_engagement")
print("  - pages_manage_posts")
print("  - pages_manage_engagement")

print("\n[STEP 5] Copy the new token (starts with 'EAAU...')")

print("\n[STEP 6] Open .env file and replace this line:")
print("FACEBOOK_ACCESS_TOKEN=old_token_here")
print("\nWith:")
print("FACEBOOK_ACCESS_TOKEN=your_new_token_here")

print("\n[STEP 7] Save .env file (Ctrl+S)")

print("\n[STEP 8] Run this command:")
print("python get_page_access_token.py")

print("\n[STEP 9] Test posting:")
print("python social_media_post.py 'Test post'")

print("\n" + "="*60)
print("Time needed: 2 minutes")
print("="*60 + "\n")

input("Press Enter when you have the new token and updated .env file...")

print("\n[*] Now running get_page_access_token.py to convert to page token...")
import subprocess
subprocess.run(["python", "get_page_access_token.py"])
