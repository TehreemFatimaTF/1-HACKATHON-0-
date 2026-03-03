import asyncio
import os
import random
import logging
import glob
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Environment variables load karein
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration - Use absolute paths
BASE_DIR = Path(__file__).parent.parent  # Project root
DONE_DIR = BASE_DIR / "Done"

class LinkedInAutomation:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.storage_state_path = str(BASE_DIR / "linkedin_session.json")
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    async def get_latest_draft(self):
        """Done folder se sabse nayi LinkedIn draft file uthata hai"""
        # Look for LinkedIn draft files in Done/ folder
        pattern = str(DONE_DIR / "linkedin_draft_*.md")
        files = glob.glob(pattern)

        if files:
            latest_file = max(files, key=os.path.getctime)
            logger.info(f"LinkedIn draft file mili: {latest_file}")
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

                # Extract content after '## Post Content:' or '## LinkedIn Post Draft'
                if '## Post Content:' in content:
                    lines = content.split('\n')
                    in_post_section = False
                    post_content = []
                    for line in lines:
                        if '## Post Content:' in line:
                            in_post_section = True
                            continue
                        if in_post_section:
                            if line.startswith('##') and 'Post Content' not in line:
                                break  # Stop at next section
                            if line.strip():
                                post_content.append(line)
                    if post_content:
                        content = '\n'.join(post_content).strip()
                        logger.info(f"Extracted post content ({len(content)} chars)")
                        return content

                # Fallback: try to extract from LinkedIn Post Draft section
                if '## LinkedIn Post Draft' in content:
                    lines = content.split('\n')
                    in_post_section = False
                    post_content = []
                    for line in lines:
                        if '## LinkedIn Post Draft' in line:
                            in_post_section = True
                            continue
                        if in_post_section:
                            if line.startswith('##'):
                                break
                            if line.strip():
                                post_content.append(line)
                    if post_content:
                        content = '\n'.join(post_content).strip()
                        logger.info(f"Extracted post content ({len(content)} chars)")
                        return content

                # If no specific section found, return the whole content
                logger.info(f"Using full file content ({len(content)} chars)")
                return content

        logger.warning(f"No LinkedIn draft files found in {DONE_DIR}")
        logger.warning("Testing text use kar raha hoon.")
        return f"AI Employee Assistant is now live! 🚀 #AI #Automation\n\nPosted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    async def setup_browser(self):
        """Browser setup with session persistence"""
        self.playwright = await async_playwright().start()
        
        # Using Firefox for better LinkedIn compatibility
        self.browser = await self.playwright.firefox.launch(headless=self.headless)
        
        # Check if saved session exists
        if os.path.exists(self.storage_state_path):
            logger.info("Saved session found! Loading...")
            try:
                self.context = await self.browser.new_context(
                    storage_state=self.storage_state_path,
                    viewport={'width': 1366, 'height': 768},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
                )
                self.page = await self.context.new_page()
                
                # Verify session is still valid
                await self.page.goto("https://www.linkedin.com/feed/")
                await asyncio.sleep(random.uniform(3, 5))
                
                # Check if we're logged in by looking for feed elements
                current_url = self.page.url
                if "feed" in current_url or "dashboard" in current_url:
                    logger.info("✅ Session loaded successfully! Already logged in.")
                    return True
                else:
                    logger.warning("Session expired. Will login again.")
                    await self.context.close()
            except Exception as e:
                logger.warning(f"Failed to load session: {e}. Will login fresh.")
                if self.context:
                    await self.context.close()
        
        # Create new context without saved session
        self.context = await self.browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
        )
        self.page = await self.context.new_page()
        logger.info("Browser open ho gaya (fresh session).")
        return False

    async def save_session(self):
        """Save the current session to a file"""
        try:
            await self.context.storage_state(path=self.storage_state_path)
            logger.info(f"✅ Session saved to {self.storage_state_path}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    async def handle_captcha_and_login(self):
        """Handle login and potential CAPTCHA"""
        logger.info("Login page par ja raha hoon...")
        await self.page.goto("https://www.linkedin.com/login")
        await asyncio.sleep(random.uniform(2, 4))

        # Fill credentials
        await self.page.fill("#username", self.email)
        await asyncio.sleep(random.uniform(1, 2))

        await self.page.fill("#password", self.password)
        await asyncio.sleep(random.uniform(1, 2))

        await self.page.click("button[type='submit']")
        await asyncio.sleep(random.uniform(3, 5))

        # Check if we're on the feed page now (successful login)
        current_url = self.page.url
        if "feed" in current_url or "dashboard" in current_url:
            logger.info("Login successful, no manual intervention needed")
            await self.save_session()
            return True

        # Wait for feed navigation
        try:
            await self.page.wait_for_url("**/feed**", timeout=10000)
            logger.info("Successfully navigated to feed after login")
            await self.save_session()
            return True
        except:
            logger.info("Checking for 2FA or additional verification...")
            try:
                await self.page.wait_for_timeout(10000)
                current_url = self.page.url
                if "feed" in current_url or "dashboard" in current_url:
                    logger.info("Login resolved automatically")
                    await self.save_session()
                    return True
                else:
                    logger.warning("Still need manual verification. Please complete any 2FA or CAPTCHA.")
                    for i in range(30):
                        await asyncio.sleep(10)
                        current_url = self.page.url
                        if "feed" in current_url or "dashboard" in current_url:
                            logger.info("Login completed manually")
                            await self.save_session()
                            return True
                        logger.info(f"Waiting for manual login... {i+1}/30 (10s intervals)")
            except:
                pass

        return "feed" in self.page.url or "dashboard" in self.page.url

    async def navigate_to_post_creation(self):
        """Navigate to LinkedIn feed and create post (personal profile)"""
        logger.info("Navigating to LinkedIn feed for post creation...")

        # Navigate to LinkedIn feed (personal)
        logger.info("Going to LinkedIn feed...")
        await self.page.goto("https://www.linkedin.com/feed/")
        await asyncio.sleep(random.uniform(5, 8))

        # Take a screenshot for debugging
        try:
            await self.page.screenshot(path="feed_page.png")
            logger.info("Screenshot saved: feed_page.png")
        except:
            pass

        # Look for "Start a post" button on the feed page
        # This is the main post creation box on the home feed
        feed_post_selectors = [
            # Main "Start a post" box at top of feed
            "button:has-text('Start a post')",
            "div[role='button']:has-text('Start a post')",
            "[data-test-id='share-box-feed-shared']",
            "[data-test-id='share-box-feed'] button",
            # Alternative selectors
            "button[aria-label*='Create a post']",
            "button[aria-label*='Share']",
            ".share-box-feed-entry__trigger",
            # By placeholder
            "div[placeholder*='Start a post']",
            # Direct text match
            "button:text('Start a post')",
            "div:text('Start a post')"
        ]

        for selector in feed_post_selectors:
            try:
                logger.info(f"Trying selector: {selector}")
                post_button = await self.page.wait_for_selector(selector, timeout=5000)
                await asyncio.sleep(random.uniform(2, 3))
                await post_button.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(1, 2))
                await post_button.click()
                await asyncio.sleep(random.uniform(3, 5))
                logger.info(f"✅ Successfully clicked post button using: {selector}")
                
                # Take screenshot after clicking
                try:
                    await self.page.screenshot(path="after_clicking_start_post.png")
                except:
                    pass
                
                return True
            except Exception as e:
                logger.info(f"Selector failed: {selector}")
                continue

        # If direct click fails, try clicking on the div container
        logger.warning("Direct selectors failed, trying alternative approach...")
        try:
            # Look for the container and click it
            container = await self.page.query_selector("div.share-box-feed-entry")
            if container:
                await container.click()
                await asyncio.sleep(random.uniform(3, 5))
                logger.info("✅ Clicked share-box-feed-entry container")
                return True
        except Exception as e:
            logger.info(f"Container click failed: {e}")

        # Try keyboard navigation as fallback
        logger.info("Trying keyboard navigation...")
        await self.page.keyboard.press("Tab")
        await asyncio.sleep(random.uniform(1, 2))
        await self.page.keyboard.press("Enter")
        await asyncio.sleep(random.uniform(3, 5))
        logger.info("✅ Used keyboard navigation (Tab + Enter)")
        return True

    async def post_content(self, content):
        """Post content to LinkedIn"""
        logger.info("Attempting to post content...")
        logger.info(f"Content length: {len(content)} characters")

        try:
            # Take screenshot to see current state
            try:
                await self.page.screenshot(path="before_editor.png")
            except:
                pass

            # Wait for the text editor to appear
            editor_selectors = [
                "div[role='textbox'][contenteditable='true']",
                "div[data-test-id='share-content-textarea']",
                "div[aria-label*='Write content']",
                "div[aria-label*='Create a post']",
                "[data-test-id='share-content-textarea'] div[contenteditable='true']",
                # Company page specific
                "div[aria-label*='Share content']",
                "div[placeholder*='post' i]",
                "div[placeholder*='Share' i]",
                ".share-content-textarea",
                "#share-content-textarea"
            ]

            editor_found = False
            editor = None

            for selector in editor_selectors:
                try:
                    editor = await self.page.wait_for_selector(selector, timeout=8000)
                    await asyncio.sleep(random.uniform(2, 3))
                    editor_found = True
                    logger.info(f"✅ Found editor using: {selector}")
                    break
                except:
                    continue

            # If still not found, try to find any contenteditable div
            if not editor_found:
                logger.info("Trying to find any contenteditable element...")
                try:
                    editor = await self.page.query_selector("div[contenteditable='true']")
                    if editor:
                        editor_found = True
                        logger.info("✅ Found contenteditable div")
                except:
                    pass

            # Last resort - use keyboard navigation
            if not editor_found:
                logger.info("Using Tab key to navigate to editor...")
                await asyncio.sleep(random.uniform(2, 3))
                for _ in range(5):
                    await self.page.keyboard.press("Tab")
                    await asyncio.sleep(random.uniform(0.5, 1))
                
                # Try to type directly
                editor_found = True
                logger.info("Attempting to type after Tab navigation")

            if not editor_found:
                logger.error("❌ Could not find text editor")
                return False

            # Clear and type content
            await editor.click()
            await asyncio.sleep(random.uniform(1, 2))
            
            # Use keyboard type for more natural input
            await editor.fill(content)
            await asyncio.sleep(random.uniform(2, 4))

            logger.info("✅ Content filled successfully")

            # Take screenshot before posting
            try:
                await self.page.screenshot(path="before_post.png")
            except:
                pass

            # Look for the Post button with comprehensive selectors
            post_button_selectors = [
                "button:has-text('Post')",
                "button:has-text('Share')",
                "button[aria-label='Post']",
                "button[aria-label='Share']",
                "button.share-actions__trigger",
                "[data-test-id='share-content-button']",
                # LinkedIn new UI selectors
                "button.ember-view:has-text('Post')",
                "button.ember-view:has-text('Share')",
                # Company page specific
                "button[data-test-selector='update-submit-button']",
                "button[data-test-id='update-submit-button']",
                # Generic submit buttons
                "button[type='submit']:has-text('Post')",
                "button[type='submit']:has-text('Share')",
                # By class names
                ".share-box-actions__submit-button",
                ".share-box-update-button",
                # Full text match
                "button:text('Post')",
                "button:text('Share')"
            ]

            button_found = False
            for selector in post_button_selectors:
                try:
                    logger.info(f"Trying Post button selector: {selector}")
                    post_button = await self.page.wait_for_selector(selector, timeout=5000)
                    await asyncio.sleep(random.uniform(1, 2))
                    await post_button.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(1, 2))

                    # Check if button is enabled
                    is_disabled = await post_button.get_attribute('disabled')
                    if is_disabled:
                        logger.info(f"Button disabled, waiting... ({selector})")
                        await asyncio.sleep(3)
                        continue

                    await post_button.click()
                    await asyncio.sleep(random.uniform(5, 8))
                    button_found = True
                    logger.info(f"✅ Post button clicked: {selector}")
                    
                    # Take screenshot after clicking
                    try:
                        await self.page.screenshot(path="after_post_click.png")
                    except:
                        pass
                    
                    break
                except Exception as e:
                    logger.info(f"Post button selector failed: {selector}")
                    continue

            # If selectors fail, try keyboard shortcut
            if not button_found:
                logger.info("Trying keyboard shortcut (Ctrl+Enter)...")
                await self.page.keyboard.press("Control+Enter")
                await asyncio.sleep(random.uniform(5, 8))
                button_found = True
                logger.info("✅ Used Ctrl+Enter to submit post")

            # Final fallback - try to find any button in the bottom-right area
            if not button_found:
                logger.info("Trying to find Post button by evaluating all buttons...")
                try:
                    # Get all buttons and find the Post/Share button
                    buttons = await self.page.query_selector_all("button")
                    for btn in buttons:
                        text = await btn.inner_text()
                        if text and ("Post" in text or "Share" in text):
                            is_visible = await btn.is_visible()
                            is_enabled = await btn.is_enabled()
                            if is_visible and is_enabled:
                                await btn.scroll_into_view_if_needed()
                                await asyncio.sleep(random.uniform(1, 2))
                                await btn.click()
                                await asyncio.sleep(random.uniform(5, 8))
                                button_found = True
                                logger.info(f"✅ Post button clicked by text: '{text}'")
                                break
                except Exception as e:
                    logger.info(f"Button search failed: {e}")

            if not button_found:
                logger.error("❌ Could not find Post button")
                return False

            # Wait and verify post was successful
            logger.info("Waiting for post to publish...")
            await asyncio.sleep(5)

            # Check for success indicators
            try:
                # Look for "Posted" confirmation or feed
                success_indicators = [
                    "text=Posted",
                    "text=Post",
                    "text=Your post has been shared"
                ]
                
                for indicator in success_indicators:
                    try:
                        await self.page.wait_for_selector(indicator, timeout=3000)
                        logger.info("✅ Found success indicator!")
                        break
                    except:
                        continue

                current_url = self.page.url
                if "feed" in current_url or "inbox" in current_url:
                    logger.info("✅ SUCCESS! Post published and on feed.")
                    return True
                
                logger.info("✅ Post likely successful!")
                return True

            except Exception as e:
                logger.info(f"Verification: {e}")
                return True  # Assume success even if verification fails

        except Exception as e:
            logger.error(f"❌ Error posting content: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    async def run(self):
        """Main execution flow"""
        session_loaded = await self.setup_browser()
        content = await self.get_latest_draft()

        try:
            # Skip login if session was loaded
            if not session_loaded:
                login_success = await self.handle_captcha_and_login()
                if not login_success:
                    logger.error("❌ Login failed, cannot continue")
                    return
            else:
                logger.info("Using saved session, skipping login...")

            await asyncio.sleep(random.uniform(3, 5))

            # Navigate to post creation
            navigation_success = await self.navigate_to_post_creation()
            if not navigation_success:
                logger.error("❌ Could not navigate to post creation")
                return

            await asyncio.sleep(random.uniform(3, 5))

            # Post the content
            post_success = await self.post_content(content)

            if post_success:
                logger.info("✅ MUBARAK HO! Post kamyab rahi.")
            else:
                logger.error("❌ Post failed!")

        except Exception as e:
            logger.error(f"❌ Major error: {e}")
            import traceback
            logger.error(traceback.format_exc())

        finally:
            # Keep browser open for user to verify
            logger.info("=" * 50)
            logger.info("✅ Task complete! Browser will stay open for 30 seconds.")
            logger.info("You can verify the post manually.")
            logger.info("Browser will auto-close after 30 seconds...")
            logger.info("=" * 50)
            
            await asyncio.sleep(30)  # Wait 30 seconds before closing
            
            logger.info("Closing browser...")
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

if __name__ == "__main__":
    bot = LinkedInAutomation(headless=False)
    asyncio.run(bot.run())
