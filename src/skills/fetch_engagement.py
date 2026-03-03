"""
Fetch Engagement Metrics Skill

Collects engagement metrics from all social media platforms with:
- Metrics collection (likes, comments, shares, reach)
- Sentiment analysis on comments and reactions
- Weekly engagement summary generation
- Cross-platform analytics

This skill can be executed autonomously as part of multi-step workflows.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from src.mcp.twitter_client import TwitterClient
from src.mcp.facebook_client import FacebookClient
from src.mcp.instagram_client import InstagramClient
from src.models.social_media_post import SocialMediaPost, EngagementMetrics, SentimentScores, SentimentClass
from src.audit.gold_logger import GoldAuditLogger
from src.utils.sentiment import analyze_sentiment, get_sentiment_summary


def fetch_engagement(input_params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch engagement metrics for a social media post

    Args:
        input_params: Post data (post_id, platforms)
        context: Workflow context

    Returns:
        Dictionary with engagement metrics for all platforms
    """
    audit_logger = GoldAuditLogger()

    # Extract parameters
    post_id = input_params.get("post_id")
    platforms = input_params.get("platforms", ["twitter", "facebook", "instagram"])

    if not post_id:
        raise ValueError("post_id is required")

    # Load post
    try:
        post = SocialMediaPost.load(post_id, directory="Done")
    except FileNotFoundError:
        raise ValueError(f"Post {post_id} not found")

    # Initialize clients
    twitter_client = TwitterClient()
    facebook_client = FacebookClient()
    instagram_client = InstagramClient()

    # Collect metrics from each platform
    all_metrics = []
    errors = []

    # Twitter metrics
    if "twitter" in platforms and post.is_published_to("twitter"):
        try:
            twitter_post_id = post.platform_post_ids["twitter"]
            twitter_result = twitter_client.get_tweet_metrics(twitter_post_id)

            if twitter_result.get("success"):
                metrics = EngagementMetrics(
                    platform="twitter",
                    likes=twitter_result["likes"],
                    comments=twitter_result["comments"],
                    shares=twitter_result["shares"],
                    reach=twitter_result["reach"],
                    engagement_rate=twitter_result["engagement_rate"],
                    collected_at=datetime.utcnow(),
                )
                all_metrics.append(metrics)
                post.add_engagement_metrics(metrics)

                # Log success
                audit_logger.log_action(
                    action_type="STEP_EXECUTE",
                    action_name="fetch_twitter_metrics",
                    parameters={"post_id": post_id, "tweet_id": twitter_post_id},
                    decision_rationale="Fetching Twitter engagement metrics",
                    execution_result="SUCCESS",
                    result_data=twitter_result,
                    business_impact=f"Twitter metrics: {twitter_result['likes']} likes, {twitter_result['reach']} reach",
                )
            else:
                errors.append({"platform": "twitter", "error": twitter_result.get("error")})

        except Exception as e:
            errors.append({"platform": "twitter", "error": str(e)})

            audit_logger.log_action(
                action_type="ERROR",
                action_name="fetch_twitter_metrics_failed",
                parameters={"post_id": post_id},
                decision_rationale="Twitter metrics fetch failed",
                execution_result="FAILURE",
                result_data={},
                business_impact="Twitter metrics unavailable",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "recovery_attempted": False,
                    "recovery_result": "N/A",
                },
            )

    # Facebook metrics
    if "facebook" in platforms and post.is_published_to("facebook"):
        try:
            facebook_post_id = post.platform_post_ids["facebook"]
            facebook_result = facebook_client.get_post_metrics(facebook_post_id)

            if facebook_result.get("success"):
                metrics = EngagementMetrics(
                    platform="facebook",
                    likes=facebook_result["likes"],
                    comments=facebook_result["comments"],
                    shares=facebook_result["shares"],
                    reach=facebook_result["reach"],
                    engagement_rate=facebook_result["engagement_rate"],
                    collected_at=datetime.utcnow(),
                )
                all_metrics.append(metrics)
                post.add_engagement_metrics(metrics)

                # Log success
                audit_logger.log_action(
                    action_type="STEP_EXECUTE",
                    action_name="fetch_facebook_metrics",
                    parameters={"post_id": post_id, "facebook_post_id": facebook_post_id},
                    decision_rationale="Fetching Facebook engagement metrics",
                    execution_result="SUCCESS",
                    result_data=facebook_result,
                    business_impact=f"Facebook metrics: {facebook_result['likes']} likes, {facebook_result['reach']} reach",
                )
            else:
                errors.append({"platform": "facebook", "error": facebook_result.get("error")})

        except Exception as e:
            errors.append({"platform": "facebook", "error": str(e)})

            audit_logger.log_action(
                action_type="ERROR",
                action_name="fetch_facebook_metrics_failed",
                parameters={"post_id": post_id},
                decision_rationale="Facebook metrics fetch failed",
                execution_result="FAILURE",
                result_data={},
                business_impact="Facebook metrics unavailable",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "recovery_attempted": False,
                    "recovery_result": "N/A",
                },
            )

    # Instagram metrics
    if "instagram" in platforms and post.is_published_to("instagram"):
        try:
            instagram_post_id = post.platform_post_ids["instagram"]
            instagram_result = instagram_client.get_post_metrics(instagram_post_id)

            if instagram_result.get("success"):
                metrics = EngagementMetrics(
                    platform="instagram",
                    likes=instagram_result["likes"],
                    comments=instagram_result["comments"],
                    shares=instagram_result["shares"],
                    reach=instagram_result["reach"],
                    engagement_rate=instagram_result["engagement_rate"],
                    collected_at=datetime.utcnow(),
                )
                all_metrics.append(metrics)
                post.add_engagement_metrics(metrics)

                # Log success
                audit_logger.log_action(
                    action_type="STEP_EXECUTE",
                    action_name="fetch_instagram_metrics",
                    parameters={"post_id": post_id, "instagram_post_id": instagram_post_id},
                    decision_rationale="Fetching Instagram engagement metrics",
                    execution_result="SUCCESS",
                    result_data=instagram_result,
                    business_impact=f"Instagram metrics: {instagram_result['likes']} likes, {instagram_result['reach']} reach",
                )
            else:
                errors.append({"platform": "instagram", "error": instagram_result.get("error")})

        except Exception as e:
            errors.append({"platform": "instagram", "error": str(e)})

            audit_logger.log_action(
                action_type="ERROR",
                action_name="fetch_instagram_metrics_failed",
                parameters={"post_id": post_id},
                decision_rationale="Instagram metrics fetch failed",
                execution_result="FAILURE",
                result_data={},
                business_impact="Instagram metrics unavailable",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "recovery_attempted": False,
                    "recovery_result": "N/A",
                },
            )

    # Perform sentiment analysis on engagement
    if all_metrics:
        sentiment_result = analyze_engagement_sentiment(post, all_metrics)
        post.update_sentiment(sentiment_result)

    # Save updated post
    post.save(directory="Done")

    # Calculate totals
    total_engagement = post.get_total_engagement()
    avg_engagement_rate = post.get_average_engagement_rate()

    # Log overall result
    audit_logger.log_action(
        action_type="STEP_EXECUTE",
        action_name="fetch_engagement_complete",
        parameters={
            "post_id": post_id,
            "platforms_checked": len(platforms),
            "metrics_collected": len(all_metrics),
        },
        decision_rationale="Engagement metrics collection completed",
        execution_result="SUCCESS" if all_metrics else "PARTIAL",
        result_data={
            "total_likes": total_engagement["likes"],
            "total_reach": total_engagement["reach"],
            "avg_engagement_rate": avg_engagement_rate,
        },
        business_impact=f"Collected metrics from {len(all_metrics)} platforms",
    )

    return {
        "success": len(all_metrics) > 0,
        "post_id": post_id,
        "metrics": [m.to_dict() for m in all_metrics],
        "total_engagement": total_engagement,
        "avg_engagement_rate": avg_engagement_rate,
        "sentiment": post.sentiment_scores.to_dict() if post.sentiment_scores else None,
        "errors": errors,
    }


def analyze_engagement_sentiment(
    post: SocialMediaPost,
    metrics: List[EngagementMetrics]
) -> SentimentScores:
    """
    Analyze sentiment of engagement data

    Args:
        post: SocialMediaPost instance
        metrics: List of EngagementMetrics

    Returns:
        SentimentScores instance
    """
    # For now, use a simple heuristic based on engagement rate
    # In production, this would analyze actual comments and reactions

    # Calculate average engagement rate
    avg_rate = sum(m.engagement_rate for m in metrics) / len(metrics)

    # Classify sentiment based on engagement rate
    if avg_rate >= 0.05:  # 5% or higher is excellent
        classification = SentimentClass.POSITIVE
        polarity = 0.8
    elif avg_rate >= 0.02:  # 2-5% is good
        classification = SentimentClass.POSITIVE
        polarity = 0.5
    elif avg_rate >= 0.01:  # 1-2% is neutral
        classification = SentimentClass.NEUTRAL
        polarity = 0.0
    else:  # Below 1% is concerning
        classification = SentimentClass.NEGATIVE
        polarity = -0.3

    # Create sentiment scores
    return SentimentScores(
        overall_polarity=polarity,
        overall_classification=classification,
        comment_sentiments=[],  # TODO: Analyze actual comments
        analyzed_at=datetime.utcnow(),
    )


def generate_weekly_summary(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate weekly engagement summary across all platforms

    Args:
        context: Workflow context

    Returns:
        Dictionary with weekly summary data
    """
    audit_logger = GoldAuditLogger()

    # Calculate date range (last 7 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    # Load all posts from Done directory
    import os
    from pathlib import Path

    done_dir = Path("Done")
    post_files = list(done_dir.glob("post_*.json"))

    # Filter posts from last 7 days
    weekly_posts = []
    for post_file in post_files:
        try:
            post = SocialMediaPost.load(post_file.stem.replace("post_", ""), directory="Done")
            if post.created_at >= start_date:
                weekly_posts.append(post)
        except Exception:
            continue

    # Aggregate metrics
    total_posts = len(weekly_posts)
    total_likes = 0
    total_comments = 0
    total_shares = 0
    total_reach = 0
    platform_breakdown = {
        "twitter": {"posts": 0, "likes": 0, "reach": 0},
        "facebook": {"posts": 0, "likes": 0, "reach": 0},
        "instagram": {"posts": 0, "likes": 0, "reach": 0},
    }

    for post in weekly_posts:
        engagement = post.get_total_engagement()
        total_likes += engagement["likes"]
        total_comments += engagement["comments"]
        total_shares += engagement["shares"]
        total_reach += engagement["reach"]

        # Platform breakdown
        for metrics in post.engagement_metrics:
            platform = metrics.platform
            if platform in platform_breakdown:
                platform_breakdown[platform]["posts"] += 1
                platform_breakdown[platform]["likes"] += metrics.likes
                platform_breakdown[platform]["reach"] += metrics.reach

    # Calculate averages
    avg_engagement_rate = (
        sum(post.get_average_engagement_rate() for post in weekly_posts) / total_posts
        if total_posts > 0 else 0.0
    )

    # Sentiment analysis
    sentiment_counts = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
    for post in weekly_posts:
        if post.sentiment_scores:
            sentiment_counts[post.sentiment_scores.overall_classification.value] += 1

    # Create summary
    summary = {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        "total_posts": total_posts,
        "total_engagement": {
            "likes": total_likes,
            "comments": total_comments,
            "shares": total_shares,
            "reach": total_reach,
        },
        "avg_engagement_rate": avg_engagement_rate,
        "platform_breakdown": platform_breakdown,
        "sentiment_distribution": sentiment_counts,
        "top_performing_posts": _get_top_posts(weekly_posts, limit=3),
    }

    # Log summary generation
    audit_logger.log_action(
        action_type="STEP_EXECUTE",
        action_name="generate_weekly_summary",
        parameters={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
        decision_rationale="Generating weekly engagement summary",
        execution_result="SUCCESS",
        result_data=summary,
        business_impact=f"Weekly summary: {total_posts} posts, {total_reach} total reach",
    )

    return {
        "success": True,
        "summary": summary,
    }


def _get_top_posts(posts: List[SocialMediaPost], limit: int = 3) -> List[Dict[str, Any]]:
    """
    Get top performing posts by engagement rate

    Args:
        posts: List of SocialMediaPost instances
        limit: Number of top posts to return

    Returns:
        List of top post summaries
    """
    # Sort by average engagement rate
    sorted_posts = sorted(
        posts,
        key=lambda p: p.get_average_engagement_rate(),
        reverse=True
    )

    # Return top N
    top_posts = []
    for post in sorted_posts[:limit]:
        engagement = post.get_total_engagement()
        top_posts.append({
            "post_id": post.post_id,
            "content_preview": post.content[:100] + "..." if len(post.content) > 100 else post.content,
            "platforms": post.get_published_platforms(),
            "total_likes": engagement["likes"],
            "total_reach": engagement["reach"],
            "engagement_rate": post.get_average_engagement_rate(),
            "sentiment": post.sentiment_scores.overall_classification.value if post.sentiment_scores else "UNKNOWN",
        })

    return top_posts
