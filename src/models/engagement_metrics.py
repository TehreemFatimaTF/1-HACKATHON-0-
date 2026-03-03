"""
Engagement Metrics Model for Gold Tier Autonomous Employee

Tracks social media engagement metrics across platforms.
Part of User Story 3 - Unified Social Media Broadcasting.

Usage:
    from src.models.engagement_metrics import EngagementMetrics

    metrics = EngagementMetrics(
        platform="twitter",
        post_id="123456",
        likes=100,
        comments=20,
        shares=15
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class Platform(Enum):
    """Social media platforms"""
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"


class SentimentScore(Enum):
    """Sentiment classification"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


@dataclass
class EngagementMetrics:
    """
    Social media engagement metrics for a post

    Attributes:
        platform: Social media platform
        post_id: Platform-specific post ID
        likes: Number of likes/reactions
        comments: Number of comments
        shares: Number of shares/retweets
        reach: Number of people reached
        impressions: Number of times post was displayed
        engagement_rate: Calculated engagement rate (%)
        sentiment: Overall sentiment of engagement
        timestamp: When metrics were collected
        metadata: Additional platform-specific data
    """

    platform: str
    post_id: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    reach: int = 0
    impressions: int = 0
    engagement_rate: float = 0.0
    sentiment: str = "neutral"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate engagement rate after initialization"""
        if self.impressions > 0:
            total_engagement = self.likes + self.comments + self.shares
            self.engagement_rate = round((total_engagement / self.impressions) * 100, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "platform": self.platform,
            "post_id": self.post_id,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "reach": self.reach,
            "impressions": self.impressions,
            "engagement_rate": self.engagement_rate,
            "sentiment": self.sentiment,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EngagementMetrics":
        """Create from dictionary"""
        data = data.copy()
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    def calculate_score(self) -> float:
        """
        Calculate overall engagement score (0-100)

        Weighted formula:
        - Likes: 1 point
        - Comments: 3 points (more valuable)
        - Shares: 5 points (most valuable)
        """
        score = (self.likes * 1) + (self.comments * 3) + (self.shares * 5)

        # Normalize to 0-100 scale based on reach
        if self.reach > 0:
            normalized = (score / self.reach) * 100
            return min(100, round(normalized, 2))

        return 0.0

    def is_viral(self, threshold: float = 10.0) -> bool:
        """
        Check if post is viral based on engagement rate

        Args:
            threshold: Engagement rate threshold (default: 10%)

        Returns:
            True if engagement rate exceeds threshold
        """
        return self.engagement_rate >= threshold

    def needs_attention(self) -> bool:
        """
        Check if post needs attention (negative sentiment or low engagement)

        Returns:
            True if post requires review
        """
        return (
            self.sentiment == "negative" or
            (self.impressions > 100 and self.engagement_rate < 1.0)
        )


@dataclass
class AggregatedMetrics:
    """
    Aggregated metrics across multiple posts or time period

    Attributes:
        platform: Social media platform
        total_posts: Number of posts
        total_likes: Sum of all likes
        total_comments: Sum of all comments
        total_shares: Sum of all shares
        total_reach: Sum of all reach
        total_impressions: Sum of all impressions
        avg_engagement_rate: Average engagement rate
        sentiment_breakdown: Count of positive/neutral/negative posts
        period_start: Start of aggregation period
        period_end: End of aggregation period
    """

    platform: str
    total_posts: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_reach: int = 0
    total_impressions: int = 0
    avg_engagement_rate: float = 0.0
    sentiment_breakdown: Dict[str, int] = field(default_factory=lambda: {
        "positive": 0,
        "neutral": 0,
        "negative": 0
    })
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "platform": self.platform,
            "total_posts": self.total_posts,
            "total_likes": self.total_likes,
            "total_comments": self.total_comments,
            "total_shares": self.total_shares,
            "total_reach": self.total_reach,
            "total_impressions": self.total_impressions,
            "avg_engagement_rate": self.avg_engagement_rate,
            "sentiment_breakdown": self.sentiment_breakdown,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None
        }
