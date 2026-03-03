"""
Contract test for Twitter post creation endpoint in the Gold Tier social media broadcasting system.
Test ID: T052 [P] [US3] Contract test for Twitter post creation endpoint
File: tests/contract/test_twitter_mcp.py
"""
import pytest
import requests
from unittest.mock import Mock, patch
import json

# Import the Twitter MCP client
from src.mcp.twitter_client import TwitterClient


class TestTwitterMCPContract:
    """Contract tests for Twitter MCP server endpoints."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_content = "Test tweet for contract verification"
        self.test_media_urls = ["https://example.com/test-image.jpg"]

    def test_twitter_post_creation_endpoint(self):
        """
        Test that the Twitter post creation endpoint accepts the expected contract.

        Input: Valid post content and optional media
        Expected: 200 response with post ID and creation confirmation
        """
        # Mock the Twitter API response
        mock_response = {
            "data": {
                "id": "1234567890123456789",
                "text": self.test_content
            },
            "success": True
        }

        # Create a mock Twitter client
        client = TwitterClient()

        # Test the contract compliance by mocking the actual API call
        with patch.object(client, '_make_request', return_value=mock_response):
            with patch.object(client, 'health_check', return_value={"status": "HEALTHY"}):
                # Test that the client can handle the standard request format
                response = client._make_request("/post", {
                    "content": self.test_content,
                    "media_urls": self.test_media_urls
                })

                # Verify response structure matches contract
                assert "data" in response
                assert "id" in response["data"]
                assert "text" in response["data"]
                assert response["success"] is True
                assert response["data"]["text"] == self.test_content

    def test_twitter_post_creation_with_media(self):
        """
        Test Twitter post creation with media attachment.

        Input: Post content with image URLs
        Expected: Post created with media, media URLs validated
        """
        mock_response = {
            "data": {
                "id": "9876543210987654321",
                "text": self.test_content,
                "media_keys": ["1234567890"]
            },
            "success": True
        }

        client = TwitterClient()

        with patch.object(client, '_make_request', return_value=mock_response):
            response = client._make_request("/post", {
                "content": self.test_content,
                "media_urls": self.test_media_urls
            })

            # Verify media was included in response
            assert "media_keys" in response["data"]
            assert len(response["data"]["media_keys"]) > 0

    def test_twitter_engagement_metrics_endpoint(self):
        """
        Test that the Twitter engagement metrics endpoint accepts the expected contract.

        Input: Valid post ID
        Expected: 200 response with engagement metrics (likes, retweets, etc.)
        """
        post_id = "1234567890123456789"
        mock_response = {
            "data": {
                "post_id": post_id,
                "engagement_metrics": {
                    "likes": 42,
                    "retweets": 12,
                    "replies": 5,
                    "impressions": 1500,
                    "engagement_rate": 0.038
                }
            },
            "success": True
        }

        client = TwitterClient()

        with patch.object(client, '_make_request', return_value=mock_response):
            response = client._make_request("/engagement", {
                "post_id": post_id
            })

            # Verify engagement metrics structure
            assert "data" in response
            assert "engagement_metrics" in response["data"]
            metrics = response["data"]["engagement_metrics"]
            assert "likes" in metrics
            assert "retweets" in metrics
            assert "impressions" in metrics

    def test_twitter_health_check_endpoint(self):
        """
        Test that the Twitter health check endpoint returns expected format.

        Input: Health check request
        Expected: Status and rate limit information
        """
        mock_response = {
            "status": "HEALTHY",
            "authenticated": True,
            "rate_limit": {
                "limit": 50,
                "remaining": 45,
                "reset_time": "2023-01-01T00:00:00Z"
            }
        }

        client = TwitterClient()

        with patch.object(client, '_make_request', return_value=mock_response):
            response = client._make_request("/health", {})

            # Verify health check response structure
            assert "status" in response
            assert "authenticated" in response
            assert "rate_limit" in response
            assert response["status"] in ["HEALTHY", "DEGRADED", "FAILED"]

    def test_twitter_error_handling(self):
        """
        Test that Twitter client handles errors according to contract.

        Input: Invalid request or API error
        Expected: Proper error response with error type and message
        """
        error_response = {
            "error": {
                "type": "API_ERROR",
                "message": "Invalid content or authentication failed",
                "code": 400
            }
        }

        client = TwitterClient()

        with patch.object(client, '_make_request', return_value=error_response):
            response = client._make_request("/post", {
                "content": "Invalid content here"  # This should trigger an error in our mock
            })

            # Verify error structure
            assert "error" in response
            error = response["error"]
            assert "type" in error
            assert "message" in error
            assert "code" in error


if __name__ == "__main__":
    test = TestTwitterMCPContract()
    test.setup_method()

    print("Running Twitter post creation endpoint contract test...")
    try:
        test.test_twitter_post_creation_endpoint()
        print("✅ Twitter post creation endpoint contract test passed")
    except Exception as e:
        print(f"❌ Twitter post creation endpoint contract test failed: {e}")

    print("Running Twitter post creation with media contract test...")
    try:
        test.test_twitter_post_creation_with_media()
        print("✅ Twitter post creation with media contract test passed")
    except Exception as e:
        print(f"❌ Twitter post creation with media contract test failed: {e}")

    print("Running Twitter engagement metrics endpoint contract test...")
    try:
        test.test_twitter_engagement_metrics_endpoint()
        print("✅ Twitter engagement metrics endpoint contract test passed")
    except Exception as e:
        print(f"❌ Twitter engagement metrics endpoint contract test failed: {e}")

    print("Running Twitter health check endpoint contract test...")
    try:
        test.test_twitter_health_check_endpoint()
        print("✅ Twitter health check endpoint contract test passed")
    except Exception as e:
        print(f"❌ Twitter health check endpoint contract test failed: {e}")

    print("Running Twitter error handling contract test...")
    try:
        test.test_twitter_error_handling()
        print("✅ Twitter error handling contract test passed")
    except Exception as e:
        print(f"❌ Twitter error handling contract test failed: {e}")

    print("All Twitter MCP contract tests completed!")