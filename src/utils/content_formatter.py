"""
Content Formatter for Platform-Specific Optimization

Formats content for different social media platforms with:
- Character limit handling (280 for Twitter, 2200 for Instagram)
- Hashtag optimization (max 30 for Instagram)
- Platform-specific formatting conventions
- Automatic truncation with ellipsis
"""

from typing import List


def format_for_platform(
    content: str,
    platform: str,
    hashtags: List[str] = None
) -> str:
    """
    Format content for a specific social media platform

    Args:
        content: Base content to format
        platform: Target platform (twitter, facebook, instagram)
        hashtags: List of hashtags to include

    Returns:
        Formatted content optimized for the platform
    """
    hashtags = hashtags or []

    if platform == "twitter":
        return format_for_twitter(content, hashtags)
    elif platform == "facebook":
        return format_for_facebook(content, hashtags)
    elif platform == "instagram":
        return format_for_instagram(content, hashtags)
    else:
        return content


def format_for_twitter(content: str, hashtags: List[str]) -> str:
    """
    Format content for Twitter (280 character limit)

    Args:
        content: Base content
        hashtags: List of hashtags

    Returns:
        Twitter-formatted content
    """
    # Twitter character limit
    TWITTER_LIMIT = 280

    # Combine hashtags
    hashtag_str = " ".join(hashtags) if hashtags else ""

    # Calculate available space for content
    hashtag_length = len(hashtag_str) + (1 if hashtag_str else 0)  # +1 for space
    available_length = TWITTER_LIMIT - hashtag_length

    # Truncate content if needed
    if len(content) > available_length:
        # Leave room for ellipsis
        content = content[:available_length - 3] + "..."

    # Combine content and hashtags
    if hashtag_str:
        return f"{content} {hashtag_str}"
    else:
        return content


def format_for_facebook(content: str, hashtags: List[str]) -> str:
    """
    Format content for Facebook (no strict character limit)

    Args:
        content: Base content
        hashtags: List of hashtags

    Returns:
        Facebook-formatted content
    """
    # Facebook doesn't have a strict character limit
    # But posts over 63,206 characters are truncated

    # Combine hashtags
    hashtag_str = " ".join(hashtags) if hashtags else ""

    # Facebook convention: hashtags at the end
    if hashtag_str:
        return f"{content}\n\n{hashtag_str}"
    else:
        return content


def format_for_instagram(content: str, hashtags: List[str]) -> str:
    """
    Format content for Instagram (2200 character limit, max 30 hashtags)

    Args:
        content: Base content
        hashtags: List of hashtags (will be limited to 30)

    Returns:
        Instagram-formatted content
    """
    # Instagram limits
    INSTAGRAM_LIMIT = 2200
    MAX_HASHTAGS = 30

    # Limit hashtags to 30
    limited_hashtags = hashtags[:MAX_HASHTAGS] if hashtags else []

    # Combine hashtags
    hashtag_str = " ".join(limited_hashtags) if limited_hashtags else ""

    # Calculate available space for content
    hashtag_length = len(hashtag_str) + (2 if hashtag_str else 0)  # +2 for newlines
    available_length = INSTAGRAM_LIMIT - hashtag_length

    # Truncate content if needed
    if len(content) > available_length:
        # Leave room for ellipsis
        content = content[:available_length - 3] + "..."

    # Instagram convention: hashtags at the end with line breaks
    if hashtag_str:
        return f"{content}\n\n{hashtag_str}"
    else:
        return content


def optimize_hashtags(hashtags: List[str], platform: str) -> List[str]:
    """
    Optimize hashtags for a specific platform

    Args:
        hashtags: List of hashtags
        platform: Target platform

    Returns:
        Optimized hashtag list
    """
    if platform == "instagram":
        # Instagram allows max 30 hashtags
        return hashtags[:30]
    elif platform == "twitter":
        # Twitter: fewer hashtags for better engagement (2-3 recommended)
        return hashtags[:3]
    elif platform == "facebook":
        # Facebook: 1-2 hashtags recommended
        return hashtags[:2]
    else:
        return hashtags


def truncate_content(content: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate content to a maximum length

    Args:
        content: Content to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating (default: "...")

    Returns:
        Truncated content
    """
    if len(content) <= max_length:
        return content

    # Truncate and add suffix
    truncate_at = max_length - len(suffix)
    return content[:truncate_at] + suffix


def extract_hashtags(content: str) -> tuple[str, List[str]]:
    """
    Extract hashtags from content

    Args:
        content: Content with hashtags

    Returns:
        Tuple of (content without hashtags, list of hashtags)
    """
    words = content.split()
    hashtags = [word for word in words if word.startswith("#")]
    content_words = [word for word in words if not word.startswith("#")]

    return " ".join(content_words), hashtags


def add_call_to_action(content: str, platform: str) -> str:
    """
    Add platform-specific call-to-action

    Args:
        content: Base content
        platform: Target platform

    Returns:
        Content with call-to-action
    """
    cta_map = {
        "twitter": "\n\n💬 What do you think? Reply below!",
        "facebook": "\n\n👍 Like and share if you agree!",
        "instagram": "\n\n💬 Comment below and tag a friend!",
    }

    cta = cta_map.get(platform, "")
    return f"{content}{cta}"


def format_with_emojis(content: str, platform: str) -> str:
    """
    Add platform-appropriate emojis

    Args:
        content: Base content
        platform: Target platform

    Returns:
        Content with emojis
    """
    # Instagram and Facebook users engage more with emojis
    if platform in ["instagram", "facebook"]:
        # Add emojis if not already present
        if not any(char in content for char in ["🎯", "💡", "🚀", "✨", "💪"]):
            return f"✨ {content}"

    return content
