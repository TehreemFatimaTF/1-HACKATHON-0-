import time
import os
from datetime import datetime

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
INBOX_DIR = os.path.join(BASE_DIR, "Inbox")
LOGS_DIR = os.path.join(BASE_DIR, "Logs")

# Ensure directories exist
for directory in [INBOX_DIR, LOGS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

class LinkedInWatcher:
    """Monitors LinkedIn trends and business news"""

    def __init__(self):
        self.running = False
        self.log_file = os.path.join(LOGS_DIR, "watcher_linkedin.log")
        self.check_interval = 3600  # Check every 1 hour
        self.trend_index = 0

        # Simulated business trends for demo
        self.demo_trends = [
            {
                "title": "AI Automation Trends 2026",
                "content": "Businesses are increasingly adopting AI employees for routine tasks. Market size expected to reach $50B by 2027.",
                "category": "Technology",
                "relevance": "High",
                "hashtags": "#AI #Automation #FutureOfWork"
            },
            {
                "title": "Remote Work Best Practices",
                "content": "New study shows 73% productivity increase with AI-assisted task management in remote teams.",
                "category": "Business",
                "relevance": "Medium",
                "hashtags": "#RemoteWork #Productivity #AITools"
            },
            {
                "title": "Email Marketing ROI Statistics",
                "content": "Email marketing delivers $42 ROI for every $1 spent. Automation increases engagement by 320%.",
                "category": "Marketing",
                "relevance": "High",
                "hashtags": "#EmailMarketing #ROI #MarketingAutomation"
            },
            {
                "title": "Sales Automation Success Stories",
                "content": "Companies using AI for lead qualification see 50% faster sales cycles and 35% higher conversion rates.",
                "category": "Sales",
                "relevance": "High",
                "hashtags": "#SalesAutomation #LeadGen #AI"
            },
            {
                "title": "Customer Service AI Revolution",
                "content": "AI-powered customer service reduces response time by 80% while maintaining 95% satisfaction rates.",
                "category": "Customer Service",
                "relevance": "Medium",
                "hashtags": "#CustomerService #AI #CX"
            }
        ]

    def log(self, message, level="INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [LINKEDIN] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def create_inbox_file(self, trend):
        """Create a markdown file in Inbox folder from LinkedIn trend"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        # Clean title for filename
        clean_title = "".join(c for c in trend['title'][:30] if c.isalnum() or c in " -_")
        filename = f"LinkedIn_{timestamp}_{clean_title}.md"
        filepath = os.path.join(INBOX_DIR, filename)

        # Build metadata section
        metadata = f"""---
Source: LinkedIn
Category: {trend['category']}
Relevance: {trend['relevance']}
Detected_At: {timestamp}
Status: Unprocessed
Type: Business_Trend
---

"""

        # Build content
        content = f"# {trend['title']}\n\n"
        content += f"**Category:** {trend['category']}\n"
        content += f"**Relevance:** {trend['relevance']}\n"
        content += f"**Hashtags:** {trend['hashtags']}\n\n"
        content += "---\n\n"
        content += trend['content']
        content += "\n\n## Potential Actions\n\n"
        content += "- Create LinkedIn post about this trend\n"
        content += "- Share with team for discussion\n"
        content += "- Incorporate into marketing strategy\n"
        content += "- Research competitors' response\n"

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(metadata + content)

        self.log(f"Created: {filename}")
        return filepath

    def fetch_trends(self):
        """Fetch LinkedIn trends (simulated for demo)"""
        # In production, this would:
        # 1. Use LinkedIn API or web scraping
        # 2. Fetch trending posts in your industry
        # 3. Filter by relevance to your business
        # 4. Extract key insights and metrics

        if self.trend_index < len(self.demo_trends):
            trend = self.demo_trends[self.trend_index]
            self.create_inbox_file(trend)
            self.log(f"New trend captured: {trend['title']}")
            self.trend_index += 1
        else:
            self.log("All demo trends processed, restarting cycle")
            self.trend_index = 0
            time.sleep(300)  # Wait 5 minutes before restarting

    def start(self):
        """Start monitoring LinkedIn trends"""
        self.running = True
        self.log("=== LinkedIn Trends Watcher Starting ===", "SYSTEM")
        self.log(f"Check interval: {self.check_interval} seconds (1 hour)")
        self.log(f"Output to: {INBOX_DIR}")
        self.log(f"Demo trends available: {len(self.demo_trends)}")
        self.log("Note: Using simulated trends for demo (LinkedIn API integration pending)")

        try:
            while self.running:
                self.fetch_trends()
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the watcher"""
        self.log("=== Shutting down LinkedIn watcher ===", "SYSTEM")
        self.running = False

if __name__ == "__main__":
    watcher = LinkedInWatcher()
    watcher.start()
