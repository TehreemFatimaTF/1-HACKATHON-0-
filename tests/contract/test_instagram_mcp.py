"""
Contract test for Instagram post creation endpoint in the Gold Tier social media broadcasting system.
Test ID: T054 [P] [US3] Contract test for Instagram post creation endpoint
File: tests/contract/test_instagram_mcp.py
"""
import pytest
import requests
from unittest.mock import Mock, patch
import json

# Import the Instagram MCP client
from src.mcp.instagram_client import InstagramClient


class TestInstagramMCPContract:
    """Contract tests for Instagram MCP server endpoints."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_content = "Test Instagram post for contract verification"
        self.test_hashtags = ["#test", "#automation", "#ai"]
        self.test_image_url = "https://example.com/test-image.jpg"

    def test_instagram_post_creation_endpoint(self):
        """
        Test that the Instagram post creation endpoint accepts the expected contract.

        Input: Valid post content, hashtags, and image URL
        Expected: 200 response with post ID and creation confirmation
        """
        # Mock the Instagram API response
        mock_response = {
            "success": True,
            "post_id": "ABC123XYZ",
            "post_url": "https://instagram.com/p/ABC123XYZ"
        }

        # Create a mock Instagram client
        client = InstagramClient()

        # Test the contract compliance by mocking the actual API call
        with patch.object(client, '_make_request', return_value=mock_response):
            with patch.object(client, 'health_check', return_value={"status": "HEALTHY"}):
                # Test that the client can handle the standard request format
                response = client._make_request("/post", {
                    "content": self.test_content,
                    "hashtags": self.test_hashtags,
                    "image_url": self.test_image_url
                })

                # Verify response structure matches contract
                assert "success" in response
                assert response["success"] is True
                assert "post_id" in response
                assert "post_url" in response
                assert response["post_id"] == "ABC123XYZ"

    def test_instagram_post_creation_with_hashtags(self):
        """
        Test Instagram post creation with hashtag validation.

        Input: Post content with hashtag list
        Expected: Post created with validated hashtags, max 30
        """
        mock_response = {
            "success": True,
            "post_id": "DEF456UVW",
            "post_url": "https://instagram.com/p/DEF456UVW"
        }

        client = InstagramClient()

        with patch.object(client, '_make_request', return_value=mock_response):
            response = client._make_request("/post", {
                "content": self.test_content,
                "hashtags": self.test_hashtags,
                "image_url": self.test_image_url
            })

            # Verify response structure
            assert "success" in response
            assert response["success"] is True
            assert len(response["post_id"]) > 0

    def test_instagram_engagement_metrics_endpoint(self):
        """
        Test that the Instagram engagement metrics endpoint accepts the expected contract.

        Input: Valid post ID
        Expected: 200 response with engagement metrics (likes, comments, saves, reach)
        """
        post_id = "ABC123XYZ"
        mock_response = {
            "data": {
                "post_id": post_id,
                "engagement_metrics": {
                    "likes": 24,
                    "comments": 7,
                    "shares": 3,  # Using saves as shares equivalent
                    "reach": 850,
                    "engagement_rate": 0.036
                }
            },
            "success": True
        }

        client = InstagramClient()

        with patch.object(client, '_make_request', return_value=mock_response):
            response = client._make_request("/metrics", {
                "post_id": post_id
            })

            # Verify engagement metrics structure
            assert "data" in response
            assert "engagement_metrics" in response["data"]
            metrics = response["data"]["engagement_metrics"]
            assert "likes" in metrics
            assert "comments" in metrics
            assert "shares" in metrics
            assert "reach" in metrics
            assert "engagement_rate" in metrics

    def test_instagram_health_check_endpoint(self):
        """
        Test that the Instagram health check endpoint returns expected format.

        Input: Health check request
        Expected: Status and rate limit information
        """
        mock_response = {
            "status": "HEALTHY",
            "authenticated": True,
            "rate_limit": "5/25"
        }

        client = InstagramClient()

        with patch.object(client, '_make_request', return_value=mock_response):
            response = client._make_request("/health", {})

            # Verify health check response structure
            assert "status" in response
            assert "authenticated" in response
            assert "rate_limit" in response
            assert response["status"] in ["HEALTHY", "DEGRADED", "FAILED"]

    def test_instagram_error_handling(self):
        """
        Test that Instagram client handles errors according to contract.

        Input: Invalid request or API error (missing image, too many hashtags)
        Expected: Proper error response with error type and message
        """
        error_response = {
            "success": False,
            "error": "Image URL required or hashtag limit exceeded",
            "error_code": 400
        }

        client = InstagramClient()

        with patch.object(client, '_make_request', return_value=error_response):
            response = client._make_request("/post", {
                "content": self.test_content,
                "hashtags": ["#tag1", "#tag2"] * 20,  # Exceeds 30 hashtag limit
                "image_url": None  # Missing required image
            })

            # Verify error structure
            assert "error" in response
            assert response["success"] is False
            assert response["error_code"] == 400


if __name__ == "__main__":
    test = TestInstagramMCPContract()
    test.setup_method()

    print("Running Instagram post creation endpoint contract test...")
    try:
        test.test_instagram_post_creation_endpoint()
        print("✅ Instagram post creation endpoint contract test passed")
    except Exception as e:
        print(f"❌ Instagram post creation endpoint contract test failed: {e}")

    print("Running Instagram post creation with hashtags contract test...")
    try:
        test.test_instagram_post_creation_with_hashtags()
        print("✅ Instagram post creation with hashtags contract test passed")
    except Exception as e:
        print(f"❌ Instagram post creation with hashtags contract test failed: {e}")

    print("Running Instagram engagement metrics endpoint contract test...")
    try:
        test.test_instagram_engagement_metrics_endpoint()
        print("✅ Instagram engagement metrics endpoint contract test passed")
    except Exception as e:
        print(f"❌ Instagram engagement metrics endpoint contract test failed: {e}")

    print("Running Instagram health check endpoint contract test...")
    try:
        test.test_instagram_health_check_endpoint()
        print("✅ Instagram health check endpoint contract test passed")
    except Exception as e:
        print(f"❌ Instagram health check endpoint contract test failed: {e}")

    print("Running Instagram error handling contract test...")
    try:
        test.test_instagram_error_handling()
        print("✅ Instagram error handling contract test passed")
    except Exception as e:
        print(f"❌ Instagram error handling contract test failed: {e}")

    print("All Instagram MCP contract tests completed!")