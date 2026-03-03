import time
import os
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEEDS_ACTION_DIR = os.path.join(BASE_DIR, "Needs_Action")
LOGS_DIR = os.path.join(BASE_DIR, "Logs")
SESSION_PATH = os.path.expanduser("~/whatsapp_session")

# Keywords to monitor
KEYWORDS = ["urgent", "asap", "invoice", "payment"]

# Ensure directories exist
for directory in [NEEDS_ACTION_DIR, LOGS_DIR, SESSION_PATH]:
    if not os.path.exists(directory):
        os.makedirs(directory)


class WhatsAppWatcher:
    """Monitors WhatsApp Web for new messages with specific keywords"""

    def __init__(self):
        self.running = False
        self.log_file = os.path.join(LOGS_DIR, "watcher_whatsapp.log")
        self.check_interval = 30  # 30 seconds
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.processed_messages = set()

    def log(self, message, level="INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [WHATSAPP] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def initialize_browser(self):
        """Initialize Playwright browser with persistent context"""
        try:
            self.log("Initializing Playwright browser...")
            self.playwright = sync_playwright().start()

            # Launch browser with persistent context to save session
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=SESSION_PATH,
                headless=False,  # Must be False for QR code scan
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ],
                viewport={'width': 1280, 'height': 720}
            )

            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            self.log("Browser initialized successfully")
            return True

        except Exception as e:
            self.log(f"Failed to initialize browser: {e}", "ERROR")
            return False

    def login_whatsapp(self):
        """Navigate to WhatsApp Web and handle QR code scan if needed"""
        try:
            self.log("Navigating to WhatsApp Web...")
            self.page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=60000)

            # Check if already logged in by looking for chat list
            try:
                self.page.wait_for_selector('div[aria-label="Chat list"]', timeout=5000)
                self.log("Already logged in to WhatsApp Web")
                return True
            except PlaywrightTimeout:
                pass

            # Check for QR code - need to scan
            try:
                qr_code = self.page.wait_for_selector('canvas[aria-label="Scan this QR code to link a device!"]', timeout=10000)
                if qr_code:
                    self.log("=" * 60, "SYSTEM")
                    self.log("QR CODE DETECTED - FIRST TIME SETUP", "SYSTEM")
                    self.log("=" * 60, "SYSTEM")
                    self.log("INSTRUCTIONS:", "SYSTEM")
                    self.log("1. Look at the browser window that just opened", "SYSTEM")
                    self.log("2. You should see a QR code on the screen", "SYSTEM")
                    self.log("3. Open WhatsApp on your phone", "SYSTEM")
                    self.log("4. Tap the 3 dots (menu) → Linked Devices", "SYSTEM")
                    self.log("5. Tap 'Link a Device'", "SYSTEM")
                    self.log("6. Scan the QR code shown in the browser", "SYSTEM")
                    self.log("=" * 60, "SYSTEM")
                    self.log("Waiting for QR code scan (timeout: 5 minutes)...", "SYSTEM")
                    self.log("Please scan now...", "SYSTEM")

                    # Wait for successful login (chat list appears)
                    self.page.wait_for_selector('div[aria-label="Chat list"]', timeout=300000)  # 5 minutes
                    self.log("=" * 60, "SYSTEM")
                    self.log("✓ QR CODE SCANNED SUCCESSFULLY!", "SYSTEM")
                    self.log("✓ Session saved for future use", "SYSTEM")
                    self.log("✓ You won't need to scan again!", "SYSTEM")
                    self.log("=" * 60, "SYSTEM")

                    # Give WhatsApp time to fully load
                    time.sleep(5)
                    return True

            except PlaywrightTimeout:
                self.log("=" * 60, "ERROR")
                self.log("QR CODE SCAN TIMEOUT!", "ERROR")
                self.log("=" * 60, "ERROR")
                self.log("The QR code was not scanned within 5 minutes.", "ERROR")
                self.log("", "ERROR")
                self.log("TROUBLESHOOTING:", "ERROR")
                self.log("1. Make sure the browser window is visible", "ERROR")
                self.log("2. Check if QR code is displayed on screen", "ERROR")
                self.log("3. Try running the watcher again", "ERROR")
                self.log("4. If QR code doesn't appear, delete session:", "ERROR")
                self.log("   rm -rf ~/whatsapp_session", "ERROR")
                self.log("=" * 60, "ERROR")
                return False

        except Exception as e:
            self.log(f"Error during WhatsApp login: {e}", "ERROR")
            return False

    def contains_keyword(self, text):
        """Check if text contains any of the monitored keywords (case-insensitive)"""
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in KEYWORDS)

    def create_task_file(self, chat_name, message_text, timestamp):
        """Create a markdown file in Needs_Action directory"""
        file_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        clean_chat_name = "".join(c for c in chat_name[:30] if c.isalnum() or c in " -_")
        filename = f"WhatsApp_{file_timestamp}_{clean_chat_name}.md"
        filepath = os.path.join(NEEDS_ACTION_DIR, filename)

        metadata = f"""---
Source: WhatsApp
Type: WhatsApp
From: {chat_name}
Detected_At: {file_timestamp}
Status: Unprocessed
Tags: #whatsapp #message
---

"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(metadata)
            f.write(f"# WhatsApp Message from {chat_name}\n\n")
            f.write(f"**From:** {chat_name}\n\n")
            f.write(f"**Received:** {timestamp}\n\n")
            f.write(f"**Detected:** {file_timestamp}\n\n")
            f.write("---\n\n")
            f.write("## Message Content\n\n")
            f.write(message_text)

        self.log(f"Created task file: {filename}")
        return filepath

    def get_unread_chats(self):
        """Get all chats with unread messages"""
        try:
            # Wait for chat list to be visible
            self.page.wait_for_selector('div[aria-label="Chat list"]', timeout=10000)

            # Find all chat elements with unread badge
            unread_chats = []

            # WhatsApp uses different selectors for unread chats
            # Look for chats with unread badge (green dot or number)
            chat_elements = self.page.query_selector_all('div[role="listitem"]')

            for chat_elem in chat_elements:
                try:
                    # Check if chat has unread indicator
                    unread_badge = chat_elem.query_selector('span[data-icon="unread-count"], span[aria-label*="unread"]')

                    if unread_badge:
                        # Get chat name
                        chat_name_elem = chat_elem.query_selector('span[dir="auto"][title]')
                        if chat_name_elem:
                            chat_name = chat_name_elem.get_attribute('title')
                            unread_chats.append({
                                'element': chat_elem,
                                'name': chat_name
                            })
                except Exception as e:
                    continue

            return unread_chats

        except Exception as e:
            self.log(f"Error getting unread chats: {e}", "ERROR")
            return []

    def read_chat_messages(self, chat_element, chat_name):
        """Click on chat and read recent messages"""
        try:
            # Click on the chat to open it
            chat_element.click()
            time.sleep(2)  # Wait for chat to load

            # Get all message elements in the chat
            message_elements = self.page.query_selector_all('div[class*="message-in"], div[class*="message-out"]')

            # Get last 10 messages (or fewer if less available)
            recent_messages = message_elements[-10:] if len(message_elements) > 10 else message_elements

            messages_with_keywords = []

            for msg_elem in recent_messages:
                try:
                    # Get message text
                    text_elem = msg_elem.query_selector('span.selectable-text')
                    if text_elem:
                        message_text = text_elem.inner_text()

                        # Create unique message ID to avoid duplicates
                        msg_id = f"{chat_name}_{hash(message_text)}"

                        # Check if message contains keywords and hasn't been processed
                        if self.contains_keyword(message_text) and msg_id not in self.processed_messages:
                            # Get timestamp if available
                            time_elem = msg_elem.query_selector('span[data-icon="msg-time"], span[class*="time"]')
                            timestamp = time_elem.inner_text() if time_elem else "Unknown"

                            messages_with_keywords.append({
                                'text': message_text,
                                'timestamp': timestamp,
                                'id': msg_id
                            })

                except Exception as e:
                    continue

            return messages_with_keywords

        except Exception as e:
            self.log(f"Error reading chat messages from {chat_name}: {e}", "ERROR")
            return []

    def scan_for_keywords(self):
        """Scan all unread chats for messages with keywords"""
        try:
            self.log("Scanning for unread messages with keywords...")

            # Get all unread chats
            unread_chats = self.get_unread_chats()

            if not unread_chats:
                self.log("No unread chats found")
                return

            self.log(f"Found {len(unread_chats)} unread chat(s)")

            new_tasks = 0

            for chat in unread_chats:
                chat_name = chat['name']
                self.log(f"Checking chat: {chat_name}")

                # Read messages from this chat
                messages = self.read_chat_messages(chat['element'], chat_name)

                # Create task files for messages with keywords
                for msg in messages:
                    self.create_task_file(chat_name, msg['text'], msg['timestamp'])
                    self.processed_messages.add(msg['id'])
                    new_tasks += 1

            if new_tasks > 0:
                self.log(f"Created {new_tasks} new task(s) from WhatsApp messages")
            else:
                self.log("No messages with keywords found")

        except Exception as e:
            self.log(f"Error during keyword scan: {e}", "ERROR")

    def start(self):
        """Start the WhatsApp watcher"""
        self.running = True
        self.log("=" * 60, "SYSTEM")
        self.log("=== WhatsApp Watcher Starting ===", "SYSTEM")
        self.log("=" * 60, "SYSTEM")
        self.log(f"Check interval: {self.check_interval} seconds")
        self.log(f"Monitoring keywords: {', '.join(KEYWORDS)}")
        self.log(f"Output directory: {NEEDS_ACTION_DIR}")
        self.log(f"Session path: {SESSION_PATH}")

        # Initialize browser
        if not self.initialize_browser():
            self.log("Failed to initialize browser", "ERROR")
            self.running = False
            return

        # Login to WhatsApp Web
        if not self.login_whatsapp():
            self.log("Failed to login to WhatsApp Web", "ERROR")
            self.cleanup()
            self.running = False
            return

        self.log("WhatsApp Web connected successfully")
        self.log("Starting message monitoring...")
        self.log("=" * 60, "SYSTEM")

        try:
            while self.running:
                self.scan_for_keywords()
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            self.stop()

    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
            self.log("Browser resources cleaned up")
        except Exception as e:
            self.log(f"Error during cleanup: {e}", "ERROR")

    def stop(self):
        """Stop the WhatsApp watcher"""
        self.log("=" * 60, "SYSTEM")
        self.log("=== Shutting down WhatsApp watcher ===", "SYSTEM")
        self.running = False
        self.cleanup()
        self.log("WhatsApp watcher stopped")
        self.log("=" * 60, "SYSTEM")


if __name__ == "__main__":
    print("\n[STARTING] WhatsApp Watcher...\n")
    watcher = WhatsAppWatcher()
    watcher.start()
