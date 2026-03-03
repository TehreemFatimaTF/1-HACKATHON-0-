"""
Social Media Base Client for Gold Tier Autonomous Employee

Abstract base class for unified social media interface.
Part of User Story 3 - Unified Social Media Broadcasting.

Usage:
    from src.mcp.social_media_base import SocialMediaBase

    class MyPlatformClient(SocialMediaBase):
        def post(self, content, **kwargs):
            # Implementation
            pass
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.mcp.base_mcp import BaseMCPClient
from src.models.social_media_post import SocialMediaPost
from src.models.engagement_metrics import EngagementMetrics


class SocialMediaBase(BaseMCPClient, ABC):
    """
    Abstract base class for social media platform clients

    Provides unified interface for:
    - Posting content
    - Fetching engagement metrics
    - Rate limit handling
    - Platform-specific formatting
    """

    def __init__(self, platform_name: str, **kwargs):
        """
        Initialize social media client

        Args:
            platform_name: Name of the platform (twitter, facebook, instagram)
            **kwargs: Platform-specific configuration
        """
        super().__init__(name=platform_name)
        self.platform_name = platform_name
        self.rate_limits = self._get_rate_limits()

    @abstractmethod
    def post(self, content: str, **kwargs) -> Dict[str, Any]:
        """
        Post content to the platform

        Args:
            content: Text content to post
            **kwargs: Platform-specific parameters (images, hashtags, etc.)

        Returns:
            Dictionary with post_id and platform-specific response

        Raises:
            RateLimitError: If rate limit exceeded
            AuthenticationError: If authentication fails
            PostError: If post creation fails
        """
        pass

    @abstractmethod
    def get_engagement_metrics(self, post_id: str) -> EngagementMetrics:
        """
        Fetch engagement metrics for a post

        Args:
            post_id: Platform-specific post ID

        Returns:
            EngagementMetrics object with likes, comments, shares, etc.

        Raises:
            NotFoundError: If post not found
            APIError: If API request fails
        """
        pass

    @abstractmethod
    def format_content(self, post: SocialMediaPost) -> str:
        """
        Format content for platform-specific requirements

        Args:
            post: SocialMediaPost object

        Returns:
            Formatted content string

        Examples:
            - Twitter: Truncate to 280 chars, optimize hashtags
            - Instagram: Add hashtags at end, format for visual appeal
            - Facebook: Longer form content, link previews
        """
        pass

    @abstractmethod
    def _get_rate_limits(self) -> Dict[str, int]:
        """
        Get platform-specific rate limits

        Returns:
            Dictionary with rate limit configuration
            Example: {"posts_per_day": 50, "posts_per_hour": 10}
        """
        pass

    def check_rate_limit(self) -> bool:
        """
        Check if rate limit allows posting

        Returns:
            True if posting is allowed, False if rate limited
        """
        # Default implementation - override for platform-specific logic
        return True

    def validate_content(self, content: str) -> bool:
        """
        Validate content meets platform requirements

        Args:
            content: Content to validate

        Returns:
            True if valid, False otherwise
        """
        if not content or not content.strip():
            return False

        # Check minimum length
        if len(content.strip()) < 1:
            return False

        return True

    def get_platform_name(self) -> str:
        """Get platform name"""
        return self.platform_name

    def create_post_object(self, content: str, **kwargs) -> SocialMediaPost:
        """
        Create SocialMediaPost object

        Args:
            content: Post content
            **kwargs: Additional post parameters

        Returns:
            SocialMediaPost object
        """
        return SocialMediaPost(
            platform=self.platform_name,
            content=content,
            timestamp=datetime.now(),
            metadata=kwargs
        )

    def log_post(self, post_id: str, content: str, result: Dict[str, Any]):
        """
        Log post to audit trail

        Args:
            post_id: Platform post ID
            content: Post content
            result: Post result from API
        """
        # Integration with Gold Audit Logger
        try:
            from src.audit.gold_logger import GoldAuditLogger

            logger = GoldAuditLogger()
            logger.log_action(
                action_type="social_media_post",
                parameters={
                    "platform": self.platform_name,
                    "post_id": post_id,
                    "content_preview": content[:100]
                },
                result=result,
                business_impact=f"Posted to {self.platform_name}"
            )
        except Exception as e:
            print(f"Warning: Failed to log post to audit trail: {e}")


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass


class PostError(Exception):
    """Raised when post creation fails"""
    pass


class NotFoundError(Exception):
    """Raised when resource not found"""
    pass
