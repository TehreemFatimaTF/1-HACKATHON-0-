"""
Specialized Social Media Agent for Platinum Tier
Handles all social media tasks across platforms
"""

from typing import Dict, List
from .base_agent import BaseAgent, AgentCapability
from datetime import datetime


class SocialMediaAgent(BaseAgent):
    """
    Specialized agent for social media management.
    Handles posting, engagement, and analytics across platforms.
    """

    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id=agent_id,
            name="SocialMediaAgent",
            specialization="social_media",
            capabilities=[
                AgentCapability.SOCIAL_MEDIA,
                AgentCapability.ANALYTICS
            ]
        )
        self.platforms = ["twitter", "facebook", "instagram", "linkedin"]
        self.posts_history = []
        self.engagement_metrics = {}

    def _execute_task_impl(self, task: Dict) -> Dict:
        """
        Execute social media tasks

        Args:
            task: Social media task to execute

        Returns:
            Dict: Execution result
        """
        task_type = task.get("type", "")

        if task_type == "social_post":
            return self._create_post(task)
        elif task_type == "social_broadcast":
            return self._broadcast_post(task)
        elif task_type == "social_analyze":
            return self._analyze_engagement(task)
        elif task_type == "social_schedule":
            return self._schedule_post(task)
        else:
            return {
                "success": False,
                "error": f"Unknown social media task type: {task_type}"
            }

    def _create_post(self, task: Dict) -> Dict:
        """Create social media post"""
        try:
            post_data = task.get("data", {})
            platform = post_data.get("platform", "twitter")
            content = post_data.get("content", "")

            if not content:
                return {
                    "success": False,
                    "error": "Post content is required"
                }

            # Optimize content for platform
            optimized_content = self._optimize_for_platform(content, platform)

            post_record = {
                "task_id": task.get("task_id"),
                "platform": platform,
                "content": optimized_content,
                "posted_at": datetime.now().isoformat(),
                "status": "posted"
            }

            self.posts_history.append(post_record)

            return {
                "success": True,
                "message": f"Post created on {platform}",
                "post_id": post_record.get("task_id"),
                "platform": platform,
                "content": optimized_content
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create post: {str(e)}"
            }

    def _broadcast_post(self, task: Dict) -> Dict:
        """Broadcast post to multiple platforms"""
        try:
            post_data = task.get("data", {})
            content = post_data.get("content", "")
            platforms = post_data.get("platforms", self.platforms)

            if not content:
                return {
                    "success": False,
                    "error": "Post content is required"
                }

            results = []
            for platform in platforms:
                platform_task = {
                    "task_id": f"{task.get('task_id')}_{platform}",
                    "type": "social_post",
                    "data": {
                        "platform": platform,
                        "content": content
                    }
                }

                result = self._create_post(platform_task)
                results.append({
                    "platform": platform,
                    "success": result.get("success"),
                    "post_id": result.get("post_id")
                })

            successful_posts = sum(1 for r in results if r["success"])

            return {
                "success": successful_posts > 0,
                "message": f"Broadcast to {successful_posts}/{len(platforms)} platforms",
                "results": results,
                "total_platforms": len(platforms),
                "successful_posts": successful_posts
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to broadcast post: {str(e)}"
            }

    def _analyze_engagement(self, task: Dict) -> Dict:
        """Analyze social media engagement"""
        try:
            platform = task.get("data", {}).get("platform", "all")

            if platform == "all":
                posts = self.posts_history
            else:
                posts = [p for p in self.posts_history if p["platform"] == platform]

            analysis = {
                "total_posts": len(posts),
                "platforms": list(set(p["platform"] for p in posts)),
                "recent_posts": posts[-5:],
                "posting_frequency": self._calculate_frequency(posts),
                "analyzed_at": datetime.now().isoformat()
            }

            return {
                "success": True,
                "message": "Engagement analysis complete",
                "analysis": analysis
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to analyze engagement: {str(e)}"
            }

    def _schedule_post(self, task: Dict) -> Dict:
        """Schedule post for future publication"""
        try:
            post_data = task.get("data", {})
            scheduled_time = post_data.get("scheduled_time")

            if not scheduled_time:
                return {
                    "success": False,
                    "error": "Scheduled time is required"
                }

            schedule_record = {
                "task_id": task.get("task_id"),
                "content": post_data.get("content"),
                "platform": post_data.get("platform"),
                "scheduled_for": scheduled_time,
                "status": "scheduled"
            }

            return {
                "success": True,
                "message": f"Post scheduled for {scheduled_time}",
                "schedule_id": schedule_record.get("task_id")
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to schedule post: {str(e)}"
            }

    def _optimize_for_platform(self, content: str, platform: str) -> str:
        """Optimize content for specific platform"""
        if platform == "twitter":
            # Twitter has 280 character limit
            if len(content) > 280:
                return content[:277] + "..."
        elif platform == "linkedin":
            # LinkedIn prefers professional tone
            # Add hashtags if not present
            if "#" not in content:
                content += "\n\n#Business #Professional"
        elif platform == "instagram":
            # Instagram loves hashtags
            if "#" not in content:
                content += "\n\n#InstaDaily #Business"

        return content

    def _calculate_frequency(self, posts: List[Dict]) -> str:
        """Calculate posting frequency"""
        if len(posts) < 2:
            return "insufficient_data"

        # Simple frequency calculation
        if len(posts) >= 7:
            return "daily"
        elif len(posts) >= 3:
            return "weekly"
        else:
            return "occasional"

    def get_social_stats(self) -> Dict:
        """Get social media statistics"""
        platform_counts = {}
        for post in self.posts_history:
            platform = post["platform"]
            platform_counts[platform] = platform_counts.get(platform, 0) + 1

        return {
            "total_posts": len(self.posts_history),
            "posts_by_platform": platform_counts,
            "recent_posts": self.posts_history[-10:],
            "agent_metrics": self.metrics
        }
