import time
import os
from datetime import datetime
from typing import Dict, List, Optional
import json

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
INBOX_DIR = os.path.join(BASE_DIR, "Inbox")
LOGS_DIR = os.path.join(BASE_DIR, "Logs")
DONE_DIR = os.path.join(BASE_DIR, "Done")

# Ensure directories exist
for directory in [INBOX_DIR, LOGS_DIR, DONE_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

class FacebookWatcher:
    """Monitors Facebook pages, groups, and posts for business insights"""

    def __init__(self):
        self.running = False
        self.log_file = os.path.join(LOGS_DIR, "watcher_facebook.log")
        self.check_interval = 1800  # Check every 30 minutes
        self.content_index = 0

        # Facebook credentials (to be provided by user)
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID", "")
        self.instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        self.instagram_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID", "")

        # Track posted content for summary generation
        self.posted_content = []
        self.summary_file = os.path.join(DONE_DIR, "facebook_summary.json")

        # Simulated Facebook content for demo
        self.demo_content = [
            {
                "title": "Customer Success Story: AI Automation",
                "content": "Just helped a client automate their entire email workflow! They're now saving 20 hours per week and seeing 3x faster response times. AI employees are game-changers for small businesses.",
                "category": "Success Story",
                "engagement_potential": "High",
                "hashtags": "#AIAutomation #CustomerSuccess #SmallBusiness #Productivity",
                "post_type": "text",
                "platforms": ["facebook", "instagram"]
            },
            {
                "title": "Industry Insight: Remote Work Trends",
                "content": "New data shows 85% of businesses are adopting AI tools for remote team management. The future of work is here, and it's automated! 🚀",
                "category": "Industry News",
                "engagement_potential": "Medium",
                "hashtags": "#RemoteWork #FutureOfWork #AITools #BusinessTrends",
                "post_type": "text",
                "platforms": ["facebook"]
            },
            {
                "title": "Product Update: New Features",
                "content": "Exciting news! Our AI Employee now supports multi-platform social media posting. One message, all platforms. Save time, increase reach! 📱✨",
                "category": "Product Update",
                "engagement_potential": "High",
                "hashtags": "#ProductUpdate #SocialMedia #Automation #Innovation",
                "post_type": "text",
                "platforms": ["facebook", "instagram"]
            },
            {
                "title": "Engagement Post: Question",
                "content": "Quick poll: What's your biggest challenge with social media management? A) Time B) Content ideas C) Consistency D) Analytics. Comment below! 👇",
                "category": "Engagement",
                "engagement_potential": "Very High",
                "hashtags": "#SocialMediaMarketing #BusinessOwners #Poll #Community",
                "post_type": "text",
                "platforms": ["facebook"]
            },
            {
                "title": "Educational Content: Tips",
                "content": "5 Ways AI Can Transform Your Business:\n1. Automate repetitive tasks\n2. Improve customer response time\n3. Generate insights from data\n4. Optimize marketing campaigns\n5. Scale without hiring\n\nWhich one interests you most?",
                "category": "Educational",
                "engagement_potential": "High",
                "hashtags": "#BusinessTips #AITransformation #Entrepreneurship #GrowthHacking",
                "post_type": "text",
                "platforms": ["facebook", "instagram"]
            }
        ]

    def log(self, message: str, level: str = "INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [FACEBOOK] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def create_inbox_file(self, content: Dict) -> str:
        """Create a markdown file in Inbox folder from Facebook content"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        # Clean title for filename
        clean_title = "".join(c for c in content['title'][:30] if c.isalnum() or c in " -_")
        filename = f"Facebook_{timestamp}_{clean_title}.md"
        filepath = os.path.join(INBOX_DIR, filename)

        # Build metadata section
        metadata = f"""---
Source: Facebook
Category: {content['category']}
Engagement_Potential: {content['engagement_potential']}
Detected_At: {timestamp}
Status: Unprocessed
Type: Social_Media_Content
Platforms: {', '.join(content['platforms'])}
Post_Type: {content['post_type']}
---

"""

        # Build content
        file_content = f"# {content['title']}\n\n"
        file_content += f"**Category:** {content['category']}\n"
        file_content += f"**Engagement Potential:** {content['engagement_potential']}\n"
        file_content += f"**Platforms:** {', '.join(content['platforms'])}\n"
        file_content += f"**Hashtags:** {content['hashtags']}\n\n"
        file_content += "---\n\n"
        file_content += "## Content\n\n"
        file_content += content['content']
        file_content += "\n\n## Suggested Actions\n\n"
        file_content += "- [ ] Review and approve content\n"
        file_content += "- [ ] Post to Facebook\n"
        if "instagram" in content['platforms']:
            file_content += "- [ ] Post to Instagram (requires image)\n"
        file_content += "- [ ] Monitor engagement metrics\n"
        file_content += "- [ ] Respond to comments\n"
        file_content += "- [ ] Generate performance summary\n"

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(metadata + file_content)

        self.log(f"Created: {filename}")
        return filepath

    def post_to_facebook(self, content: str) -> Dict:
        """Post content to Facebook page"""
        try:
            # Import Facebook client
            from src.mcp.facebook_client import FacebookClient

            if not self.access_token or not self.page_id:
                self.log("Facebook credentials not configured", "WARNING")
                return {
                    "success": False,
                    "error": "Missing Facebook credentials",
                    "platform": "facebook"
                }

            # Initialize client
            client = FacebookClient(
                access_token=self.access_token,
                page_id=self.page_id
            )

            # Post content
            result = client.post_to_page(content=content)

            if result.get("success"):
                self.log(f"Posted to Facebook: {result.get('post_id')}", "SUCCESS")
                self.posted_content.append({
                    "platform": "facebook",
                    "content": content[:100],
                    "post_id": result.get("post_id"),
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                })

            return result

        except Exception as e:
            self.log(f"Facebook posting failed: {str(e)}", "ERROR")
            return {
                "success": False,
                "error": str(e),
                "platform": "facebook"
            }

    def post_to_instagram(self, content: str, hashtags: List[str], image_url: str = None) -> Dict:
        """Post content to Instagram"""
        try:
            # Import Instagram client
            from src.mcp.instagram_client import InstagramClient

            if not self.instagram_access_token or not self.instagram_account_id:
                self.log("Instagram credentials not configured", "WARNING")
                return {
                    "success": False,
                    "error": "Missing Instagram credentials",
                    "platform": "instagram"
                }

            if not image_url:
                self.log("Instagram requires image URL - skipping", "WARNING")
                return {
                    "success": False,
                    "error": "Instagram requires image URL",
                    "platform": "instagram"
                }

            # Initialize client
            client = InstagramClient(
                access_token=self.instagram_access_token,
                instagram_account_id=self.instagram_account_id
            )

            # Post content
            result = client.post_to_instagram(
                content=content,
                hashtags=hashtags,
                image_url=image_url
            )

            if result.get("success"):
                self.log(f"Posted to Instagram: {result.get('post_id')}", "SUCCESS")
                self.posted_content.append({
                    "platform": "instagram",
                    "content": content[:100],
                    "post_id": result.get("post_id"),
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                })

            return result

        except Exception as e:
            self.log(f"Instagram posting failed: {str(e)}", "ERROR")
            return {
                "success": False,
                "error": str(e),
                "platform": "instagram"
            }

    def broadcast_content(self, content: Dict) -> Dict:
        """Broadcast content to multiple platforms"""
        results = {
            "facebook": None,
            "instagram": None,
            "summary": ""
        }

        # Extract hashtags
        hashtags = [tag.strip() for tag in content['hashtags'].split() if tag.startswith('#')]

        # Post to Facebook
        if "facebook" in content['platforms']:
            fb_result = self.post_to_facebook(content['content'])
            results['facebook'] = fb_result

        # Post to Instagram (if image URL provided)
        if "instagram" in content['platforms']:
            # For demo, we skip Instagram without image
            self.log("Instagram posting requires image URL - create inbox file for manual processing", "INFO")
            results['instagram'] = {
                "success": False,
                "error": "Image URL required for Instagram",
                "platform": "instagram"
            }

        # Generate summary
        success_count = sum(1 for r in results.values() if isinstance(r, dict) and r.get("success"))
        total_platforms = len(content['platforms'])
        results['summary'] = f"Posted to {success_count}/{total_platforms} platforms"

        return results

    def generate_summary(self) -> Dict:
        """Generate summary of all posted content"""
        if not self.posted_content:
            return {
                "total_posts": 0,
                "message": "No posts to summarize"
            }

        # Calculate statistics
        total_posts = len(self.posted_content)
        facebook_posts = sum(1 for p in self.posted_content if p['platform'] == 'facebook')
        instagram_posts = sum(1 for p in self.posted_content if p['platform'] == 'instagram')
        successful_posts = sum(1 for p in self.posted_content if p['status'] == 'success')

        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_posts": total_posts,
            "successful_posts": successful_posts,
            "failed_posts": total_posts - successful_posts,
            "by_platform": {
                "facebook": facebook_posts,
                "instagram": instagram_posts
            },
            "recent_posts": self.posted_content[-5:],
            "success_rate": f"{(successful_posts/total_posts)*100:.1f}%" if total_posts > 0 else "0%"
        }

        # Save summary to file
        with open(self.summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        self.log(f"Summary generated: {total_posts} posts, {successful_posts} successful", "INFO")

        return summary

    def create_summary_markdown(self) -> str:
        """Create a markdown summary file"""
        summary = self.generate_summary()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"Facebook_Summary_{timestamp}.md"
        filepath = os.path.join(DONE_DIR, filename)

        content = f"""# Facebook & Instagram Activity Summary

**Generated:** {summary['generated_at']}

## Overview
- **Total Posts:** {summary['total_posts']}
- **Successful:** {summary['successful_posts']}
- **Failed:** {summary['failed_posts']}
- **Success Rate:** {summary['success_rate']}

## Posts by Platform
- **Facebook:** {summary['by_platform']['facebook']}
- **Instagram:** {summary['by_platform']['instagram']}

## Recent Posts
"""

        for post in summary.get('recent_posts', []):
            content += f"\n### {post['platform'].title()} - {post['timestamp']}\n"
            content += f"- **Post ID:** {post['post_id']}\n"
            content += f"- **Content:** {post['content']}...\n"
            content += f"- **Status:** {post['status']}\n"

        content += "\n---\n*Generated by Facebook Watcher*\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        self.log(f"Summary markdown created: {filename}", "INFO")
        return filepath

    def fetch_content(self):
        """Fetch Facebook content (simulated for demo)"""
        # In production, this would:
        # 1. Use Facebook Graph API to fetch page posts
        # 2. Monitor relevant groups and pages
        # 3. Track engagement metrics
        # 4. Identify trending topics
        # 5. Suggest content for posting

        if self.content_index < len(self.demo_content):
            content = self.demo_content[self.content_index]
            self.create_inbox_file(content)
            self.log(f"New content captured: {content['title']}")

            # Optionally auto-post (for demo purposes)
            # Uncomment to enable auto-posting:
            # self.broadcast_content(content)

            self.content_index += 1
        else:
            self.log("All demo content processed, generating summary")
            self.create_summary_markdown()
            self.content_index = 0
            time.sleep(300)  # Wait 5 minutes before restarting

    def start(self):
        """Start monitoring Facebook"""
        self.running = True
        self.log("=== Facebook & Instagram Watcher Starting ===", "SYSTEM")
        self.log(f"Check interval: {self.check_interval} seconds (30 minutes)")
        self.log(f"Output to: {INBOX_DIR}")
        self.log(f"Demo content available: {len(self.demo_content)}")

        # Check credentials
        if not self.access_token:
            self.log("WARNING: FACEBOOK_ACCESS_TOKEN not set in environment", "WARNING")
        if not self.page_id:
            self.log("WARNING: FACEBOOK_PAGE_ID not set in environment", "WARNING")
        if not self.instagram_access_token:
            self.log("WARNING: INSTAGRAM_ACCESS_TOKEN not set in environment", "WARNING")
        if not self.instagram_account_id:
            self.log("WARNING: INSTAGRAM_ACCOUNT_ID not set in environment", "WARNING")

        self.log("Note: Using simulated content for demo (Facebook API integration ready)")

        try:
            while self.running:
                self.fetch_content()
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the watcher"""
        self.log("=== Shutting down Facebook watcher ===", "SYSTEM")

        # Generate final summary
        if self.posted_content:
            self.create_summary_markdown()

        self.running = False

if __name__ == "__main__":
    watcher = FacebookWatcher()
    watcher.start()
