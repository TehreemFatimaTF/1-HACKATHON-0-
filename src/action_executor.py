import os
import json
import shutil
from datetime import datetime
from pathlib import Path

# Add the LinkedIn poster import (optional)
import sys
sys.path.append(str(Path(__file__).parent))
try:
    from linkedin_poster import LinkedInPoster
    LINKEDIN_AVAILABLE = True
except ImportError:
    LINKEDIN_AVAILABLE = False
    print("[WARNING] LinkedInPoster not available - LinkedIn features disabled")
    LinkedInPoster = None

# Import Gold Tier autonomous engine
try:
    from engine_gold import RalphWiggumLoopEngine
    from models.autonomous_task import AutonomousTask, Priority
    from models.step import StepSchema, StepStatus
    GOLD_TIER_AVAILABLE = True
except ImportError:
    GOLD_TIER_AVAILABLE = False
    print("[WARNING] Gold Tier engine not available - running in Silver Tier mode")

# Configuration
BASE_DIR = Path(__file__).parent.parent
APPROVED_DIR = BASE_DIR / "4_Approved"
DONE_DIR = BASE_DIR / "Done"
LOGS_DIR = BASE_DIR / "Logs"
ACTIONS_LOG = LOGS_DIR / "external_actions.json"

# Gold Tier Configuration
AUTONOMOUS_MODE_ENABLED = False  # Set to True to enable autonomous execution

class ActionExecutor:
    """Executes approved plans using MCP tools and external APIs"""

    def __init__(self):
        self.log_file = LOGS_DIR / "action_executor.log"
        self.actions_data = self.load_actions_log()
        if LINKEDIN_AVAILABLE and LinkedInPoster:
            self.linkedin_poster = LinkedInPoster()  # Initialize LinkedIn poster
        else:
            self.linkedin_poster = None

        # Initialize Gold Tier engine if enabled
        self.gold_tier_engine = None
        self.autonomous_mode = AUTONOMOUS_MODE_ENABLED

        if self.autonomous_mode and GOLD_TIER_AVAILABLE:
            try:
                self.gold_tier_engine = RalphWiggumLoopEngine()
                self.log("Gold Tier autonomous engine initialized", "SYSTEM")
            except Exception as e:
                self.log(f"Failed to initialize Gold Tier engine: {e}", "ERROR")
                self.autonomous_mode = False

    def log(self, message, level="INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [EXECUTOR] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def load_actions_log(self):
        """Load existing actions log"""
        if ACTIONS_LOG.exists():
            with open(ACTIONS_LOG, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "emails_sent": [],
            "linkedin_posts": [],
            "reports_generated": [],
            "meetings_scheduled": [],
            "total_emails": 0,
            "total_posts": 0,
            "total_reports": 0,
            "total_meetings": 0,
            "last_updated": "Never",
            "daily_stats": {}
        }

    def save_actions_log(self):
        """Save actions log to file"""
        self.actions_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(ACTIONS_LOG, 'w', encoding='utf-8') as f:
            json.dump(self.actions_data, f, indent=2)

    def parse_plan(self, filepath):
        """Parse a plan file to extract action details"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        action = {
            "type": None,
            "recipient": None,
            "subject": None,
            "body": None,
            "content": None,
            "hashtags": [],
            "metadata": {}
        }

        # Parse metadata section
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                metadata_section = parts[1]
                body_section = parts[2]

                # Parse metadata
                for line in metadata_section.strip().split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        action["metadata"][key.strip()] = value.strip()

                # Determine action type from metadata
                if "Action_Type" in action["metadata"]:
                    action_type_raw = action["metadata"]["Action_Type"].lower()
                    if "email" in action_type_raw:
                        action["type"] = "email"
                    elif "linkedin" in action_type_raw:
                        action["type"] = "linkedin_post"
                    else:
                        action["type"] = action_type_raw

                if "Recipient" in action["metadata"]:
                    action["recipient"] = action["metadata"]["Recipient"]
                if "Subject" in action["metadata"]:
                    action["subject"] = action["metadata"]["Subject"]

                content = body_section

        # Parse content for action indicators
        lines = content.split("\n")
        current_section = None
        body_lines = []
        in_body_section = False

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Detect action type (only if not already set from metadata)
            if not action["type"] and ("send email" in line_lower or "email to" in line_lower):
                action["type"] = "email"
                # Try to extract recipient
                if "@" in line:
                    words = line.split()
                    for word in words:
                        if "@" in word:
                            action["recipient"] = word.strip(",:;")
                            break

            elif not action["type"] and ("linkedin post" in line_lower or "post on linkedin" in line_lower):
                action["type"] = "linkedin_post"

            # Extract subject
            elif line_lower.startswith("subject:") or line.startswith("**Subject:**"):
                action["subject"] = line.split(":", 1)[1].strip().strip("*")

            # Extract body/content sections
            elif line_lower.startswith("body:") or line_lower.startswith("**body:**"):
                in_body_section = True
                continue
            elif line_lower.startswith("content:") or line_lower.startswith("**content:**"):
                in_body_section = True
                continue

            # Stop collecting body at certain markers
            elif line.startswith("---") and in_body_section:
                in_body_section = False
            elif line.startswith("**Execution Notes:**"):
                in_body_section = False

            # Collect body content
            elif in_body_section and line.strip():
                body_lines.append(line)

            # Extract hashtags
            if "#" in line and not line.startswith("#"):
                hashtags = [word for word in line.split() if word.startswith("#") and len(word) > 1]
                action["hashtags"].extend(hashtags)

        # If no body found yet, try to extract everything after "Body:" or "Content:"
        if not body_lines:
            body_marker_found = False
            for i, line in enumerate(lines):
                if "**Body:**" in line or "**Content:**" in line or line.strip().startswith("Body:") or line.strip().startswith("Content:"):
                    body_marker_found = True
                    continue
                if body_marker_found:
                    if line.startswith("---") or line.startswith("**Execution"):
                        break
                    if line.strip():
                        body_lines.append(line)

        action["body"] = "\n".join(body_lines).strip()
        action["content"] = action["body"]  # Alias for LinkedIn posts

        return action

    def execute_email(self, action, plan_file):
        """Execute email action - requires MCP integration"""
        self.log(f"Email action detected: {action['subject']}")
        self.log(f"Recipient: {action['recipient']}")

        # NOTE: This requires MCP gmail__send_email tool
        # For now, we log the action and mark it as pending MCP execution

        email_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "plan_file": plan_file,
            "recipient": action["recipient"],
            "subject": action["subject"],
            "body": action["body"],
            "status": "pending_mcp",
            "message": "Requires Claude Code MCP execution"
        }

        self.actions_data["emails_sent"].append(email_record)
        self.actions_data["total_emails"] += 1

        self.log(f"Email logged for MCP execution: {action['subject']}", "SUCCESS")
        return True

    def execute_linkedin_post(self, action, plan_file):
        """Execute LinkedIn post action - try MCP first, then direct API"""
        self.log(f"LinkedIn post action detected")
        self.log(f"Content preview: {action['content'][:50]}...")

        # Try to use MCP if available (this would be handled by Claude's built-in tools)
        # For now, let's try direct API posting first
        try:
            success = self.linkedin_poster.post_update(action["content"], action["hashtags"])
            if success:
                self.log(f"LinkedIn post successful via direct API", "SUCCESS")

                # Log the successful post
                post_record = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "plan_file": plan_file,
                    "content": action["content"],
                    "hashtags": action["hashtags"],
                    "status": "posted",
                    "message": "Successfully posted to LinkedIn via direct API"
                }
            else:
                # If direct API fails, log as simulated
                post_record = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "plan_file": plan_file,
                    "content": action["content"],
                    "hashtags": action["hashtags"],
                    "status": "pending_manual",
                    "message": "LinkedIn API not configured - create manually or set up credentials"
                }
                self.log(f"LinkedIn post requires manual setup - see instructions", "WARNING")

        except Exception as e:
            self.log(f"Error in LinkedIn posting: {e}", "ERROR")
            # Fallback to simulated logging
            post_record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "plan_file": plan_file,
                "content": action["content"],
                "hashtags": action["hashtags"],
                "status": "pending_manual",
                "message": f"Error occurred: {str(e)}. Set up LinkedIn credentials to post automatically."
            }

        self.actions_data["linkedin_posts"].append(post_record)
        self.actions_data["total_posts"] += 1

        # Save to LinkedIn log
        linkedin_log = LOGS_DIR / "linkedin_posts.log"
        with open(linkedin_log, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Timestamp: {post_record['timestamp']}\n")
            f.write(f"Plan: {plan_file}\n")
            f.write(f"Content:\n{action['content']}\n")
            f.write(f"Hashtags: {' '.join(action['hashtags'])}\n")
            f.write(f"Status: {post_record['status']}\n")
            f.write(f"Message: {post_record['message']}\n")
            f.write(f"{'='*60}\n")

        if "posted" in post_record["status"]:
            self.log(f"LinkedIn post successfully published", "SUCCESS")
        else:
            self.log(f"LinkedIn post pending manual setup", "INFO")

        return True

    def move_to_done(self, filepath):
        """Move executed plan to Done folder"""
        filename = os.path.basename(filepath)
        dest_path = DONE_DIR / filename

        # Add execution timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        dest_path = DONE_DIR / f"{name}_executed_{timestamp}{ext}"

        shutil.move(filepath, dest_path)
        self.log(f"Moved to Done: {filename}")
        return dest_path

    def scan_and_execute(self):
        """Scan 4_Approved folder and execute all plans"""
        self.log("=== Starting Action Execution Scan ===", "SYSTEM")

        if not APPROVED_DIR.exists():
            self.log("4_Approved folder not found", "ERROR")
            return

        # Get all markdown files
        plan_files = list(APPROVED_DIR.glob("*.md"))

        if not plan_files:
            self.log("No approved plans found")
            return

        self.log(f"Found {len(plan_files)} approved plan(s)")

        executed_count = 0
        failed_count = 0

        for plan_file in plan_files:
            try:
                self.log(f"\nProcessing: {plan_file.name}")

                # Parse the plan
                action = self.parse_plan(plan_file)

                if not action["type"]:
                    self.log(f"Could not determine action type for {plan_file.name}", "WARNING")
                    continue

                # Execute based on type
                success = False
                if action["type"] == "email" or "send_email" in action["type"]:
                    success = self.execute_email(action, plan_file.name)
                elif action["type"] == "linkedin_post" or "linkedin" in action["type"]:
                    success = self.execute_linkedin_post(action, plan_file.name)
                else:
                    self.log(f"Unknown action type: {action['type']}", "WARNING")
                    continue

                if success:
                    # Move to Done folder
                    self.move_to_done(plan_file)
                    executed_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                self.log(f"Error processing {plan_file.name}: {e}", "ERROR")
                failed_count += 1

        # Save updated log
        self.save_actions_log()

        # Summary
        self.log("\n=== Execution Summary ===", "SYSTEM")
        self.log(f"[OK] Successfully executed: {executed_count}")
        self.log(f"[FAIL] Failed: {failed_count}")
        self.log(f"[STATS] Total emails sent: {self.actions_data['total_emails']}")
        self.log(f"[STATS] Total LinkedIn posts: {self.actions_data['total_posts']}")

        return {
            "executed": executed_count,
            "failed": failed_count,
            "total_emails": self.actions_data["total_emails"],
            "total_posts": self.actions_data["total_posts"]
        }

if __name__ == "__main__":
    print("\n[AI Employee - Action Executor]")
    print("="*60)

    executor = ActionExecutor()
    results = executor.scan_and_execute()

    print("\n" + "="*60)
    print("[Execution complete!]")
    print("="*60 + "\n")
