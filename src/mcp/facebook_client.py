"""
Facebook Graph API Client for Gold Tier Autonomous Employee

Implements Facebook integration with:
- OAuth 2.0 authentication
- Post creation with media support
- Engagement metrics collection
- Rate limit handling (200 calls/hour)
- Page and user posting support

Architecture:
- Extends BaseMCPClient for consistent MCP interface
- Uses retry decorator for transient failures
- Integrates with circuit breaker for fault tolerance
- Comprehensive error handling and recovery
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import requests

from src.mcp.base_mcp import BaseMCPClient
from src.utils.retry import retry_with_backoff
from src.audit.gold_logger import GoldAuditLogger


class FacebookAuthenticationError(Exception):
    """Raised when Facebook authentication fails"""
    pass


class FacebookRateLimitError(Exception):
    """Raised when Facebook rate limit is exceeded"""
    pass


class FacebookClient(BaseMCPClient):
    """
    Facebook Graph API client with OAuth 2.0 and rate limiting

    Features:
    - OAuth 2.0 authentication
    - Post creation with media
    - Engagement metrics collection
    - Rate limit tracking (200 calls/hour)
    - Page and user posting
    - Comprehensive audit logging
    """

    # Rate limits
    CALL_LIMIT_HOUR = 200

    def __init__(
        self,
        endpoint_url: str = "https://graph.facebook.com/v18.0",
        access_token: Optional[str] = None,
        page_id: Optional[str] = None,
        audit_logger: Optional[GoldAuditLogger] = None,
    ):
        """
        Initialize Facebook client

        Args:
            endpoint_url: Facebook Graph API base URL
            access_token: Facebook access token (from .env if not provided)
            page_id: Facebook page ID for posting (from .env if not provided)
            audit_logger: Gold audit logger instance
        """
        super().__init__(server_name="FACEBOOK", endpoint_url=endpoint_url)

        # Load credentials from environment
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID")

        # Audit logging
        self.audit_logger = audit_logger or GoldAuditLogger()

        # Rate limiting
        self.call_count_hour = 0
        self.call_reset_time = datetime.utcnow() + timedelta(hours=1)

        # Verify authentication
        if self.access_token:
            self._verify_token()

    def _verify_token(self) -> None:
        """Verify Facebook access token"""
        try:
            response = requests.get(
                f"{self.endpoint_url}/me",
                params={"access_token": self.access_token},
                timeout=10,
            )

            response.raise_for_status()

            # Log successful verification
            self.audit_logger.log_action(
                action_type="MCP_CALL",
                action_name="facebook_verify_token",
                parameters={},
                decision_rationale="Verifying Facebook access token",
                execution_result="SUCCESS",
                result_data={},
                business_impact="Facebook connection established",
            )

        except Exception as e:
            self.audit_logger.log_action(
                action_type="ERROR",
                action_name="facebook_verify_failed",
                parameters={},
                decision_rationale="Facebook token verification failed",
                execution_result="FAILURE",
                result_data={},
                business_impact="Facebook connection unavailable",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "recovery_attempted": False,
                    "recovery_result": "N/A",
                },
            )
            raise FacebookAuthenticationError(f"Token verification failed: {e}")

    def _check_rate_limit(self) -> None:
        """Check if rate limit is exceeded"""
        now = datetime.utcnow()

        # Reset counter if 1 hour passed
        if now >= self.call_reset_time:
            self.call_count_hour = 0
            self.call_reset_time = now + timedelta(hours=1)

        # Check limit
        if self.call_count_hour >= self.CALL_LIMIT_HOUR:
            wait_seconds = (self.call_reset_time - now).total_seconds()
            raise FacebookRateLimitError(
                f"Rate limit exceeded (200/hour). Reset in {wait_seconds:.0f} seconds"
            )

    @retry_with_backoff(max_attempts=3, exceptions=(requests.exceptions.RequestException,))
    def post_to_page(
        self,
        content: str,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Post content to Facebook page

        Args:
            content: Post content
            media_urls: Optional list of media URLs to attach

        Returns:
            Response with post ID and URL

        Raises:
            FacebookRateLimitError: If rate limit exceeded
        """
        # Check rate limit
        self._check_rate_limit()

        # Prepare post data
        post_data = {
            "message": content,
            "access_token": self.access_token,
        }

        # TODO: Add media upload support
        # if media_urls:
        #     post_data["attached_media"] = self._upload_media(media_urls)

        try:
            # Post to page feed
            response = requests.post(
                f"{self.endpoint_url}/{self.page_id}/feed",
                data=post_data,
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            # Increment rate limit counter
            self.call_count_hour += 1

            # Log success
            self.audit_logger.log_action(
                action_type="MCP_CALL",
                action_name="facebook_post",
                parameters={"content_length": len(content)},
                decision_rationale="Posting to Facebook page",
                execution_result="SUCCESS",
                result_data={"post_id": result["id"]},
                business_impact=f"Facebook post published: {content[:50]}...",
            )

            return {
                "success": True,
                "post_id": result["id"],
                "post_url": f"https://facebook.com/{result['id']}",
                "content": content,
            }

        except requests.exceptions.HTTPError as e:
            # Log error
            self.audit_logger.log_action(
                action_type="ERROR",
                action_name="facebook_post_failed",
                parameters={"content_length": len(content)},
                decision_rationale="Facebook post failed",
                execution_result="FAILURE",
                result_data={},
                business_impact="Facebook post not published",
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
        Get engagement metrics for a Facebook post

        Args:
            post_id: Facebook post ID

        Returns:
            Engagement metrics (likes, comments, shares, reach)

        Raises:
            FacebookRateLimitError: If rate limit exceeded
        """
        # Check rate limit
        self._check_rate_limit()

        try:
            # Get post with metrics
            response = requests.get(
                f"{self.endpoint_url}/{post_id}",
                params={
                    "fields": "likes.summary(true),comments.summary(true),shares,insights.metric(post_impressions)",
                    "access_token": self.access_token,
                },
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            # Increment rate limit counter
            self.call_count_hour += 1

            # Extract metrics
            likes = result.get("likes", {}).get("summary", {}).get("total_count", 0)
            comments = result.get("comments", {}).get("summary", {}).get("total_count", 0)
            shares = result.get("shares", {}).get("count", 0)

            # Get impressions from insights
            impressions = 0
            if "insights" in result and result["insights"]["data"]:
                impressions = result["insights"]["data"][0].get("values", [{}])[0].get("value", 0)

            # Calculate engagement rate
            engagements = likes + comments + shares
            engagement_rate = engagements / impressions if impressions > 0 else 0.0

            # Log success
            self.audit_logger.log_action(
                action_type="MCP_CALL",
                action_name="facebook_get_metrics",
                parameters={"post_id": post_id},
                decision_rationale="Fetching Facebook post metrics",
                execution_result="SUCCESS",
                result_data={"likes": likes, "comments": comments, "shares": shares},
                business_impact=f"Retrieved metrics: {engagements} engagements, {impressions} impressions",
            )

            return {
                "success": True,
                "platform": "facebook",
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "reach": impressions,
                "engagement_rate": engagement_rate,
            }

        except requests.exceptions.HTTPError as e:
            # Log error
            self.audit_logger.log_action(
                action_type="ERROR",
                action_name="facebook_get_metrics_failed",
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
        Check Facebook API health

        Returns:
            Health status information
        """
        try:
            # Try to get page info
            response = requests.get(
                f"{self.endpoint_url}/{self.page_id}",
                params={"access_token": self.access_token},
                timeout=10,
            )

            response.raise_for_status()

            return {
                "status": "healthy",
                "authenticated": True,
                "rate_limit": f"{self.call_count_hour}/{self.CALL_LIMIT_HOUR}",
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "authenticated": False,
            }

    def call(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an API call to Facebook

        Args:
            endpoint: API endpoint (e.g., "post/create", "metrics/get")
            data: Request data

        Returns:
            Response data
        """
        if endpoint == "post/create":
            return self.post_to_page(
                content=data["content"],
                media_urls=data.get("media_urls"),
            )
        elif endpoint == "metrics/get":
            return self.get_post_metrics(post_id=data["post_id"])
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")
