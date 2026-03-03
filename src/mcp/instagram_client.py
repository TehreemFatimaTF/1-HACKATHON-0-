"""
Instagram API Client for Gold Tier Autonomous Employee

Implements Instagram integration with:
- OAuth 2.0 authentication via Facebook Graph API
- Post creation with media support (required for Instagram)
- Engagement metrics collection
- Rate limit handling (25 posts/day)
- Hashtag optimization (max 30 hashtags)

Architecture:
- Extends BaseMCPClient for consistent MCP interface
- Uses retry decorator for transient failures
- Integrates with circuit breaker for fault tolerance
- Comprehensive error handling and recovery

Note: Instagram requires media (photo/video) for all posts
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import requests

from src.mcp.base_mcp import BaseMCPClient
from src.utils.retry import retry_with_backoff
from src.audit.gold_logger import GoldAuditLogger


class InstagramAuthenticationError(Exception):
    """Raised when Instagram authentication fails"""
    pass


class InstagramRateLimitError(Exception):
    """Raised when Instagram rate limit is exceeded"""
    pass


class InstagramClient(BaseMCPClient):
    """
    Instagram API client with OAuth 2.0 and rate limiting

    Features:
    - OAuth 2.0 authentication via Facebook
    - Post creation with media (required)
    - Engagement metrics collection
    - Rate limit tracking (25 posts/day)
    - Hashtag optimization (max 30)
    - Comprehensive audit logging
    """

    # Rate limits
    POST_LIMIT_DAY = 25
    MAX_HASHTAGS = 30
    MAX_CAPTION_LENGTH = 2200

    def __init__(
        self,
        endpoint_url: str = "https://graph.facebook.com/v18.0",
        access_token: Optional[str] = None,
        instagram_account_id: Optional[str] = None,
        audit_logger: Optional[GoldAuditLogger] = None,
    ):
        """
        Initialize Instagram client

        Args:
            endpoint_url: Instagram Graph API base URL
            access_token: Facebook access token with Instagram permissions
            instagram_account_id: Instagram Business Account ID
            audit_logger: Gold audit logger instance
        """
        super().__init__(server_name="INSTAGRAM", endpoint_url=endpoint_url)

        # Load credentials from environment
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.instagram_account_id = instagram_account_id or os.getenv("INSTAGRAM_ACCOUNT_ID")

        # Audit logging
        self.audit_logger = audit_logger or GoldAuditLogger()

        # Rate limiting
        self.post_count_day = 0
        self.post_reset_time = datetime.utcnow() + timedelta(days=1)

        # Verify authentication
        if self.access_token and self.instagram_account_id:
            self._verify_account()

    def _verify_account(self) -> None:
        """Verify Instagram account access"""
        try:
            response = requests.get(
                f"{self.endpoint_url}/{self.instagram_account_id}",
                params={
                    "fields": "id,username",
                    "access_token": self.access_token,
                },
                timeout=10,
            )

            response.raise_for_status()

            # Log successful verification
            self.audit_logger.log_action(
                action_type="MCP_CALL",
                action_name="instagram_verify_account",
                parameters={},
                decision_rationale="Verifying Instagram account access",
                execution_result="SUCCESS",
                result_data={},
                business_impact="Instagram connection established",
            )

        except Exception as e:
            self.audit_logger.log_action(
                action_type="ERROR",
                action_name="instagram_verify_failed",
                parameters={},
                decision_rationale="Instagram account verification failed",
                execution_result="FAILURE",
                result_data={},
                business_impact="Instagram connection unavailable",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "recovery_attempted": False,
                    "recovery_result": "N/A",
                },
            )
            raise InstagramAuthenticationError(f"Account verification failed: {e}")

    def _check_rate_limit(self) -> None:
        """Check if post rate limit is exceeded"""
        now = datetime.utcnow()

        # Reset counter if 24 hours passed
        if now >= self.post_reset_time:
            self.post_count_day = 0
            self.post_reset_time = now + timedelta(days=1)

        # Check limit
        if self.post_count_day >= self.POST_LIMIT_DAY:
            wait_seconds = (self.post_reset_time - now).total_seconds()
            raise InstagramRateLimitError(
                f"Post rate limit exceeded (25/day). Reset in {wait_seconds:.0f} seconds"
            )

    def _validate_content(self, caption: str, hashtags: List[str]) -> None:
        """
        Validate Instagram content

        Args:
            caption: Post caption
            hashtags: List of hashtags

        Raises:
            ValueError: If validation fails
        """
        # Check caption length
        if len(caption) > self.MAX_CAPTION_LENGTH:
            raise ValueError(
                f"Caption length ({len(caption)}) exceeds Instagram limit ({self.MAX_CAPTION_LENGTH})"
            )

        # Check hashtag count
        if len(hashtags) > self.MAX_HASHTAGS:
            raise ValueError(
                f"Hashtag count ({len(hashtags)}) exceeds Instagram limit ({self.MAX_HASHTAGS})"
            )

    @retry_with_backoff(max_attempts=3, exceptions=(requests.exceptions.RequestException,))
    def create_media_container(
        self,
        image_url: str,
        caption: str,
        hashtags: List[str]
    ) -> str:
        """
        Create Instagram media container (step 1 of posting)

        Args:
            image_url: URL of image to post
            caption: Post caption
            hashtags: List of hashtags

        Returns:
            Media container ID

        Raises:
            InstagramRateLimitError: If rate limit exceeded
        """
        # Check rate limit
        self._check_rate_limit()

        # Validate content
        self._validate_content(caption, hashtags)

        # Combine caption with hashtags
        full_caption = f"{caption}\n\n{' '.join(hashtags)}"

        try:
            # Create media container
            response = requests.post(
                f"{self.endpoint_url}/{self.instagram_account_id}/media",
                data={
                    "image_url": image_url,
                    "caption": full_caption,
                    "access_token": self.access_token,
                },
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            return result["id"]

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Failed to create media container: {e}")

    @retry_with_backoff(max_attempts=3, exceptions=(requests.exceptions.RequestException,))
    def publish_media_container(self, container_id: str) -> Dict[str, Any]:
        """
        Publish Instagram media container (step 2 of posting)

        Args:
            container_id: Media container ID from create_media_container

        Returns:
            Response with post ID

        Raises:
            InstagramRateLimitError: If rate limit exceeded
        """
        try:
            # Publish container
            response = requests.post(
                f"{self.endpoint_url}/{self.instagram_account_id}/media_publish",
                data={
                    "creation_id": container_id,
                    "access_token": self.access_token,
                },
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            # Increment rate limit counter
            self.post_count_day += 1

            return {
                "success": True,
                "post_id": result["id"],
                "post_url": f"https://instagram.com/p/{result['id']}",
            }

        except requests.exceptions.HTTPError as e:
            return {
                "success": False,
                "error": str(e),
            }

    def post_to_instagram(
        self,
        content: str,
        hashtags: List[str],
        image_url: str
    ) -> Dict[str, Any]:
        """
        Post content to Instagram (2-step process)

        Args:
            content: Post caption
            hashtags: List of hashtags
            image_url: URL of image to post (required for Instagram)

        Returns:
            Response with post ID and URL

        Raises:
            InstagramRateLimitError: If rate limit exceeded
            ValueError: If content validation fails
        """
        if not image_url:
            raise ValueError("Instagram requires an image URL for all posts")

        try:
            # Step 1: Create media container
            container_id = self.create_media_container(image_url, content, hashtags)

            # Step 2: Publish container
            result = self.publish_media_container(container_id)

            if result["success"]:
                # Log success
                self.audit_logger.log_action(
                    action_type="MCP_CALL",
                    action_name="instagram_post",
                    parameters={
                        "caption_length": len(content),
                        "hashtag_count": len(hashtags),
                    },
                    decision_rationale="Posting to Instagram",
                    execution_result="SUCCESS",
                    result_data={"post_id": result["post_id"]},
                    business_impact=f"Instagram post published: {content[:50]}...",
                )

            return result

        except Exception as e:
            # Log error
            self.audit_logger.log_action(
                action_type="ERROR",
                action_name="instagram_post_failed",
                parameters={"caption_length": len(content)},
                decision_rationale="Instagram post failed",
                execution_result="FAILURE",
                result_data={},
                business_impact="Instagram post not published",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "recovery_attempted": False,
                    "recovery_result": "N/A",
                },
            )

            return {
                "success": False,
                "error": str(e),
            }

    @retry_with_backoff(max_attempts=3, exceptions=(requests.exceptions.RequestException,))
    def get_post_metrics(self, post_id: str) -> Dict[str, Any]:
        """
        Get engagement metrics for an Instagram post

        Args:
            post_id: Instagram post ID

        Returns:
            Engagement metrics (likes, comments, shares, reach)
        """
        try:
            # Get post with metrics
            response = requests.get(
                f"{self.endpoint_url}/{post_id}/insights",
                params={
                    "metric": "engagement,impressions,reach,saved",
                    "access_token": self.access_token,
                },
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            # Extract metrics
            metrics = {item["name"]: item["values"][0]["value"] for item in result["data"]}

            # Get likes and comments separately
            post_response = requests.get(
                f"{self.endpoint_url}/{post_id}",
                params={
                    "fields": "like_count,comments_count",
                    "access_token": self.access_token,
                },
                timeout=30,
            )
            post_response.raise_for_status()
            post_data = post_response.json()

            likes = post_data.get("like_count", 0)
            comments = post_data.get("comments_count", 0)
            reach = metrics.get("reach", 0)
            engagement = metrics.get("engagement", 0)

            # Calculate engagement rate
            engagement_rate = engagement / reach if reach > 0 else 0.0

            # Log success
            self.audit_logger.log_action(
                action_type="MCP_CALL",
                action_name="instagram_get_metrics",
                parameters={"post_id": post_id},
                decision_rationale="Fetching Instagram post metrics",
                execution_result="SUCCESS",
                result_data={"likes": likes, "comments": comments, "reach": reach},
                business_impact=f"Retrieved metrics: {engagement} engagements, {reach} reach",
            )

            return {
                "success": True,
                "platform": "instagram",
                "likes": likes,
                "comments": comments,
                "shares": metrics.get("saved", 0),  # Instagram doesn't have shares, use saves
                "reach": reach,
                "engagement_rate": engagement_rate,
            }

        except requests.exceptions.HTTPError as e:
            # Log error
            self.audit_logger.log_action(
                action_type="ERROR",
                action_name="instagram_get_metrics_failed",
                parameters={"post_id": post_id},
                decision_rationale="Metrics fetch failed",
                execution_result="FAILURE",
                result_data={},
                business_impact="Metrics unavailable",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "recovery_attempted": False,
                    "recovery_result": "N/A",
                },
            )

            return {
                "success": False,
                "error": str(e),
            }

    def health_check(self) -> Dict[str, Any]:
        """
        Check Instagram API health

        Returns:
            Health status information
        """
        try:
            # Try to get account info
            response = requests.get(
                f"{self.endpoint_url}/{self.instagram_account_id}",
                params={
                    "fields": "id,username",
                    "access_token": self.access_token,
                },
                timeout=10,
            )

            response.raise_for_status()

            return {
                "status": "healthy",
                "authenticated": True,
                "rate_limit": f"{self.post_count_day}/{self.POST_LIMIT_DAY}",
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "authenticated": False,
            }

    def call(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an API call to Instagram

        Args:
            endpoint: API endpoint (e.g., "post/create", "metrics/get")
            data: Request data

        Returns:
            Response data
        """
        if endpoint == "post/create":
            return self.post_to_instagram(
                content=data["content"],
                hashtags=data.get("hashtags", []),
                image_url=data.get("image_url"),
            )
        elif endpoint == "metrics/get":
            return self.get_post_metrics(post_id=data["post_id"])
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")
