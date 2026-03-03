"""
Unified Social Media Broadcasting Skill

Broadcasts content simultaneously to Twitter, Facebook, and Instagram with:
- Platform-specific content formatting
- Graceful degradation (continue on single platform failure)
- Comprehensive error handling
- Audit logging for all operations

This skill can be executed autonomously as part of multi-step workflows.
"""

from typing import Dict, Any, List
from src.mcp.twitter_client import TwitterClient
from src.mcp.facebook_client import FacebookClient
from src.mcp.instagram_client import InstagramClient
from src.models.social_media_post import SocialMediaPost, PlatformVariant
from src.audit.gold_logger import GoldAuditLogger
from src.utils.content_formatter import format_for_platform


def broadcast_marketing(input_params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Broadcast content to multiple social media platforms simultaneously

    Args:
        input_params: Content data (content, hashtags, media_urls)
        context: Workflow context

    Returns:
        Dictionary with broadcast results for each platform
    """
    audit_logger = GoldAuditLogger()

    # Extract parameters
    content = input_params.get("content", "")
    hashtags = input_params.get("hashtags", [])
    media_urls = input_params.get("media_urls", [])

    # Create SocialMediaPost model
    post = SocialMediaPost(
        content=content,
        hashtags=hashtags,
        media_urls=media_urls,
    )

    # Mark as publishing
    post.mark_publishing()

    # Initialize clients
    twitter_client = TwitterClient()
    facebook_client = FacebookClient()
    instagram_client = InstagramClient()

    # Track results
    results = {}
    successful_platforms = []
    failed_platforms = []

    # Platform 1: Twitter/X
    try:
        # Format content for Twitter (280 char limit)
        twitter_content = format_for_platform(content, "twitter", hashtags)

        # Create platform variant
        post.platform_variants["twitter"] = PlatformVariant(
            content=twitter_content,
            character_count=len(twitter_content),
            media_count=len(media_urls),
            hashtag_count=len(hashtags),
        )

        # Post to Twitter
        twitter_result = twitter_client.post_tweet(
            content=twitter_content,
            media_urls=media_urls if media_urls else None,
        )

        if twitter_result.get("success"):
            # Record publication
            post.record_publication(
                platform="twitter",
                platform_post_id=twitter_result["tweet_id"],
            )
            successful_platforms.append("twitter")
            results["twitter"] = {
                "success": True,
                "post_id": twitter_result["tweet_id"],
                "url": twitter_result["tweet_url"],
            }

            # Log success
            audit_logger.log_action(
                action_type="STEP_EXECUTE",
                action_name="broadcast_twitter",
                parameters={"content_length": len(twitter_content)},
                decision_rationale="Broadcasting to Twitter",
                execution_result="SUCCESS",
                result_data={"tweet_id": twitter_result["tweet_id"]},
                business_impact=f"Twitter post published: {twitter_content[:50]}...",
            )
        else:
            failed_platforms.append("twitter")
            results["twitter"] = {
                "success": False,
                "error": twitter_result.get("error", "Unknown error"),
            }

    except Exception as e:
        # Graceful degradation: log error but continue with other platforms
        failed_platforms.append("twitter")
        results["twitter"] = {
            "success": False,
            "error": str(e),
        }

        audit_logger.log_action(
            action_type="ERROR",
            action_name="broadcast_twitter_failed",
            parameters={"content_length": len(content)},
            decision_rationale="Twitter broadcast failed, continuing with other platforms",
            execution_result="FAILURE",
            result_data={},
            business_impact="Twitter post not published, graceful degradation active",
            error_details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "recovery_attempted": True,
                "recovery_result": "continuing_with_other_platforms",
            },
        )

    # Platform 2: Facebook
    try:
        # Format content for Facebook
        facebook_content = format_for_platform(content, "facebook", hashtags)

        # Create platform variant
        post.platform_variants["facebook"] = PlatformVariant(
            content=facebook_content,
            character_count=len(facebook_content),
            media_count=len(media_urls),
            hashtag_count=len(hashtags),
        )

        # Post to Facebook
        facebook_result = facebook_client.post_to_page(
            content=facebook_content,
            media_urls=media_urls if media_urls else None,
        )

        if facebook_result.get("success"):
            # Record publication
            post.record_publication(
                platform="facebook",
                platform_post_id=facebook_result["post_id"],
            )
            successful_platforms.append("facebook")
            results["facebook"] = {
                "success": True,
                "post_id": facebook_result["post_id"],
                "url": facebook_result["post_url"],
            }

            # Log success
            audit_logger.log_action(
                action_type="STEP_EXECUTE",
                action_name="broadcast_facebook",
                parameters={"content_length": len(facebook_content)},
                decision_rationale="Broadcasting to Facebook",
                execution_result="SUCCESS",
                result_data={"post_id": facebook_result["post_id"]},
                business_impact=f"Facebook post published: {facebook_content[:50]}...",
            )
        else:
            failed_platforms.append("facebook")
            results["facebook"] = {
                "success": False,
                "error": facebook_result.get("error", "Unknown error"),
            }

    except Exception as e:
        # Graceful degradation: log error but continue with other platforms
        failed_platforms.append("facebook")
        results["facebook"] = {
            "success": False,
            "error": str(e),
        }

        audit_logger.log_action(
            action_type="ERROR",
            action_name="broadcast_facebook_failed",
            parameters={"content_length": len(content)},
            decision_rationale="Facebook broadcast failed, continuing with other platforms",
            execution_result="FAILURE",
            result_data={},
            business_impact="Facebook post not published, graceful degradation active",
            error_details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "recovery_attempted": True,
                "recovery_result": "continuing_with_other_platforms",
            },
        )

    # Platform 3: Instagram
    try:
        # Format content for Instagram (2200 char limit, max 30 hashtags)
        instagram_content = format_for_platform(content, "instagram", hashtags)

        # Create platform variant
        post.platform_variants["instagram"] = PlatformVariant(
            content=instagram_content,
            character_count=len(instagram_content),
            media_count=len(media_urls),
            hashtag_count=min(len(hashtags), 30),  # Instagram max 30 hashtags
        )

        # Instagram requires an image
        if media_urls:
            # Post to Instagram
            instagram_result = instagram_client.post_to_instagram(
                content=instagram_content,
                hashtags=hashtags[:30],  # Limit to 30 hashtags
                image_url=media_urls[0],  # Use first image
            )

            if instagram_result.get("success"):
                # Record publication
                post.record_publication(
                    platform="instagram",
                    platform_post_id=instagram_result["post_id"],
                )
                successful_platforms.append("instagram")
                results["instagram"] = {
                    "success": True,
                    "post_id": instagram_result["post_id"],
                    "url": instagram_result["post_url"],
                }

                # Log success
                audit_logger.log_action(
                    action_type="STEP_EXECUTE",
                    action_name="broadcast_instagram",
                    parameters={"content_length": len(instagram_content)},
                    decision_rationale="Broadcasting to Instagram",
                    execution_result="SUCCESS",
                    result_data={"post_id": instagram_result["post_id"]},
                    business_impact=f"Instagram post published: {instagram_content[:50]}...",
                )
            else:
                failed_platforms.append("instagram")
                results["instagram"] = {
                    "success": False,
                    "error": instagram_result.get("error", "Unknown error"),
                }
        else:
            # Instagram requires media
            failed_platforms.append("instagram")
            results["instagram"] = {
                "success": False,
                "error": "Instagram requires at least one image",
            }

    except Exception as e:
        # Graceful degradation: log error
        failed_platforms.append("instagram")
        results["instagram"] = {
            "success": False,
            "error": str(e),
        }

        audit_logger.log_action(
            action_type="ERROR",
            action_name="broadcast_instagram_failed",
            parameters={"content_length": len(content)},
            decision_rationale="Instagram broadcast failed",
            execution_result="FAILURE",
            result_data={},
            business_impact="Instagram post not published",
            error_details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "recovery_attempted": False,
                "recovery_result": "N/A",
            },
        )

    # Update post status
    post.mark_published(successful_platforms)

    # Save post
    post_path = post.save(directory="Done")

    # Determine overall success
    overall_success = len(successful_platforms) > 0

    # Log overall broadcast result
    audit_logger.log_action(
        action_type="STEP_EXECUTE",
        action_name="broadcast_marketing_complete",
        parameters={
            "platforms_attempted": 3,
            "platforms_successful": len(successful_platforms),
            "platforms_failed": len(failed_platforms),
        },
        decision_rationale="Multi-platform broadcast completed",
        execution_result="SUCCESS" if overall_success else "FAILURE",
        result_data={
            "successful_platforms": successful_platforms,
            "failed_platforms": failed_platforms,
            "post_id": post.post_id,
        },
        business_impact=f"Broadcast to {len(successful_platforms)}/3 platforms successful",
    )

    return {
        "success": overall_success,
        "post_id": post.post_id,
        "post_path": post_path,
        "platforms_successful": successful_platforms,
        "platforms_failed": failed_platforms,
        "results": results,
        "status": post.status.value,
    }
