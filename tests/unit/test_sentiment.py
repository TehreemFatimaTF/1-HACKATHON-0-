"""
Unit test for sentiment analysis classification in the Gold Tier system.
Test ID: T057 [P] [US3] Unit test for sentiment analysis classification
File: tests/unit/test_sentiment.py
"""
import pytest
from unittest.mock import Mock, patch
from src.utils.sentiment import (
    analyze_sentiment, analyze_batch, get_sentiment_summary, SentimentClass
)


class TestSentimentAnalysis:
    """Unit tests for sentiment analysis functionality."""

    def test_positive_sentiment_detection(self):
        """
        Test that positive sentiment is correctly detected.

        Input: Clearly positive text
        Expected: POSITIVE sentiment classification with positive polarity score
        """
        positive_texts = [
            "I love this product!",
            "The service was excellent and amazing",
            "Great experience, highly recommend",
            "Fantastic quality and fast delivery"
        ]

        for text in positive_texts:
            sentiment, polarity = analyze_sentiment(text)

            # For positive texts, we expect positive classification and score
            assert sentiment == SentimentClass.POSITIVE
            assert polarity > 0.0

    def test_negative_sentiment_detection(self):
        """
        Test that negative sentiment is correctly detected.

        Input: Clearly negative text
        Expected: NEGATIVE sentiment classification with negative polarity score
        """
        negative_texts = [
            "This product is terrible and awful",
            "I hate this service, very disappointed",
            "Poor quality, worst experience ever",
            "Broken item, complete waste of money"
        ]

        for text in negative_texts:
            sentiment, polarity = analyze_sentiment(text)

            # For negative texts, we expect negative classification and score
            assert sentiment == SentimentClass.NEGATIVE
            assert polarity < 0.0

    def test_neutral_sentiment_detection(self):
        """
        Test that neutral sentiment is correctly detected.

        Input: Neutral or mixed text
        Expected: NEUTRAL sentiment classification with near-zero polarity score
        """
        neutral_texts = [
            "The weather is okay today",
            "I went to the store and bought some milk",
            "The meeting is scheduled for 2 PM",
            "This is a factual statement about data"
        ]

        for text in neutral_texts:
            sentiment, polarity = analyze_sentiment(text)

            # For neutral texts, we expect neutral classification and score near zero
            assert sentiment == SentimentClass.NEUTRAL
            assert -0.1 <= polarity <= 0.1

    def test_empty_text_handling(self):
        """
        Test that empty or whitespace-only text is handled properly.

        Input: Empty string or whitespace
        Expected: NEUTRAL sentiment classification with zero polarity score
        """
        empty_texts = ["", "   ", "\n\t", "  \n  "]

        for text in empty_texts:
            sentiment, polarity = analyze_sentiment(text)

            # Empty text should be handled gracefully
            assert sentiment == SentimentClass.NEUTRAL
            assert polarity == 0.0

    def test_batch_sentiment_analysis(self):
        """
        Test that batch sentiment analysis works correctly.

        Input: List of texts with mixed sentiments
        Expected: List of (sentiment, polarity) tuples matching individual analysis
        """
        test_texts = [
            "I love this product!",  # Positive
            "This is terrible",      # Negative
            "The weather is okay"    # Neutral
        ]

        batch_results = analyze_batch(test_texts)

        # Verify batch results match individual analysis
        for i, text in enumerate(test_texts):
            individual_sentiment, individual_polarity = analyze_sentiment(text)
            batch_sentiment, batch_polarity = batch_results[i]

            assert individual_sentiment == batch_sentiment
            assert individual_polarity == batch_polarity

    def test_sentiment_summary_statistics(self):
        """
        Test that sentiment summary provides accurate statistics.

        Input: List of texts with mixed sentiments
        Expected: Accurate counts, percentages, and averages
        """
        test_texts = [
            "I love this product!",      # Positive
            "This is terrible",          # Negative
            "The weather is okay",       # Neutral
            "Amazing service!",          # Positive
            "Poor quality",              # Negative
            "I went to the store"        # Neutral
        ]

        summary = get_sentiment_summary(test_texts)

        # Verify basic structure
        assert "total_count" in summary
        assert "positive_count" in summary
        assert "neutral_count" in summary
        assert "negative_count" in summary
        assert "average_polarity" in summary
        assert "overall_sentiment" in summary

        # Verify counts
        assert summary["total_count"] == len(test_texts)
        assert summary["positive_count"] + summary["neutral_count"] + summary["negative_count"] == len(test_texts)

        # Verify percentages
        total_percentage = summary["positive_percentage"] + summary["neutral_percentage"] + summary["negative_percentage"]
        assert abs(total_percentage - 100.0) < 0.1  # Allow small floating point errors

        # For our specific test data: 2 positive, 2 neutral, 2 negative
        assert summary["positive_count"] == 2
        assert summary["neutral_count"] == 2
        assert summary["negative_count"] == 2

    def test_single_text_sentiment_summary(self):
        """
        Test sentiment summary with a single text.

        Input: List with one text
        Expected: Summary with correct statistics for single item
        """
        test_texts = ["I really enjoyed this experience"]

        summary = get_sentiment_summary(test_texts)

        # Should have one item in total
        assert summary["total_count"] == 1
        assert summary["positive_count"] >= 0
        assert summary["neutral_count"] >= 0
        assert summary["negative_count"] >= 0

        # All percentages should be either 0% or 100% for single item
        total_percentage = summary["positive_percentage"] + summary["neutral_percentage"] + summary["negative_percentage"]
        assert abs(total_percentage - 100.0) < 0.1

    def test_empty_list_sentiment_summary(self):
        """
        Test sentiment summary with an empty list.

        Input: Empty list
        Expected: Default summary with zero counts and neutral sentiment
        """
        summary = get_sentiment_summary([])

        # Verify default values for empty list
        assert summary["total_count"] == 0
        assert summary["positive_count"] == 0
        assert summary["neutral_count"] == 0
        assert summary["negative_count"] == 0
        assert summary["average_polarity"] == 0.0
        assert summary["overall_sentiment"] == SentimentClass.NEUTRAL.value

    def test_mixed_sentiment_edge_cases(self):
        """
        Test edge cases with mixed or complex sentiment.

        Input: Texts with mixed or subtle sentiment
        Expected: Reasonable sentiment classification
        """
        edge_case_texts = [
            "It's okay but could be better",  # Mixed, likely neutral
            "Not bad, not great either",      # Mixed, likely neutral
            "Surprisingly good quality",      # Positive with qualifier
            "Absolutely the worst experience"  # Strongly negative
        ]

        results = analyze_batch(edge_case_texts)

        # All should return valid sentiment and polarity
        for sentiment, polarity in results:
            assert sentiment in [SentimentClass.POSITIVE, SentimentClass.NEUTRAL, SentimentClass.NEGATIVE]
            assert -1.0 <= polarity <= 1.0

    def test_sentiment_summary_with_extreme_polarities(self):
        """
        Test sentiment summary with texts of extreme polarities.

        Input: List with strongly positive and negative texts
        Expected: Appropriate average polarity calculation
        """
        extreme_texts = [
            "Absolutely amazing and wonderful! Best ever!",      # Very positive
            "Terrible, horrible, worst experience ever!",       # Very negative
        ]

        summary = get_sentiment_summary(extreme_texts)

        # With equal positive and negative, average polarity should be near zero
        assert -0.5 <= summary["average_polarity"] <= 0.5

    def test_long_text_sentiment(self):
        """
        Test sentiment analysis on longer text passages.

        Input: Longer text with mixed sentiment indicators
        Expected: Overall sentiment based on dominant sentiment
        """
        long_text = """
        I really wanted to like this product but unfortunately it didn't meet my expectations.
        The quality was poor and it broke after a week. However, the customer service was
        responsive and helpful, which was a positive experience.
        """

        sentiment, polarity = analyze_sentiment(long_text)

        # For mixed content, the result should be based on dominant sentiment
        assert sentiment in [SentimentClass.POSITIVE, SentimentClass.NEUTRAL, SentimentClass.NEGATIVE]
        assert -1.0 <= polarity <= 1.0


if __name__ == "__main__":
    test = TestSentimentAnalysis()

    print("Running positive sentiment detection test...")
    try:
        test.test_positive_sentiment_detection()
        print("✅ Positive sentiment detection test passed")
    except Exception as e:
        print(f"❌ Positive sentiment detection test failed: {e}")

    print("Running negative sentiment detection test...")
    try:
        test.test_negative_sentiment_detection()
        print("✅ Negative sentiment detection test passed")
    except Exception as e:
        print(f"❌ Negative sentiment detection test failed: {e}")

    print("Running neutral sentiment detection test...")
    try:
        test.test_neutral_sentiment_detection()
        print("✅ Neutral sentiment detection test passed")
    except Exception as e:
        print(f"❌ Neutral sentiment detection test failed: {e}")

    print("Running empty text handling test...")
    try:
        test.test_empty_text_handling()
        print("✅ Empty text handling test passed")
    except Exception as e:
        print(f"❌ Empty text handling test failed: {e}")

    print("Running batch sentiment analysis test...")
    try:
        test.test_batch_sentiment_analysis()
        print("✅ Batch sentiment analysis test passed")
    except Exception as e:
        print(f"❌ Batch sentiment analysis test failed: {e}")

    print("Running sentiment summary statistics test...")
    try:
        test.test_sentiment_summary_statistics()
        print("✅ Sentiment summary statistics test passed")
    except Exception as e:
        print(f"❌ Sentiment summary statistics test failed: {e}")

    print("Running single text sentiment summary test...")
    try:
        test.test_single_text_sentiment_summary()
        print("✅ Single text sentiment summary test passed")
    except Exception as e:
        print(f"❌ Single text sentiment summary test failed: {e}")

    print("Running empty list sentiment summary test...")
    try:
        test.test_empty_list_sentiment_summary()
        print("✅ Empty list sentiment summary test passed")
    except Exception as e:
        print(f"❌ Empty list sentiment summary test failed: {e}")

    print("Running mixed sentiment edge cases test...")
    try:
        test.test_mixed_sentiment_edge_cases()
        print("✅ Mixed sentiment edge cases test passed")
    except Exception as e:
        print(f"❌ Mixed sentiment edge cases test failed: {e}")

    print("Running sentiment summary with extreme polarities test...")
    try:
        test.test_sentiment_summary_with_extreme_polarities()
        print("✅ Sentiment summary with extreme polarities test passed")
    except Exception as e:
        print(f"❌ Sentiment summary with extreme polarities test failed: {e}")

    print("Running long text sentiment test...")
    try:
        test.test_long_text_sentiment()
        print("✅ Long text sentiment test passed")
    except Exception as e:
        print(f"❌ Long text sentiment test failed: {e}")

    print("All sentiment analysis unit tests completed!")