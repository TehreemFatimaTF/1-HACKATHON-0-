"""
SocialMediaPost model for Gold Tier Autonomous Employee

Represents content published across multiple social media platforms with:
- Platform-specific content variants
- Engagement metrics tracking
- Sentiment analysis results
- Multi-platform publication status

Supports: Twitter/X, Facebook, Instagram
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import json
import os


class PostStatus(str, Enum):
    """Social media post status"""
    DRAFT = "DRAFT"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"  # Published to some but not all platforms


class SentimentClass(str, Enum):
    """Sentiment classification"""
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


@dataclass
class PlatformVariant:
    """Platform-specific content formatting"""
    content: str
    character_count: int
    media_count: int
    hashtag_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "character_count": self.character_count,
            "media_count": self.media_count,
            "hashtag_count": self.hashtag_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlatformVariant":
        return cls(
            content=data["content"],
            character_count=data["character_count"],
            media_count=data["media_count"],
            hashtag_count=data["hashtag_count"],
        )


@dataclass
class EngagementMetrics:
    """Engagement metrics for a specific platform"""
    platform: str
    likes: int
    comments: int
    shares: int
    reach: int
    engagement_rate: float
    collected_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "reach": self.reach,
            "engagement_rate": self.engagement_rate,
            "collected_at": self.collected_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EngagementMetrics":
        return cls(
            platform=data["platform"],
            likes=data["likes"],
            comments=data["comments"],
            shares=data["shares"],
            reach=data["reach"],
            engagement_rate=data["engagement_rate"],
            collected_at=datetime.fromisoformat(data["collected_at"]),
        )


@dataclass
class SentimentScores:
    """Sentiment analysis results"""
    overall_polarity: float  # -1.0 (negative) to +1.0 (positive)
    overall_classification: SentimentClass
    comment_sentiments: List[Dict[str, Any]]
    analyzed_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_polarity": self.overall_polarity,
            "overall_classification": self.overall_classification.value,
            "comment_sentiments": self.comment_sentiments,
            "analyzed_at": self.analyzed_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SentimentScores":
        return cls(
            overall_polarity=data["overall_polarity"],
            overall_classification=SentimentClass(data["overall_classification"]),
            comment_sentiments=data["comment_sentiments"],
            analyzed_at=datetime.fromisoformat(data["analyzed_at"]),
        )


@dataclass
class SocialMediaPost:
    """
    Content published across multiple social media platforms

    Validation Rules:
    - content length <= 2200 characters (Instagram limit)
    - platform_variants.twitter.character_count <= 280 (or 4000 for premium)
    - hashtags.length <= 30 (Instagram limit)
    - status = PARTIAL if published to some but not all platforms
    - engagement_rate must be between 0.0 and 1.0
    """
    content: str
    hashtags: List[str]
    post_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform_variants: Dict[str, PlatformVariant] = field(default_factory=dict)
    media_urls: List[str] = field(default_factory=list)
    publication_timestamps: Dict[str, Optional[datetime]] = field(default_factory=dict)
    platform_post_ids: Dict[str, Optional[str]] = field(default_factory=dict)
    engagement_metrics: List[EngagementMetrics] = field(default_factory=list)
    sentiment_scores: Optional[SentimentScores] = None
    status: PostStatus = PostStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate post after initialization"""
        self.validate()

    def validate(self) -> bool:
        """
        Validate social media post according to business rules

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        # Validate content length (Instagram limit)
        if len(self.content) > 2200:
            raise ValueError(f"Content length ({len(self.content)}) exceeds Instagram limit (2200)")

        # Validate hashtag count (Instagram limit)
        if len(self.hashtags) > 30:
            raise ValueError(f"Hashtag count ({len(self.hashtags)}) exceeds Instagram limit (30)")

        # Validate Twitter variant if present
        if "twitter" in self.platform_variants:
            twitter_variant = self.platform_variants["twitter"]
            if twitter_variant.character_count > 280:
                # Allow up to 4000 for Twitter Premium
                if twitter_variant.character_count > 4000:
                    raise ValueError(
                        f"Twitter content length ({twitter_variant.character_count}) exceeds limit (4000)"
                    )

        # Validate engagement rates
        for metrics in self.engagement_metrics:
            if not (0.0 <= metrics.engagement_rate <= 1.0):
                raise ValueError(
                    f"Engagement rate ({metrics.engagement_rate}) must be between 0.0 and 1.0"
                )

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert post to dictionary for JSON serialization"""
        return {
            "post_id": self.post_id,
            "content": self.content,
            "platform_variants": {
                platform: variant.to_dict()
                for platform, variant in self.platform_variants.items()
            },
            "media_urls": self.media_urls,
            "hashtags": self.hashtags,
            "publication_timestamps": {
                platform: ts.isoformat() if ts else None
                for platform, ts in self.publication_timestamps.items()
            },
            "platform_post_ids": self.platform_post_ids,
            "engagement_metrics": [m.to_dict() for m in self.engagement_metrics],
            "sentiment_scores": self.sentiment_scores.to_dict() if self.sentiment_scores else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SocialMediaPost":
        """Create post from dictionary"""
        return cls(
            post_id=data.get("post_id", str(uuid.uuid4())),
            content=data["content"],
            platform_variants={
                platform: PlatformVariant.from_dict(variant)
                for platform, variant in data.get("platform_variants", {}).items()
            },
            media_urls=data.get("media_urls", []),
            hashtags=data.get("hashtags", []),
            publication_timestamps={
                platform: datetime.fromisoformat(ts) if ts else None
                for platform, ts in data.get("publication_timestamps", {}).items()
            },
            platform_post_ids=data.get("platform_post_ids", {}),
            engagement_metrics=[
                EngagementMetrics.from_dict(m)
                for m in data.get("engagement_metrics", [])
            ],
            sentiment_scores=SentimentScores.from_dict(data["sentiment_scores"])
            if data.get("sentiment_scores") else None,
            status=PostStatus(data.get("status", "DRAFT")),
            created_at=datetime.fromisoformat(data["created_at"])
            if isinstance(data.get("created_at"), str)
            else data.get("created_at", datetime.utcnow()),
            last_updated=datetime.fromisoformat(data["last_updated"])
            if isinstance(data.get("last_updated"), str)
            else data.get("last_updated", datetime.utcnow()),
        )

    def save(self, directory: str = "Done") -> str:
        """
        Save post to JSON file

        Args:
            directory: Directory to save post file

        Returns:
            Path to saved file
        """
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"post_{self.post_id}.json")

        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        return filepath

    @classmethod
    def load(cls, post_id: str, directory: str = "Done") -> "SocialMediaPost":
        """
        Load post from JSON file

        Args:
            post_id: Post ID to load
            directory: Directory containing post file

        Returns:
            Loaded SocialMediaPost instance
        """
        filepath = os.path.join(directory, f"post_{post_id}.json")

        with open(filepath, "r") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def mark_publishing(self) -> None:
        """Mark post as currently publishing"""
        self.status = PostStatus.PUBLISHING
        self.last_updated = datetime.utcnow()

    def mark_published(self, platforms: List[str]) -> None:
        """
        Mark post as published

        Args:
            platforms: List of platforms successfully published to
        """
        total_platforms = len(self.platform_variants)
        published_count = len(platforms)

        if published_count == 0:
            self.status = PostStatus.FAILED
        elif published_count < total_platforms:
            self.status = PostStatus.PARTIAL
        else:
            self.status = PostStatus.PUBLISHED

        self.last_updated = datetime.utcnow()

    def record_publication(
        self,
        platform: str,
        platform_post_id: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Record successful publication to a platform

        Args:
            platform: Platform name (twitter, facebook, instagram)
            platform_post_id: Platform-specific post ID
            timestamp: Publication timestamp (defaults to now)
        """
        self.platform_post_ids[platform] = platform_post_id
        self.publication_timestamps[platform] = timestamp or datetime.utcnow()
        self.last_updated = datetime.utcnow()

    def add_engagement_metrics(self, metrics: EngagementMetrics) -> None:
        """
        Add engagement metrics for a platform

        Args:
            metrics: EngagementMetrics instance
        """
        # Remove old metrics for this platform
        self.engagement_metrics = [
            m for m in self.engagement_metrics
            if m.platform != metrics.platform
        ]

        # Add new metrics
        self.engagement_metrics.append(metrics)
        self.last_updated = datetime.utcnow()

    def update_sentiment(self, sentiment: SentimentScores) -> None:
        """
        Update sentiment analysis results

        Args:
            sentiment: SentimentScores instance
        """
        self.sentiment_scores = sentiment
        self.last_updated = datetime.utcnow()

    def get_total_engagement(self) -> Dict[str, int]:
        """
        Get total engagement across all platforms

        Returns:
            Dictionary with total likes, comments, shares, reach
        """
        total = {
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "reach": 0,
        }

        for metrics in self.engagement_metrics:
            total["likes"] += metrics.likes
            total["comments"] += metrics.comments
            total["shares"] += metrics.shares
            total["reach"] += metrics.reach

        return total

    def get_average_engagement_rate(self) -> float:
        """
        Get average engagement rate across all platforms

        Returns:
            Average engagement rate (0.0 to 1.0)
        """
        if not self.engagement_metrics:
            return 0.0

        total_rate = sum(m.engagement_rate for m in self.engagement_metrics)
        return total_rate / len(self.engagement_metrics)

    def is_published_to(self, platform: str) -> bool:
        """
        Check if post is published to a specific platform

        Args:
            platform: Platform name

        Returns:
            True if published to platform
        """
        return (
            platform in self.platform_post_ids
            and self.platform_post_ids[platform] is not None
        )

    def get_published_platforms(self) -> List[str]:
        """
        Get list of platforms post is published to

        Returns:
            List of platform names
        """
        return [
            platform
            for platform, post_id in self.platform_post_ids.items()
            if post_id is not None
        ]
