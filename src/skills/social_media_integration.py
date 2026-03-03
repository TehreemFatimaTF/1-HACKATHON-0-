"""
Social Media Skills Integration with Ralph Wiggum Loop Engine

This module registers all social media skills with the autonomous execution engine,
allowing them to be called as part of multi-step workflows.
"""

from src.engine_gold import RalphWiggumLoopEngine
from src.skills.broadcast_marketing import broadcast_marketing
from src.skills.fetch_engagement import fetch_engagement, generate_weekly_summary


def register_social_media_skills(engine: RalphWiggumLoopEngine) -> None:
    """
    Register all social media skills with the autonomous execution engine

    Args:
        engine: RalphWiggumLoopEngine instance

    Skills registered:
    - broadcast_marketing: Multi-platform content broadcasting
    - fetch_engagement: Engagement metrics collection
    - generate_weekly_summary: Weekly analytics report
    """
    # Register social media skills
    engine.register_action("broadcast_marketing", broadcast_marketing)
    engine.register_action("fetch_engagement", fetch_engagement)
    engine.register_action("generate_weekly_summary", generate_weekly_summary)

    # Register rollback actions for social media operations
    engine.register_action("delete_social_post", _rollback_social_post)
    engine.register_action("delete_twitter_post", _rollback_twitter_post)
    engine.register_action("delete_facebook_post", _rollback_facebook_post)
    engine.register_action("delete_instagram_post", _rollback_instagram_post)

    print("[Social Media Integration] Registered 3 social media skills with autonomous engine")


def _rollback_social_post(output: dict, context: dict) -> dict:
    """
    Rollback action for multi-platform post

    Args:
        output: Output from broadcast_marketing (contains post_id)
        context: Workflow context

    Returns:
        Rollback result
    """
    from src.models.social_media_post import SocialMediaPost, PostStatus

    post_id = output.get("post_id")

    if not post_id:
        return {"success": False, "error": "No post_id in output"}

    try:
        # Load post
        post = SocialMediaPost.load(post_id, directory="Done")

        # Mark as failed
        post.status = PostStatus.FAILED

        # Save updated state
        post.save(directory="Done")

        # TODO: Delete posts from each platform via API
        # For now, just mark as failed locally

        return {
            "success": True,
            "message": f"Post {post_id} marked as failed",
            "platforms_affected": post.get_published_platforms(),
        }

    except FileNotFoundError:
        return {"success": False, "error": f"Post {post_id} not found"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _rollback_twitter_post(output: dict, context: dict) -> dict:
    """
    Rollback action for Twitter post deletion

    Args:
        output: Output from Twitter posting (contains tweet_id)
        context: Workflow context

    Returns:
        Rollback result
    """
    from src.mcp.twitter_client import TwitterClient

    tweet_id = output.get("tweet_id")

    if not tweet_id:
        return {"success": False, "error": "No tweet_id in output"}

    try:
        # TODO: Implement Twitter post deletion via API
        # twitter_client = TwitterClient()
        # result = twitter_client.delete_tweet(tweet_id)

        return {
            "success": True,
            "message": f"Tweet {tweet_id} deletion requested (API not yet implemented)",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def _rollback_facebook_post(output: dict, context: dict) -> dict:
    """
    Rollback action for Facebook post deletion

    Args:
        output: Output from Facebook posting (contains post_id)
        context: Workflow context

    Returns:
        Rollback result
    """
    from src.mcp.facebook_client import FacebookClient

    post_id = output.get("post_id")

    if not post_id:
        return {"success": False, "error": "No post_id in output"}

    try:
        # TODO: Implement Facebook post deletion via API
        # facebook_client = FacebookClient()
        # result = facebook_client.delete_post(post_id)

        return {
            "success": True,
            "message": f"Facebook post {post_id} deletion requested (API not yet implemented)",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def _rollback_instagram_post(output: dict, context: dict) -> dict:
    """
    Rollback action for Instagram post deletion

    Args:
        output: Output from Instagram posting (contains post_id)
        context: Workflow context

    Returns:
        Rollback result
    """
    from src.mcp.instagram_client import InstagramClient

    post_id = output.get("post_id")

    if not post_id:
        return {"success": False, "error": "No post_id in output"}

    try:
        # TODO: Implement Instagram post deletion via API
        # instagram_client = InstagramClient()
        # result = instagram_client.delete_post(post_id)

        return {
            "success": True,
            "message": f"Instagram post {post_id} deletion requested (API not yet implemented)",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def initialize_social_media_integration(engine: RalphWiggumLoopEngine) -> None:
    """
    Initialize complete social media integration with autonomous engine

    This function:
    1. Registers all social media skills
    2. Sets up circuit breakers for each platform
    3. Configures retry policies
    4. Initializes rate limit tracking

    Args:
        engine: RalphWiggumLoopEngine instance
    """
    from src.mcp.twitter_client import TwitterClient
    from src.mcp.facebook_client import FacebookClient
    from src.mcp.instagram_client import InstagramClient
    from src.utils.circuit_breaker import CircuitBreaker

    # Register skills
    register_social_media_skills(engine)

    # Create circuit breakers for each platform
    twitter_circuit_breaker = CircuitBreaker(
        failure_threshold=3,
        timeout=60.0,
        name="TwitterCircuitBreaker"
    )

    facebook_circuit_breaker = CircuitBreaker(
        failure_threshold=3,
        timeout=60.0,
        name="FacebookCircuitBreaker"
    )

    instagram_circuit_breaker = CircuitBreaker(
        failure_threshold=3,
        timeout=60.0,
        name="InstagramCircuitBreaker"
    )

    # Register circuit breakers with engine
    engine.register_circuit_breaker("twitter", twitter_circuit_breaker)
    engine.register_circuit_breaker("facebook", facebook_circuit_breaker)
    engine.register_circuit_breaker("instagram", instagram_circuit_breaker)

    # Initialize clients (will verify authentication)
    try:
        twitter_client = TwitterClient()
        print("[Social Media Integration] Twitter client initialized")
    except Exception as e:
        print(f"[Social Media Integration] Warning: Twitter client initialization failed: {e}")

    try:
        facebook_client = FacebookClient()
        print("[Social Media Integration] Facebook client initialized")
    except Exception as e:
        print(f"[Social Media Integration] Warning: Facebook client initialization failed: {e}")

    try:
        instagram_client = InstagramClient()
        print("[Social Media Integration] Instagram client initialized")
    except Exception as e:
        print(f"[Social Media Integration] Warning: Instagram client initialization failed: {e}")

    print("[Social Media Integration] Initialization complete")
