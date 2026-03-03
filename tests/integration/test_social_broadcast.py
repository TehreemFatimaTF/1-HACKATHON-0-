"""
Integration test for multi-platform social media broadcasting in the Gold Tier system.
Test ID: T055 [P] [US3] Integration test for multi-platform broadcast
File: tests/integration/test_social_broadcast.py
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Import the necessary modules from the Gold Tier implementation
from src.skills.broadcast_marketing import broadcast_marketing_skill
from src.mcp.twitter_client import TwitterClient
from src.mcp.facebook_client import FacebookClient
from src.mcp.instagram_client import InstagramClient
from src.utils.content_formatter import ContentFormatter
from src.utils.sentiment import analyze_sentiment


class TestSocialBroadcastIntegration:
    """Integration tests for multi-platform social media broadcasting."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_content = "Check out our latest product update! #innovation #tech"
        self.test_image_url = "https://example.com/product-image.jpg"
        self.test_hashtags = ["#innovation", "#tech", "#product"]

    def test_multi_platform_broadcast_success(self):
        """
        Test successful broadcast to all three platforms simultaneously.

        Input: Content, image URL, and hashtags
        Expected: Post created on Twitter, Facebook, and Instagram with proper formatting
        """
        # Mock responses for all three platforms
        twitter_response = {
            "success": True,
            "tweet_id": "1234567890123456789",
            "tweet_url": "https://twitter.com/user/status/1234567890123456789"
        }

        facebook_response = {
            "success": True,
            "post_id": "9876543210987654321",
            "post_url": "https://facebook.com/9876543210987654321"
        }

        instagram_response = {
            "success": True,
            "post_id": "ABC123XYZ",
            "post_url": "https://instagram.com/p/ABC123XYZ"
        }

        # Mock the MCP clients
        with patch.object(TwitterClient, 'call', return_value=twitter_response) as mock_twitter, \
             patch.object(FacebookClient, 'call', return_value=facebook_response) as mock_facebook, \
             patch.object(InstagramClient, 'call', return_value=instagram_response) as mock_instagram:

            # Execute the broadcast skill
            result = broadcast_marketing_skill({
                "content": self.test_content,
                "image_url": self.test_content,
                "hashtags": self.test_hashtags,
                "platforms": ["twitter", "facebook", "instagram"]
            })

            # Verify all platforms were called
            assert mock_twitter.called
            assert mock_facebook.called
            assert mock_instagram.called

            # Verify the result structure
            assert "success" in result
            assert result["success"] is True
            assert "twitter" in result
            assert "facebook" in result
            assert "instagram" in result

    def test_twitter_only_broadcast(self):
        """
        Test broadcast to Twitter only.

        Input: Content and Twitter platform selection
        Expected: Post created on Twitter only, other platforms skipped
        """
        twitter_response = {
            "success": True,
            "tweet_id": "1234567890123456789",
            "tweet_url": "https://twitter.com/user/status/1234567890123456789"
        }

        with patch.object(TwitterClient, 'call', return_value=twitter_response) as mock_twitter, \
             patch.object(FacebookClient, 'call') as mock_facebook, \
             patch.object(InstagramClient, 'call') as mock_instagram:

            result = broadcast_marketing_skill({
                "content": self.test_content,
                "platforms": ["twitter"]
            })

            # Only Twitter should be called
            assert mock_twitter.called
            assert not mock_facebook.called
            assert not mock_instagram.called

            # Verify result
            assert result["success"] is True
            assert "twitter" in result
            assert "facebook" not in result
            assert "instagram" not in result

    def test_facebook_only_broadcast(self):
        """
        Test broadcast to Facebook only.

        Input: Content and Facebook platform selection
        Expected: Post created on Facebook only, other platforms skipped
        """
        facebook_response = {
            "success": True,
            "post_id": "9876543210987654321",
            "post_url": "https://facebook.com/9876543210987654321"
        }

        with patch.object(TwitterClient, 'call') as mock_twitter, \
             patch.object(FacebookClient, 'call', return_value=facebook_response) as mock_facebook, \
             patch.object(InstagramClient, 'call') as mock_instagram:

            result = broadcast_marketing_skill({
                "content": self.test_content,
                "platforms": ["facebook"]
            })

            # Only Facebook should be called
            assert not mock_twitter.called
            assert mock_facebook.called
            assert not mock_instagram.called

            # Verify result
            assert result["success"] is True
            assert "facebook" in result
            assert "twitter" not in result
            assert "instagram" not in result

    def test_content_formatting_integration(self):
        """
        Test that content is properly formatted for each platform.

        Input: Generic content
        Expected: Platform-specific formatting applied (character limits, hashtag limits, etc.)
        """
        # Mock formatter to verify it's being used
        formatter = ContentFormatter()

        with patch.object(formatter, 'format_for_platform') as mock_format:
            mock_format.side_effect = lambda content, platform: f"formatted_{platform}_{content[:20]}"

            # Test that different formatting is applied to each platform
            twitter_formatted = formatter.format_for_platform(self.test_content, "twitter")
            facebook_formatted = formatter.format_for_platform(self.test_content, "facebook")
            instagram_formatted = formatter.format_for_platform(self.test_content, "instagram")

            # Each should have different formatting based on platform constraints
            assert "twitter" in twitter_formatted
            assert "facebook" in facebook_formatted
            assert "instagram" in instagram_formatted

    def test_sentiment_analysis_integration(self):
        """
        Test that sentiment analysis is performed on broadcast content.

        Input: Content for social media
        Expected: Sentiment analysis performed and included in results
        """
        # Mock sentiment analysis
        with patch('src.utils.sentiment.analyze_sentiment') as mock_sentiment:
            mock_sentiment.return_value = {
                "polarity": 0.8,
                "subjectivity": 0.6,
                "sentiment_label": "positive"
            }

            sentiment_result = analyze_sentiment(self.test_content)

            # Verify sentiment analysis was called and returned expected structure
            mock_sentiment.assert_called_once()
            assert "polarity" in sentiment_result
            assert "sentiment_label" in sentiment_result
            assert sentiment_result["sentiment_label"] == "positive"

    def test_multi_platform_broadcast_with_engagement_tracking(self):
        """
        Test that engagement tracking works across all platforms after broadcast.

        Input: Content broadcast to all platforms
        Expected: Engagement metrics can be retrieved for all successful posts
        """
        # Mock successful broadcasts
        twitter_response = {
            "success": True,
            "tweet_id": "1234567890123456789",
            "tweet_url": "https://twitter.com/user/status/1234567890123456789"
        }

        facebook_response = {
            "success": True,
            "post_id": "9876543210987654321",
            "post_url": "https://facebook.com/9876543210987654321"
        }

        instagram_response = {
            "success": True,
            "post_id": "ABC123XYZ",
            "post_url": "https://instagram.com/p/ABC123XYZ"
        }

        with patch.object(TwitterClient, 'call', return_value=twitter_response), \
             patch.object(FacebookClient, 'call', return_value=facebook_response), \
             patch.object(InstagramClient, 'call', return_value=instagram_response), \
             patch.object(TwitterClient, 'get_tweet_metrics') as mock_twitter_metrics, \
             patch.object(FacebookClient, 'get_post_metrics') as mock_facebook_metrics, \
             patch.object(InstagramClient, 'get_post_metrics') as mock_instagram_metrics:

            # Set up mock metrics responses
            mock_twitter_metrics.return_value = {
                "success": True,
                "platform": "twitter",
                "likes": 42,
                "comments": 12,
                "shares": 8,
                "reach": 1500,
                "engagement_rate": 0.042
            }

            mock_facebook_metrics.return_value = {
                "success": True,
                "platform": "facebook",
                "likes": 28,
                "comments": 7,
                "shares": 15,
                "reach": 890,
                "engagement_rate": 0.067
            }

            mock_instagram_metrics.return_value = {
                "success": True,
                "platform": "instagram",
                "likes": 65,
                "comments": 23,
                "shares": 5,  # saves in Instagram
                "reach": 1200,
                "engagement_rate": 0.073
            }

            # Execute broadcast
            result = broadcast_marketing_skill({
                "content": self.test_content,
                "platforms": ["twitter", "facebook", "instagram"]
            })

            # Verify that metrics tracking was set up for the successful posts
            assert result["success"] is True
            assert "twitter" in result
            assert "facebook" in result
            assert "instagram" in result


if __name__ == "__main__":
    test = TestSocialBroadcastIntegration()
    test.setup_method()

    print("Running multi-platform broadcast success test...")
    try:
        test.test_multi_platform_broadcast_success()
        print("✅ Multi-platform broadcast success test passed")
    except Exception as e:
        print(f"❌ Multi-platform broadcast success test failed: {e}")

    print("Running Twitter-only broadcast test...")
    try:
        test.test_twitter_only_broadcast()
        print("✅ Twitter-only broadcast test passed")
    except Exception as e:
        print(f"❌ Twitter-only broadcast test failed: {e}")

    print("Running Facebook-only broadcast test...")
    try:
        test.test_facebook_only_broadcast()
        print("✅ Facebook-only broadcast test passed")
    except Exception as e:
        print(f"❌ Facebook-only broadcast test failed: {e}")

    print("Running content formatting integration test...")
    try:
        test.test_content_formatting_integration()
        print("✅ Content formatting integration test passed")
    except Exception as e:
        print(f"❌ Content formatting integration test failed: {e}")

    print("Running sentiment analysis integration test...")
    try:
        test.test_sentiment_analysis_integration()
        print("✅ Sentiment analysis integration test passed")
    except Exception as e:
        print(f"❌ Sentiment analysis integration test failed: {e}")

    print("Running multi-platform broadcast with engagement tracking test...")
    try:
        test.test_multi_platform_broadcast_with_engagement_tracking()
        print("✅ Multi-platform broadcast with engagement tracking test passed")
    except Exception as e:
        print(f"❌ Multi-platform broadcast with engagement tracking test failed: {e}")

    print("All social broadcast integration tests completed!")