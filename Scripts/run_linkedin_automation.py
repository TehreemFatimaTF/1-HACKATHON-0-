#!/usr/bin/env python3
"""
Enhanced LinkedIn Automation Runner

Features:
- Multiple retry attempts
- Better error handling
- Logging
- Scheduled posting capability
- Session persistence (login once, reuse)
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from linkedin_automation import LinkedInAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LinkedInAutomationRunner:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 30  # seconds
        self.post_delay = 60   # seconds between posts

    async def run_with_retry(self):
        """Run LinkedIn automation with retry logic"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Starting LinkedIn automation (Attempt {attempt + 1}/{self.max_retries})")

                bot = LinkedInAutomation(headless=False)
                await bot.run()

                logger.info("✅ LinkedIn automation completed successfully!")
                return True

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")

                if attempt < self.max_retries - 1:
                    logger.info(f"Waiting {self.retry_delay} seconds before retry...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("❌ All retry attempts failed.")
                    return False

    async def get_latest_post_content(self):
        """Get the latest post content from the appropriate folder"""
        possible_paths = [
            Path("Done"),
            Path("done"),
            Path("Needs_Action"),
            Path("."),
        ]

        for path in possible_paths:
            if path.exists():
                markdown_files = list(path.glob("*.md"))
                linkedin_files = [f for f in markdown_files if "linkedin" in f.name.lower()]

                if linkedin_files:
                    latest_file = max(linkedin_files, key=lambda f: f.stat().st_ctime)
                    logger.info(f"Found LinkedIn draft: {latest_file}")

                    with open(latest_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                        if '## LinkedIn Post Draft' in content:
                            lines = content.split('\n')
                            in_post_section = False
                            post_content = []

                            for line in lines:
                                if '## LinkedIn Post Draft' in line:
                                    in_post_section = True
                                    continue
                                if in_post_section and line.strip():
                                    post_content.append(line)

                            if post_content:
                                content = '\n'.join(post_content).strip()

                        return content.strip()

        default_content = f"""AI Employee Assistant Automation Update 🚀

This post demonstrates the autonomous capabilities of our AI Employee system.

#AI #Automation #Innovation #BusinessProcess

Posted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        logger.warning("No draft files found, using default content")
        return default_content

    async def schedule_posting(self, interval_hours=24):
        """Schedule regular posting at specified intervals"""
        logger.info(f"Starting scheduled posting (every {interval_hours} hours)")

        while True:
            try:
                success = await self.run_with_retry()
                if success:
                    logger.info(f"Waiting {interval_hours} hours until next post...")
                    await asyncio.sleep(interval_hours * 3600)
                else:
                    logger.error("Post failed, waiting before trying again...")
                    await asyncio.sleep(3600)

            except KeyboardInterrupt:
                logger.info("Scheduled posting stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in scheduled posting: {e}")
                await asyncio.sleep(3600)

async def main():
    """Main function to run LinkedIn automation"""
    runner = LinkedInAutomationRunner()

    import argparse
    parser = argparse.ArgumentParser(description='LinkedIn Automation Runner')
    parser.add_argument('--mode', choices=['once', 'scheduled'], default='once',
                       help='Run mode: once (default) or scheduled')
    parser.add_argument('--interval', type=int, default=24,
                       help='Interval in hours for scheduled mode (default: 24)')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode')

    args = parser.parse_args()

    if args.mode == 'once':
        await runner.run_with_retry()
    elif args.mode == 'scheduled':
        await runner.schedule_posting(interval_hours=args.interval)

if __name__ == "__main__":
    asyncio.run(main())
