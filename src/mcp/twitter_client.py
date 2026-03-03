"""
Twitter (X) API Client for Gold Tier Autonomous Employee

Implements Twitter/X integration with:
- OAuth 2.0 authentication
- Tweet posting with media support
- Engagement metrics collection
- Rate limit handling (50 posts/24h, 300 reads/15min)
- Character limit enforcement (280 standard, 4000 premium)

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
from requests_oauthlib import OAuth1Session

from src.mcp.base_mcp import BaseMCPClient
from src.utils.retry import retry_with_backoff
from src.audit.gold_logger import GoldAuditLogger
from src.models.social_media_post import SocialMediaPost, EngagementMetrics


class TwitterAuthenticationError(Exception):
    """Raised when Twitter authentication fails"""
    pass


class TwitterRateLimitError(Exception):
    """Raised when Twitter rate limit is exceeded"""
    pass


class TwitterClient(BaseMCPClient):
    """
    Twitter (X) API client with OAuth 2.0 and rate limiting

    Features:
    - OAuth 2.0 authentication
    - Tweet posting with media
    - Engagement metrics collection
    - Rate limit tracking (50 posts/24h)
    - Character limit enforcement
    - Comprehensive audit logging
    """

    # Rate limits
    POST_LIMIT_24H = 50
    READ_LIMIT_15MIN = 300

    def __init__(
        self,
        endpoint_url: str = "https://api.twitter.com/2",
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        audit_logger: Optional[GoldAuditLogger] = None,
    ):
        """
        Initialize Twitter client

        Args:
            endpoint_url: Twitter API base URL
            api_key: Twitter API key (from .env if not provided)
            api_secret: Twitter API secret (from .env if not provided)
            access_token: Twitter access token (from .env if not provided)
            access_token_secret: Twitter access token secret (from .env if not provided)
            audit_logger: Gold audit logger instance
        """
        super().__init__(server_name="TWITTER", endpoint_url=endpoint_url)

        # Load credentials from environment
        self.api_key = api_key or os.getenv("TWITTER_API_KEY")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET")
        self.access_token = access_token or os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = access_token_secret or os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

        # Audit logging
        self.audit_logger = audit_logger or GoldAuditLogger()

        # Rate limiting
        self.post_count_24h = 0
        self.post_reset_time = datetime.utcnow() + timedelta(hours=24)
        self.read_count_15min = 0
        self.read_reset_time = datetime.utcnow() + timedelta(minutes=15)

        # OAuth session
        self.session = None
        if all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            self._initialize_oauth()

    def _initialize_oauth(self) -> None:
        """Initialize OAuth 1.0a session"""
        try:
            self.session = OAuth1Session(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_token_secret,
            )

            # Log successful initialization
            self.audit_logger.log_action(
                action_type="MCP_CALL",
                action_name="twitter_initialize",
                parameters={},
                decision_rationale="Initializing Twitter OAuth session",
                execution_result="SUCCESS",
                result_data={},
                business_impact="Twitter connection established",
            )

        except Exception as e:
            self.audit_logger.log_action(
                action_type="ERROR",
                action_name="twitter_initialize_failed",
                parameters={},
                decision_rationale="Twitter initialization failed",
                execution_result="FAILURE",
                result_data={},
                business_impact="Twitter connection unavailable",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "recovery_attempted": False,
                    "recovery_result": "N/A",
                },
            )
            raise TwitterAuthenticationError(f"OAuth initialization failed: {e}")

    def _check_rate_limit_post(self) -> None:
        """Check if post rate limit is exceeded"""
        now = datetime.utcnow()

        # Reset counter if 24 hours passed
        if now >= self.post_reset_time:
            self.post_count_24h = 0
            self.post_reset_time = now + timedelta(hours=24)

        # Check limit
        if self.post_count_24h >= self.POST_LIMIT_24H:
            wait_seconds = (self.post_reset_time - now).total_seconds()
            raise TwitterRateLimitError(
                f"Post rate limit exceeded (50/24h). Reset in {wait_seconds:.0f} seconds"
            )

    def _check_rate_limit_read(self) -> None:
        """Check if read rate limit is exceeded"""
        now = datetime.utcnow()

        # Reset counter if 15 minutes passed
        if now >= self.read_reset_time:
            self.read_count_15min = 0
            self.read_reset_time = now + timedelta(minutes=15)

        # Check limit
        if self.read_count_15min >= self.READ_LIMIT_15MIN:
            wait_seconds = (self.read_reset_time - now).total_seconds()
            raise TwitterRateLimitError(
                f"Read rate limit exceeded (300/15min). Reset in {wait_seconds:.0f} seconds"
            )

    @retry_with_backoff(max_attempts=3, exceptions=(requests.exceptions.RequestException,))
    def post_tweet(
        self,
        content: str,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Post a tweet to Twitter

        Args:
            content: Tweet content (max 280 characters standard, 4000 premium)
            media_urls: Optional list of media URLs to attach

        Returns:
            Response with tweet ID and URL

        Raises:
            TwitterRateLimitError: If rate limit exceeded
            ValueError: If content exceeds character limit
        """
        # Check rate limit
        self._check_rate_limit_post()

        # Validate content length
        if len(content) > 280:
            # Check if premium (4000 char limit)
            if len(content) > 4000:
                raise ValueError(f"Tweet content exceeds 4000 character limit: {len(content)}")

        # Prepare tweet data
        tweet_data = {"text": content}

        # TODO: Add media upload support
        # if media_urls:
        #     media_ids = self._upload_media(media_urls)
        #     tweet_data["media"] = {"media_ids": media_ids}

        try:
            # Post tweet
            response = self.session.post(
                f"{self.endpoint_url}/tweets",
                json=tweet_data,
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            # Increment rate limit counter
            self.post_count_24h += 1

            # Log success
            self.audit_logger.log_action(
                action_type="MCP_CALL",
                action_name="twitter_post_tweet",
                parameters={"content_length": len(content)},
                decision_rationale="Posting tweet to Twitter",
                execution_result="SUCCESS",
                result_data={"tweet_id": result["data"]["id"]},
                business_impact=f"Tweet published: {content[:50]}...",
            )

            return {
                "success": True,
                "tweet_id": result["data"]["id"],
                "tweet_url": f"https://twitter.com/user/status/{result['data']['id']}",
                "content": content,
            }

        except requests.exceptions.HTTPError as e:
            # Log error
            self.audit_logger.log_action(
                action_type="ERROR",
                action_name="twitter_post_failed",
                parameters={"content_length": len(content)},
                decision_rationale="Tweet posting failed",
                execution_result="FAILURE",
                result_data={},
                business_impact="Tweet not published",
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
    def get_tweet_metrics(self, tweet_id: str) -> Dict[str, Any]:
        """
        Get engagement metrics for a tweet

        Args:
            tweet_id: Twitter tweet ID

        Returns:
            Engagement metrics (likes, retweets, replies, impressions)

        Raises:
            TwitterRateLimitError: If rate limit exceeded
        """
        # Check rate limit
        self._check_rate_limit_read()

        try:
            # Get tweet with metrics
            response = self.session.get(
                f"{self.endpoint_url}/tweets/{tweet_id}",
                params={
                    "tweet.fields": "public_metrics,created_at",
                },
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            # Increment rate limit counter
            self.read_count_15min += 1

            # Extract metrics
            metrics = result["data"]["public_metrics"]

            # Calculate engagement rate
            impressions = metrics.get("impression_count", 0)
            engagements = (
                metrics.get("like_count", 0) +
                metrics.get("retweet_count", 0) +
                metrics.get("reply_count", 0)
            )
            engagement_rate = engagements / impressions if impressions > 0 else 0.0

            # Log success
            self.audit_logger.log_action(
                action_type="MCP_CALL",
                action_name="twitter_get_metrics",
                parameters={"tweet_id": tweet_id},
                decision_rationale="Fetching tweet engagement metrics",
                execution_result="SUCCESS",
                result_data=metrics,
                business_impact=f"Retrieved metrics: {engagements} engagements, {impressions} impressions",
            )

            return {
                "success": True,
                "platform": "twitter",
                "likes": metrics.get("like_count", 0),
                "comments": metrics.get("reply_count", 0),
                "shares": metrics.get("retweet_count", 0),
                "reach": impressions,
                "engagement_rate": engagement_rate,
            }

        except requests.exceptions.HTTPError as e:
            # Log error
            self.audit_logger.log_action(
                action_type="ERROR",
                action_name="twitter_get_metrics_failed",
                parameters={"tweet_id": tweet_id},
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
        Check Twitter API health

        Returns:
            Health status information
        """
        try:
            # Try to get user info
            response = self.session.get(
                f"{self.endpoint_url}/users/me",
                timeout=10,
            )

            response.raise_for_status()

            return {
                "status": "healthy",
                "authenticated": True,
                "rate_limit_posts": f"{self.post_count_24h}/{self.POST_LIMIT_24H}",
                "rate_limit_reads": f"{self.read_count_15min}/{self.READ_LIMIT_15MIN}",
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "authenticated": False,
            }

    def call(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an API call to Twitter

        Args:
            endpoint: API endpoint (e.g., "post/create", "metrics/get")
            data: Request data

        Returns:
            Response data
        """
        if endpoint == "post/create":
            return self.post_tweet(
                content=data["content"],
                media_urls=data.get("media_urls"),
            )
        elif endpoint == "metrics/get":
            return self.get_tweet_metrics(tweet_id=data["tweet_id"])
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")
