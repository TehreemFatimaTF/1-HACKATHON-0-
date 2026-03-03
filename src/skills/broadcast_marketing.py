"""
Broadcast Marketing Skill for Gold Tier Autonomous Employee

Unified social media broadcasting across Twitter, Facebook, and Instagram.
Part of User Story 3 - Unified Social Media Broadcasting.

Usage:
    from src.skills.broadcast_marketing import broadcast_post

    result = broadcast_post(
        content="Check out our new AI automation!",
        platforms=["twitter", "facebook", "instagram"]
    )
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from src.mcp.twitter_client import TwitterClient
from src.mcp.facebook_client import FacebookClient
from src.mcp.instagram_client import InstagramClient
from src.models.social_media_post import SocialMediaPost
from src.audit.gold_logger import GoldAuditLogger
from src.utils.content_formatter import ContentFormatter


class BroadcastResult:
    """Result of broadcast operation"""

    def __init__(self):
        self.successes: List[Dict[str, Any]] = []
        self.failures: List[Dict[str, Any]] = []
        self.total_platforms = 0
        self.successful_platforms = 0

    def add_success(self, platform: str, post_id: str, details: Dict[str, Any]):
        """Record successful post"""
        self.successes.append({
            "platform": platform,
            "post_id": post_id,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })
        self.successful_platforms += 1

    def add_failure(self, platform: str, error: str):
        """Record failed post"""
        self.failures.append({
            "platform": platform,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })

    def is_success(self) -> bool:
        """Check if at least one platform succeeded"""
        return self.successful_platforms > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_platforms": self.total_platforms,
            "successful_platforms": self.successful_platforms,
            "failed_platforms": len(self.failures),
            "successes": self.successes,
            "failures": self.failures,
            "overall_status": "success" if self.is_success() else "failed"
        }


def broadcast_post(
    content: str,
    platforms: Optional[List[str]] = None,
    images: Optional[List[str]] = None,
    hashtags: Optional[List[str]] = None,
    **kwargs
) -> BroadcastResult:
    """
    Broadcast content to multiple social media platforms simultaneously

    Args:
        content: Post content (will be formatted per platform)
        platforms: List of platforms to post to (default: all configured)
        images: Optional list of image paths
        hashtags: Optional list of hashtags
        **kwargs: Additional platform-specific parameters

    Returns:
        BroadcastResult with successes and failures

    Features:
        - Graceful degradation (continues if one platform fails)
        - Platform-specific content formatting
        - Rate limit handling
        - Complete audit logging
    """
    result = BroadcastResult()
    formatter = ContentFormatter()
    audit_logger = GoldAuditLogger()

    # Default to all platforms if not specified
    if platforms is None:
        platforms = ["twitter", "facebook", "instagram"]

    result.total_platforms = len(platforms)

    # Create base post object
    base_post = SocialMediaPost(
        platform="multi",
        content=content,
        images=images or [],
        hashtags=hashtags or [],
        timestamp=datetime.now()
    )

    # Log broadcast initiation
    audit_logger.log_action(
        action_type="social_media_broadcast_start",
        parameters={
            "platforms": platforms,
            "content_preview": content[:100],
            "has_images": bool(images),
            "hashtag_count": len(hashtags) if hashtags else 0
        },
        result={"status": "initiated"},
        business_impact=f"Broadcasting to {len(platforms)} platform(s)"
    )

    # Broadcast to each platform
    for platform in platforms:
        try:
            if platform.lower() == "twitter":
                _post_to_twitter(base_post, formatter, result)
            elif platform.lower() == "facebook":
                _post_to_facebook(base_post, formatter, result)
            elif platform.lower() == "instagram":
                _post_to_instagram(base_post, formatter, result)
            else:
                result.add_failure(platform, f"Unknown platform: {platform}")

        except Exception as e:
            # Graceful degradation - log error and continue
            error_msg = f"Failed to post to {platform}: {str(e)}"
            result.add_failure(platform, error_msg)
            print(f"⚠️  {error_msg}")

            # Log failure
            audit_logger.log_action(
                action_type="social_media_post_failed",
                parameters={"platform": platform, "content_preview": content[:100]},
                result={"error": str(e)},
                business_impact=f"Failed to reach {platform} audience"
            )

    # Log final result
    audit_logger.log_action(
        action_type="social_media_broadcast_complete",
        parameters={
            "platforms": platforms,
            "content_preview": content[:100]
        },
        result=result.to_dict(),
        business_impact=f"Reached {result.successful_platforms}/{result.total_platforms} platform(s)"
    )

    # Update Dashboard
    _update_dashboard(result)

    return result


def _post_to_twitter(post: SocialMediaPost, formatter: ContentFormatter, result: BroadcastResult):
    """Post to Twitter/X"""
    try:
        # Check credentials
        api_key = os.getenv("TWITTER_API_KEY")
        if not api_key or api_key.startswith("your_"):
            result.add_failure("twitter", "Twitter credentials not configured")
            return

        # Format content for Twitter
        formatted_content = formatter.format_for_twitter(
            post.content,
            hashtags=post.hashtags
        )

        # Create client and post
        client = TwitterClient(
            api_key=api_key,
            api_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )

        response = client.post(formatted_content, images=post.images)

        result.add_success("twitter", response.get("post_id", "unknown"), response)
        print(f"✅ Posted to Twitter: {response.get('post_id')}")

    except Exception as e:
        raise Exception(f"Twitter post failed: {e}")


def _post_to_facebook(post: SocialMediaPost, formatter: ContentFormatter, result: BroadcastResult):
    """Post to Facebook"""
    try:
        # Check credentials
        app_id = os.getenv("FACEBOOK_APP_ID")
        if not app_id or app_id.startswith("your_"):
            result.add_failure("facebook", "Facebook credentials not configured")
            return

        # Format content for Facebook
        formatted_content = formatter.format_for_facebook(
            post.content,
            hashtags=post.hashtags
        )

        # Create client and post
        client = FacebookClient(
            app_id=app_id,
            app_secret=os.getenv("FACEBOOK_APP_SECRET"),
            access_token=os.getenv("FACEBOOK_ACCESS_TOKEN"),
            page_id=os.getenv("FACEBOOK_PAGE_ID")
        )

        response = client.post(formatted_content, images=post.images)

        result.add_success("facebook", response.get("post_id", "unknown"), response)
        print(f"✅ Posted to Facebook: {response.get('post_id')}")

    except Exception as e:
        raise Exception(f"Facebook post failed: {e}")


def _post_to_instagram(post: SocialMediaPost, formatter: ContentFormatter, result: BroadcastResult):
    """Post to Instagram"""
    try:
        # Check credentials
        business_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        if not business_id or business_id.startswith("your_"):
            result.add_failure("instagram", "Instagram credentials not configured")
            return

        # Format content for Instagram
        formatted_content = formatter.format_for_instagram(
            post.content,
            hashtags=post.hashtags
        )

        # Instagram requires at least one image
        if not post.images:
            result.add_failure("instagram", "Instagram requires at least one image")
            return

        # Create client and post
        client = InstagramClient(
            business_account_id=business_id,
            access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN")
        )

        response = client.post(formatted_content, images=post.images)

        result.add_success("instagram", response.get("post_id", "unknown"), response)
        print(f"✅ Posted to Instagram: {response.get('post_id')}")

    except Exception as e:
        raise Exception(f"Instagram post failed: {e}")


def _update_dashboard(result: BroadcastResult):
    """Update Dashboard.md with broadcast results"""
    try:
        from src.utils.dashboard_updater import DashboardUpdater

        updater = DashboardUpdater()
        updater.update_social_media_stats(
            successful_posts=result.successful_platforms,
            failed_posts=len(result.failures),
            platforms=result.successes
        )
    except Exception as e:
        print(f"Warning: Failed to update dashboard: {e}")


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python broadcast_marketing.py <content> [platforms]")
        print("Example: python broadcast_marketing.py 'Hello World!' twitter,facebook")
        sys.exit(1)

    content = sys.argv[1]
    platforms = sys.argv[2].split(",") if len(sys.argv) > 2 else None

    result = broadcast_post(content, platforms=platforms)

    print("\n" + "=" * 60)
    print("Broadcast Results:")
    print("=" * 60)
    print(f"Total platforms: {result.total_platforms}")
    print(f"Successful: {result.successful_platforms}")
    print(f"Failed: {len(result.failures)}")

    if result.successes:
        print("\nSuccessful posts:")
        for success in result.successes:
            print(f"  ✅ {success['platform']}: {success['post_id']}")

    if result.failures:
        print("\nFailed posts:")
        for failure in result.failures:
            print(f"  ❌ {failure['platform']}: {failure['error']}")

    sys.exit(0 if result.is_success() else 1)
