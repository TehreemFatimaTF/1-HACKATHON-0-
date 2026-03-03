"""
Sentiment Analysis Utilities
Provides sentiment classification for text using TextBlob
"""

import logging
from typing import Tuple, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

# Lazy import TextBlob to avoid import errors if not installed
_textblob_available = False
try:
    from textblob import TextBlob
    _textblob_available = True
except ImportError:
    logger.warning("TextBlob not available. Sentiment analysis will use fallback method.")


class SentimentClass(Enum):
    """Sentiment classification"""
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


def analyze_sentiment(text: str) -> Tuple[SentimentClass, float]:
    """
    Analyze sentiment of text.

    Args:
        text: Text to analyze

    Returns:
        Tuple of (sentiment_class, polarity_score)
        - sentiment_class: POSITIVE, NEUTRAL, or NEGATIVE
        - polarity_score: Float from -1.0 (negative) to +1.0 (positive)
    """
    if not text or not text.strip():
        return SentimentClass.NEUTRAL, 0.0

    if _textblob_available:
        return _analyze_with_textblob(text)
    else:
        return _analyze_with_fallback(text)


def _analyze_with_textblob(text: str) -> Tuple[SentimentClass, float]:
    """Analyze sentiment using TextBlob"""
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        # Classify based on polarity
        if polarity > 0.1:
            sentiment_class = SentimentClass.POSITIVE
        elif polarity < -0.1:
            sentiment_class = SentimentClass.NEGATIVE
        else:
            sentiment_class = SentimentClass.NEUTRAL

        return sentiment_class, polarity

    except Exception as e:
        logger.error(f"TextBlob sentiment analysis failed: {e}")
        return _analyze_with_fallback(text)


def _analyze_with_fallback(text: str) -> Tuple[SentimentClass, float]:
    """
    Simple fallback sentiment analysis using keyword matching.
    This is a basic implementation for when TextBlob is not available.
    """
    text_lower = text.lower()

    # Positive keywords
    positive_keywords = [
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
        'love', 'happy', 'pleased', 'satisfied', 'perfect', 'awesome',
        'thank', 'thanks', 'appreciate', 'excited', 'brilliant'
    ]

    # Negative keywords
    negative_keywords = [
        'bad', 'terrible', 'awful', 'horrible', 'poor', 'worst',
        'hate', 'angry', 'frustrated', 'disappointed', 'unhappy',
        'problem', 'issue', 'error', 'fail', 'broken', 'wrong'
    ]

    # Count keyword matches
    positive_count = sum(1 for word in positive_keywords if word in text_lower)
    negative_count = sum(1 for word in negative_keywords if word in text_lower)

    # Calculate simple polarity score
    total_count = positive_count + negative_count
    if total_count == 0:
        polarity = 0.0
        sentiment_class = SentimentClass.NEUTRAL
    else:
        polarity = (positive_count - negative_count) / total_count

        if polarity > 0.2:
            sentiment_class = SentimentClass.POSITIVE
        elif polarity < -0.2:
            sentiment_class = SentimentClass.NEGATIVE
        else:
            sentiment_class = SentimentClass.NEUTRAL

    return sentiment_class, polarity


def analyze_batch(texts: list[str]) -> list[Tuple[SentimentClass, float]]:
    """
    Analyze sentiment for multiple texts.

    Args:
        texts: List of texts to analyze

    Returns:
        List of (sentiment_class, polarity_score) tuples
    """
    return [analyze_sentiment(text) for text in texts]


def get_sentiment_summary(texts: list[str]) -> Dict[str, Any]:
    """
    Get sentiment summary statistics for a list of texts.

    Args:
        texts: List of texts to analyze

    Returns:
        Dict with sentiment statistics
    """
    if not texts:
        return {
            "total_count": 0,
            "positive_count": 0,
            "neutral_count": 0,
            "negative_count": 0,
            "average_polarity": 0.0,
            "overall_sentiment": SentimentClass.NEUTRAL.value
        }

    results = analyze_batch(texts)

    positive_count = sum(1 for s, _ in results if s == SentimentClass.POSITIVE)
    neutral_count = sum(1 for s, _ in results if s == SentimentClass.NEUTRAL)
    negative_count = sum(1 for s, _ in results if s == SentimentClass.NEGATIVE)

    polarities = [p for _, p in results]
    average_polarity = sum(polarities) / len(polarities) if polarities else 0.0

    # Determine overall sentiment
    if average_polarity > 0.1:
        overall_sentiment = SentimentClass.POSITIVE
    elif average_polarity < -0.1:
        overall_sentiment = SentimentClass.NEGATIVE
    else:
        overall_sentiment = SentimentClass.NEUTRAL

    return {
        "total_count": len(texts),
        "positive_count": positive_count,
        "neutral_count": neutral_count,
        "negative_count": negative_count,
        "positive_percentage": (positive_count / len(texts)) * 100,
        "neutral_percentage": (neutral_count / len(texts)) * 100,
        "negative_percentage": (negative_count / len(texts)) * 100,
        "average_polarity": average_polarity,
        "overall_sentiment": overall_sentiment.value
    }
