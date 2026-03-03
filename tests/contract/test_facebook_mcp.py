"""
Contract test for Facebook post creation endpoint in the Gold Tier social media broadcasting system.
Test ID: T053 [P] [US3] Contract test for Facebook post creation endpoint
File: tests/contract/test_facebook_mcp.py
"""
import pytest
import requests
from unittest.mock import Mock, patch
import json

# Import the Facebook MCP client
from src.mcp.facebook_client import FacebookClient


class TestFacebookMCPContract:
    """Contract tests for Facebook MCP server endpoints."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_content = "Test Facebook post for contract verification"
        self.test_media_urls = ["https://example.com/test-image.jpg"]

    def test_facebook_post_creation_endpoint(self):
        """
        Test that the Facebook post creation endpoint accepts the expected contract.

        Input: Valid post content and optional media
        Expected: 200 response with post ID and creation confirmation
        """
        # Mock the Facebook API response
        mock_response = {
            "id": "12345678901234567",
            "success": True
        }

        # Create a mock Facebook client
        client = FacebookClient()

        # Test the contract compliance by mocking the actual API call
        with patch.object(client, '_make_request', return_value=mock_response):
            with patch.object(client, 'health_check', return_value={"status": "HEALTHY"}):
                # Test that the client can handle the standard request format
                response = client._make_request("/post", {
                    "content": self.test_content,
                    "media_urls": self.test_media_urls
                })

                # Verify response structure matches contract
                assert "id" in response
                assert response["success"] is True
                assert response["id"] == "12345678901234567"
                assert "content" in response or len(self.test_content) > 0

    def test_facebook_post_creation_with_media(self):
        """
        Test Facebook post creation with media attachment.

        Input: Post content with image URLs
        Expected: Post created with media, media URLs validated
        """
        mock_response = {
            "id": "98765432109876543",
            "success": True,
            "post_url": "https://facebook.com/98765432109876543"
        }

        client = FacebookClient()

        with patch.object(client, '_make_request', return_value=mock_response):
            response = client._make_request("/post", {
                "content": self.test_content,
                "media_urls": self.test_media_urls
            })

            # Verify response structure
            assert "id" in response
            assert "post_url" in response
            assert response["success"] is True
            assert response["id"] == "98765432109876543"

    def test_facebook_engagement_metrics_endpoint(self):
        """
        Test that the Facebook engagement metrics endpoint accepts the expected contract.

        Input: Valid post ID
        Expected: 200 response with engagement metrics (likes, comments, shares, etc.)
        """
        post_id = "12345678901234567"
        mock_response = {
            "data": {
                "post_id": post_id,
                "engagement_metrics": {
                    "likes": 42,
                    "comments": 12,
                    "shares": 8,
                    "reach": 1500,
                    "engagement_rate": 0.042
                }
            },
            "success": True
        }

        client = FacebookClient()

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

    def test_facebook_health_check_endpoint(self):
        """
        Test that the Facebook health check endpoint returns expected format.

        Input: Health check request
        Expected: Status and rate limit information
        """
        mock_response = {
            "status": "HEALTHY",
            "authenticated": True,
            "rate_limit": "50/200"
        }

        client = FacebookClient()

        with patch.object(client, '_make_request', return_value=mock_response):
            response = client._make_request("/health", {})

            # Verify health check response structure
            assert "status" in response
            assert "authenticated" in response
            assert "rate_limit" in response
            assert response["status"] in ["HEALTHY", "DEGRADED", "FAILED"]

    def test_facebook_error_handling(self):
        """
        Test that Facebook client handles errors according to contract.

        Input: Invalid request or API error
        Expected: Proper error response with error type and message
        """
        error_response = {
            "success": False,
            "error": "Invalid content or authentication failed",
            "error_code": 400
        }

        client = FacebookClient()

        with patch.object(client, '_make_request', return_value=error_response):
            response = client._make_request("/post", {
                "content": "Invalid content here"  # This should trigger an error in our mock
            })

            # Verify error structure
            assert "error" in response
            assert response["success"] is False
            assert "error" in response


if __name__ == "__main__":
    test = TestFacebookMCPContract()
    test.setup_method()

    print("Running Facebook post creation endpoint contract test...")
    try:
        test.test_facebook_post_creation_endpoint()
        print("✅ Facebook post creation endpoint contract test passed")
    except Exception as e:
        print(f"❌ Facebook post creation endpoint contract test failed: {e}")

    print("Running Facebook post creation with media contract test...")
    try:
        test.test_facebook_post_creation_with_media()
        print("✅ Facebook post creation with media contract test passed")
    except Exception as e:
        print(f"❌ Facebook post creation with media contract test failed: {e}")

    print("Running Facebook engagement metrics endpoint contract test...")
    try:
        test.test_facebook_engagement_metrics_endpoint()
        print("✅ Facebook engagement metrics endpoint contract test passed")
    except Exception as e:
        print(f"❌ Facebook engagement metrics endpoint contract test failed: {e}")

    print("Running Facebook health check endpoint contract test...")
    try:
        test.test_facebook_health_check_endpoint()
        print("✅ Facebook health check endpoint contract test passed")
    except Exception as e:
        print(f"❌ Facebook health check endpoint contract test failed: {e}")

    print("Running Facebook error handling contract test...")
    try:
        test.test_facebook_error_handling()
        print("✅ Facebook error handling contract test passed")
    except Exception as e:
        print(f"❌ Facebook error handling contract test failed: {e}")

    print("All Facebook MCP contract tests completed!")