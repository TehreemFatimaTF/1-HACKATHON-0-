"""
Unit test for platform-specific content formatting in the Gold Tier system.
Test ID: T058 [P] [US3] Unit test for platform-specific content formatting
File: tests/unit/test_content_formatter.py
"""
import pytest
from src.utils.content_formatter import (
    format_for_platform,
    format_for_twitter,
    format_for_facebook,
    format_for_instagram,
    optimize_hashtags,
    truncate_content,
    extract_hashtags,
    add_call_to_action,
    format_with_emojis
)


class TestContentFormatter:
    """Unit tests for content formatting functionality."""

    def test_twitter_formatting_character_limit(self):
        """
        Test that Twitter content is properly truncated to 280 characters.

        Input: Content longer than 280 characters
        Expected: Content truncated to 280 characters with ellipsis
        """
        long_content = "x" * 350  # Content longer than Twitter's limit
        hashtags = ["#test", "#twitter"]

        # Format for Twitter
        formatted = format_for_platform(long_content, "twitter", hashtags)

        # Should be within Twitter's character limit
        assert len(formatted) <= 280
        assert "..." in formatted

    def test_twitter_hashtag_limiting(self):
        """
        Test that Twitter formatting respects hashtag recommendations.

        Input: Content with many hashtags
        Expected: Only first few hashtags included (optimized for Twitter)
        """
        content = "This is a test tweet with many hashtags"
        many_hashtags = [f"#test{i}" for i in range(10)]  # 10 hashtags

        formatted = format_for_twitter(content, many_hashtags)

        # Should limit hashtags for Twitter (3 max)
        hashtag_count = formatted.count("#")
        assert hashtag_count <= 3  # Twitter optimization should limit hashtags

    def test_facebook_formatting_no_limit(self):
        """
        Test that Facebook formatting doesn't truncate content unnecessarily.

        Input: Content with hashtags
        Expected: Content preserved with hashtags at end
        """
        content = "This is a test post for Facebook " + "x" * 200
        hashtags = ["#facebook", "#socialmedia"]

        formatted = format_for_platform(content, "facebook", hashtags)

        # Facebook doesn't have strict character limit, should preserve content
        assert content.replace(" ", "") in formatted.replace(" ", "")  # Remove spaces for comparison
        assert "#facebook" in formatted
        assert "#socialmedia" in formatted

    def test_instagram_formatting_character_limit(self):
        """
        Test that Instagram content is properly truncated to 2200 characters.

        Input: Content longer than 2200 characters
        Expected: Content truncated to 2200 characters with ellipsis
        """
        long_content = "x" * 2500  # Content longer than Instagram's limit
        hashtags = ["#instagram", "#photo", "#test"] * 15  # 45 hashtags

        formatted = format_for_platform(long_content, "instagram", hashtags)

        # Should be within Instagram's character limit
        assert len(formatted) <= 2200
        assert "..." in formatted if len(long_content) > 2200 else len(formatted) == len(long_content)

    def test_instagram_hashtag_limiting(self):
        """
        Test that Instagram formatting limits hashtags to 30.

        Input: Content with more than 30 hashtags
        Expected: Only first 30 hashtags included
        """
        content = "This is a test Instagram post"
        many_hashtags = [f"#hashtag{i}" for i in range(40)]  # 40 hashtags

        formatted = format_for_instagram(content, many_hashtags)

        # Should limit to 30 hashtags for Instagram
        hashtag_count = formatted.count("#")
        assert hashtag_count <= 30

    def test_format_for_unknown_platform(self):
        """
        Test that formatting for unknown platform returns original content.

        Input: Content for unknown platform
        Expected: Original content returned unchanged
        """
        content = "This is a test content"
        hashtags = ["#test"]

        formatted = format_for_platform(content, "unknown_platform", hashtags)

        # Should return original content for unknown platform
        assert formatted.startswith(content)

    def test_optimize_hashtags_twitter(self):
        """
        Test hashtag optimization for Twitter.

        Input: List of hashtags for Twitter
        Expected: Hashtags limited to 3
        """
        hashtags = [f"#tag{i}" for i in range(10)]
        optimized = optimize_hashtags(hashtags, "twitter")

        assert len(optimized) == 3

    def test_optimize_hashtags_instagram(self):
        """
        Test hashtag optimization for Instagram.

        Input: List of hashtags for Instagram
        Expected: Hashtags limited to 30
        """
        hashtags = [f"#tag{i}" for i in range(50)]
        optimized = optimize_hashtags(hashtags, "instagram")

        assert len(optimized) == 30

    def test_optimize_hashtags_facebook(self):
        """
        Test hashtag optimization for Facebook.

        Input: List of hashtags for Facebook
        Expected: Hashtags limited to 2
        """
        hashtags = [f"#tag{i}" for i in range(10)]
        optimized = optimize_hashtags(hashtags, "facebook")

        assert len(optimized) == 2

    def test_truncate_content_function(self):
        """
        Test the basic truncate_content utility function.

        Input: Content and max length
        Expected: Content truncated to max length with suffix
        """
        content = "This is a long content that needs to be truncated"
        truncated = truncate_content(content, 20, "...")

        assert len(truncated) == 20
        # Ensure it ends with the suffix
        assert truncated.endswith("...")

    def test_extract_hashtags(self):
        """
        Test hashtag extraction from content.

        Input: Content containing hashtags
        Expected: Content and hashtags separated
        """
        content_with_hashtags = "This is a #test post with #hashtags and #more"
        extracted_content, extracted_hashtags = extract_hashtags(content_with_hashtags)

        assert extracted_content == "This is a post with and"
        assert len(extracted_hashtags) == 3
        assert "#test" in extracted_hashtags
        assert "#hashtags" in extracted_hashtags
        assert "#more" in extracted_hashtags

    def test_add_call_to_action(self):
        """
        Test adding platform-specific call-to-action.

        Input: Content and platform
        Expected: Content with appropriate CTA
        """
        base_content = "Check out our new product!"

        twitter_cta = add_call_to_action(base_content, "twitter")
        facebook_cta = add_call_to_action(base_content, "facebook")
        instagram_cta = add_call_to_action(base_content, "instagram")

        assert "Reply below" in twitter_cta
        assert "Like and share" in facebook_cta
        assert "Comment below" in instagram_cta

    def test_format_with_emojis(self):
        """
        Test adding emojis to content.

        Input: Content and platform
        Expected: Emojis added for appropriate platforms
        """
        base_content = "New product launch!"

        twitter_formatted = format_with_emojis(base_content, "twitter")
        facebook_formatted = format_with_emojis(base_content, "facebook")
        instagram_formatted = format_with_emojis(base_content, "instagram")

        # Twitter should not add emojis (not optimized for it like Facebook/Instagram)
        assert "✨" not in twitter_formatted
        # Facebook and Instagram should add emojis
        assert "✨" in facebook_formatted
        assert "✨" in instagram_formatted

    def test_twitter_formatting_with_mixed_content(self):
        """
        Test Twitter formatting with mixed content and hashtags.

        Input: Content with some existing hashtags and new ones
        Expected: Proper formatting respecting character limit
        """
        content = "This is a test of Twitter formatting functionality"
        hashtags = ["#test", "#twitter", "#formatting", "#socialmedia"]

        formatted = format_for_twitter(content, hashtags)

        # Check that all hashtags appear in the result
        for hashtag in hashtags:
            assert hashtag in formatted

        # Should be within Twitter's character limit
        assert len(formatted) <= 280

    def test_formatting_preserves_content_meaning(self):
        """
        Test that formatting doesn't alter the essential meaning of content.

        Input: Content with important keywords
        Expected: Keywords preserved in formatted content
        """
        original_content = "New product launch with innovative features!"
        hashtags = ["#launch", "#product", "#innovation"]

        twitter_formatted = format_for_platform(original_content, "twitter", hashtags)
        facebook_formatted = format_for_platform(original_content, "facebook", hashtags)
        instagram_formatted = format_for_platform(original_content, "instagram", hashtags)

        # All should contain important keywords (unless truncated)
        assert "product" in twitter_formatted.lower() or "..." in twitter_formatted
        assert "product" in facebook_formatted.lower()
        assert "product" in instagram_formatted.lower() or "..." in instagram_formatted


if __name__ == "__main__":
    test = TestContentFormatter()

    print("Running Twitter formatting character limit test...")
    try:
        test.test_twitter_formatting_character_limit()
        print("✅ Twitter formatting character limit test passed")
    except Exception as e:
        print(f"❌ Twitter formatting character limit test failed: {e}")

    print("Running Twitter hashtag limiting test...")
    try:
        test.test_twitter_hashtag_limiting()
        print("✅ Twitter hashtag limiting test passed")
    except Exception as e:
        print(f"❌ Twitter hashtag limiting test failed: {e}")

    print("Running Facebook formatting no limit test...")
    try:
        test.test_facebook_formatting_no_limit()
        print("✅ Facebook formatting no limit test passed")
    except Exception as e:
        print(f"❌ Facebook formatting no limit test failed: {e}")

    print("Running Instagram formatting character limit test...")
    try:
        test.test_instagram_formatting_character_limit()
        print("✅ Instagram formatting character limit test passed")
    except Exception as e:
        print(f"❌ Instagram formatting character limit test failed: {e}")

    print("Running Instagram hashtag limiting test...")
    try:
        test.test_instagram_hashtag_limiting()
        print("✅ Instagram hashtag limiting test passed")
    except Exception as e:
        print(f"❌ Instagram hashtag limiting test failed: {e}")

    print("Running format for unknown platform test...")
    try:
        test.test_format_for_unknown_platform()
        print("✅ Format for unknown platform test passed")
    except Exception as e:
        print(f"❌ Format for unknown platform test failed: {e}")

    print("Running optimize hashtags Twitter test...")
    try:
        test.test_optimize_hashtags_twitter()
        print("✅ Optimize hashtags Twitter test passed")
    except Exception as e:
        print(f"❌ Optimize hashtags Twitter test failed: {e}")

    print("Running optimize hashtags Instagram test...")
    try:
        test.test_optimize_hashtags_instagram()
        print("✅ Optimize hashtags Instagram test passed")
    except Exception as e:
        print(f"❌ Optimize hashtags Instagram test failed: {e}")

    print("Running optimize hashtags Facebook test...")
    try:
        test.test_optimize_hashtags_facebook()
        print("✅ Optimize hashtags Facebook test passed")
    except Exception as e:
        print(f"❌ Optimize hashtags Facebook test failed: {e}")

    print("Running truncate content function test...")
    try:
        test.test_truncate_content_function()
        print("✅ Truncate content function test passed")
    except Exception as e:
        print(f"❌ Truncate content function test failed: {e}")

    print("Running extract hashtags test...")
    try:
        test.test_extract_hashtags()
        print("✅ Extract hashtags test passed")
    except Exception as e:
        print(f"❌ Extract hashtags test failed: {e}")

    print("Running add call to action test...")
    try:
        test.test_add_call_to_action()
        print("✅ Add call to action test passed")
    except Exception as e:
        print(f"❌ Add call to action test failed: {e}")

    print("Running format with emojis test...")
    try:
        test.test_format_with_emojis()
        print("✅ Format with emojis test passed")
    except Exception as e:
        print(f"❌ Format with emojis test failed: {e}")

    print("Running Twitter formatting with mixed content test...")
    try:
        test.test_twitter_formatting_with_mixed_content()
        print("✅ Twitter formatting with mixed content test passed")
    except Exception as e:
        print(f"❌ Twitter formatting with mixed content test failed: {e}")

    print("Running formatting preserves content meaning test...")
    try:
        test.test_formatting_preserves_content_meaning()
        print("✅ Formatting preserves content meaning test passed")
    except Exception as e:
        print(f"❌ Formatting preserves content meaning test failed: {e}")

    print("All content formatter unit tests completed!")