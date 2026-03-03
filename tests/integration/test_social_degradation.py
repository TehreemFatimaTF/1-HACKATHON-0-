"""
Integration test for graceful degradation in social media broadcasting when one platform fails.
Test ID: T056 [P] [US3] Integration test for graceful degradation (Twitter failure)
File: tests/integration/test_social_degradation.py
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Import the necessary modules from the Gold Tier implementation
from src.skills.broadcast_marketing import broadcast_marketing_skill
from src.mcp.twitter_client import TwitterClient
from src.mcp.facebook_client import FacebookClient
from src.mcp.instagram_client import InstagramClient
from src.audit.gold_logger import GoldAuditLogger


class TestSocialDegradationIntegration:
    """Integration tests for graceful degradation in social media broadcasting."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_content = "Check out our latest product update! #innovation #tech"
        self.test_image_url = "https://example.com/product-image.jpg"
        self.test_hashtags = ["#innovation", "#tech", "#product"]

    def test_twitter_failure_graceful_degradation(self):
        """
        Test that system continues to work when Twitter API fails.

        Input: Content sent to all platforms, Twitter API unavailable
        Expected: Facebook and Instagram posts succeed, Twitter fails gracefully,
                 overall operation marked as partial success
        """
        # Mock responses - Twitter fails, Facebook and Instagram succeed
        twitter_response = {
            "success": False,
            "error": "Twitter API unavailable"
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

        with patch.object(TwitterClient, 'call', return_value=twitter_response) as mock_twitter, \
             patch.object(FacebookClient, 'call', return_value=facebook_response) as mock_facebook, \
             patch.object(InstagramClient, 'call', return_value=instagram_response) as mock_instagram, \
             patch.object(GoldAuditLogger, 'log_action') as mock_audit:

            result = broadcast_marketing_skill({
                "content": self.test_content,
                "platforms": ["twitter", "facebook", "instagram"]
            })

            # Verify all platforms were attempted
            assert mock_twitter.called
            assert mock_facebook.called
            assert mock_instagram.called

            # Verify the result shows partial success
            assert "success" in result
            # Should be considered successful if at least one platform succeeded
            assert result["success"] is True
            assert result["twitter"]["success"] is False
            assert result["facebook"]["success"] is True
            assert result["instagram"]["success"] is True

            # Verify audit logging for the degradation
            assert mock_audit.call_count >= 3  # At least one call per platform attempted

    def test_facebook_failure_graceful_degradation(self):
        """
        Test that system continues to work when Facebook API fails.

        Input: Content sent to all platforms, Facebook API unavailable
        Expected: Twitter and Instagram posts succeed, Facebook fails gracefully
        """
        # Mock responses - Facebook fails, Twitter and Instagram succeed
        twitter_response = {
            "success": True,
            "tweet_id": "1234567890123456789",
            "tweet_url": "https://twitter.com/user/status/1234567890123456789"
        }

        facebook_response = {
            "success": False,
            "error": "Facebook API rate limit exceeded"
        }

        instagram_response = {
            "success": True,
            "post_id": "ABC123XYZ",
            "post_url": "https://instagram.com/p/ABC123XYZ"
        }

        with patch.object(TwitterClient, 'call', return_value=twitter_response) as mock_twitter, \
             patch.object(FacebookClient, 'call', return_value=facebook_response) as mock_facebook, \
             patch.object(InstagramClient, 'call', return_value=instagram_response) as mock_instagram:

            result = broadcast_marketing_skill({
                "content": self.test_content,
                "platforms": ["twitter", "facebook", "instagram"]
            })

            # Verify all platforms were attempted
            assert mock_twitter.called
            assert mock_facebook.called
            assert mock_instagram.called

            # Verify the result shows partial success
            assert result["success"] is True  # At least 2 out of 3 succeeded
            assert result["twitter"]["success"] is True
            assert result["facebook"]["success"] is False
            assert result["instagram"]["success"] is True

    def test_instagram_failure_graceful_degradation(self):
        """
        Test that system continues to work when Instagram API fails.

        Input: Content sent to all platforms, Instagram API unavailable
        Expected: Twitter and Facebook posts succeed, Instagram fails gracefully
        """
        # Mock responses - Instagram fails, Twitter and Facebook succeed
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
            "success": False,
            "error": "Instagram media upload failed"
        }

        with patch.object(TwitterClient, 'call', return_value=twitter_response) as mock_twitter, \
             patch.object(FacebookClient, 'call', return_value=facebook_response) as mock_facebook, \
             patch.object(InstagramClient, 'call', return_value=instagram_response) as mock_instagram:

            result = broadcast_marketing_skill({
                "content": self.test_content,
                "platforms": ["twitter", "facebook", "instagram"]
            })

            # Verify all platforms were attempted
            assert mock_twitter.called
            assert mock_facebook.called
            assert mock_instagram.called

            # Verify the result shows partial success
            assert result["success"] is True  # At least 2 out of 3 succeeded
            assert result["twitter"]["success"] is True
            assert result["facebook"]["success"] is True
            assert result["instagram"]["success"] is False

    def test_all_platforms_failure_graceful_degradation(self):
        """
        Test behavior when all platforms fail.

        Input: Content sent to all platforms, all APIs unavailable
        Expected: All platforms fail, but operation handled gracefully without crashing
        """
        # Mock responses - all platforms fail
        failure_response = {
            "success": False,
            "error": "API unavailable"
        }

        with patch.object(TwitterClient, 'call', return_value=failure_response) as mock_twitter, \
             patch.object(FacebookClient, 'call', return_value=failure_response) as mock_facebook, \
             patch.object(InstagramClient, 'call', return_value=failure_response) as mock_instagram:

            result = broadcast_marketing_skill({
                "content": self.test_content,
                "platforms": ["twitter", "facebook", "instagram"]
            })

            # Verify all platforms were attempted
            assert mock_twitter.called
            assert mock_facebook.called
            assert mock_instagram.called

            # Verify all platforms failed
            assert result["success"] is False  # All failed
            assert result["twitter"]["success"] is False
            assert result["facebook"]["success"] is False
            assert result["instagram"]["success"] is False

    def test_single_platform_degradation(self):
        """
        Test that failure of a single selected platform doesn't affect others.

        Input: Content sent to only Twitter, which fails
        Expected: Operation marked as failed since only one platform was requested
        """
        twitter_failure_response = {
            "success": False,
            "error": "Twitter API temporarily down"
        }

        with patch.object(TwitterClient, 'call', return_value=twitter_failure_response) as mock_twitter:

            result = broadcast_marketing_skill({
                "content": self.test_content,
                "platforms": ["twitter"]
            })

            # Verify Twitter was attempted
            assert mock_twitter.called

            # Since only one platform was requested and it failed, overall should fail
            assert result["success"] is False
            assert result["twitter"]["success"] is False

    def test_degradation_with_audit_logging(self):
        """
        Test that degradation events are properly logged in the audit trail.

        Input: Content sent to all platforms with Twitter failure
        Expected: All operations logged with appropriate success/failure markers
        """
        twitter_response = {
            "success": False,
            "error": "Twitter API unavailable"
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
             patch.object(GoldAuditLogger, 'log_action') as mock_audit:

            result = broadcast_marketing_skill({
                "content": self.test_content,
                "platforms": ["twitter", "facebook", "instagram"]
            })

            # Verify that audit logging was called for all operations
            # At least one call for each platform attempt plus summary
            assert mock_audit.call_count >= 3

            # Verify the operation was handled gracefully despite Twitter failure
            assert result["success"] is True  # Facebook and Instagram succeeded


if __name__ == "__main__":
    test = TestSocialDegradationIntegration()
    test.setup_method()

    print("Running Twitter failure graceful degradation test...")
    try:
        test.test_twitter_failure_graceful_degradation()
        print("✅ Twitter failure graceful degradation test passed")
    except Exception as e:
        print(f"❌ Twitter failure graceful degradation test failed: {e}")

    print("Running Facebook failure graceful degradation test...")
    try:
        test.test_facebook_failure_graceful_degradation()
        print("✅ Facebook failure graceful degradation test passed")
    except Exception as e:
        print(f"❌ Facebook failure graceful degradation test failed: {e}")

    print("Running Instagram failure graceful degradation test...")
    try:
        test.test_instagram_failure_graceful_degradation()
        print("✅ Instagram failure graceful degradation test passed")
    except Exception as e:
        print(f"❌ Instagram failure graceful degradation test failed: {e}")

    print("Running all platforms failure graceful degradation test...")
    try:
        test.test_all_platforms_failure_graceful_degradation()
        print("✅ All platforms failure graceful degradation test passed")
    except Exception as e:
        print(f"❌ All platforms failure graceful degradation test failed: {e}")

    print("Running single platform degradation test...")
    try:
        test.test_single_platform_degradation()
        print("✅ Single platform degradation test passed")
    except Exception as e:
        print(f"❌ Single platform degradation test failed: {e}")

    print("Running degradation with audit logging test...")
    try:
        test.test_degradation_with_audit_logging()
        print("✅ Degradation with audit logging test passed")
    except Exception as e:
        print(f"❌ Degradation with audit logging test failed: {e}")

    print("All social degradation integration tests completed!")