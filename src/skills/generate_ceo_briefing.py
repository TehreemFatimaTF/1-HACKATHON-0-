"""
Weekly Business Audit & CEO Briefing Generation Skill

Generates comprehensive weekly business reports with:
- Accounting summary from Odoo
- Social media engagement metrics
- Task completion statistics
- Business impact assessment
- Key insights and recommendations

This skill can be executed autonomously as part of scheduled workflows.
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import json

from src.mcp.odoo_client import OdooClient
from src.skills.fetch_engagement import generate_weekly_summary
from src.audit.gold_logger import GoldAuditLogger


def generate_ceo_briefing(input_params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate weekly CEO briefing with business metrics and insights

    Args:
        input_params: Optional parameters (start_date, end_date)
        context: Workflow context

    Returns:
        Dictionary with briefing data and file path
    """
    audit_logger = GoldAuditLogger()

    # Calculate date range (last 7 days by default)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    if "start_date" in input_params:
        start_date = datetime.fromisoformat(input_params["start_date"])
    if "end_date" in input_params:
        end_date = datetime.fromisoformat(input_params["end_date"])

    # Initialize components
    briefing_data = {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "week_number": start_date.isocalendar()[1],
            "year": start_date.year,
        },
        "generated_at": datetime.utcnow().isoformat(),
    }

    # Section 1: Accounting Summary
    try:
        accounting_summary = _get_accounting_summary(start_date, end_date)
        briefing_data["accounting"] = accounting_summary
    except Exception as e:
        briefing_data["accounting"] = {
            "error": str(e),
            "message": "Accounting data unavailable",
        }

    # Section 2: Social Media Performance
    try:
        social_summary = generate_weekly_summary(context)
        briefing_data["social_media"] = social_summary.get("summary", {})
    except Exception as e:
        briefing_data["social_media"] = {
            "error": str(e),
            "message": "Social media data unavailable",
        }

    # Section 3: Task Completion Statistics
    try:
        task_stats = _get_task_statistics(start_date, end_date)
        briefing_data["tasks"] = task_stats
    except Exception as e:
        briefing_data["tasks"] = {
            "error": str(e),
            "message": "Task statistics unavailable",
        }

    # Section 4: Audit Trail Summary
    try:
        audit_summary = _get_audit_summary(start_date, end_date)
        briefing_data["audit"] = audit_summary
    except Exception as e:
        briefing_data["audit"] = {
            "error": str(e),
            "message": "Audit data unavailable",
        }

    # Section 5: Key Insights & Recommendations
    insights = _generate_insights(briefing_data)
    briefing_data["insights"] = insights

    # Generate markdown report
    report_path = _generate_markdown_report(briefing_data)

    # Log briefing generation
    audit_logger.log_action(
        action_type="STEP_EXECUTE",
        action_name="generate_ceo_briefing",
        parameters={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        decision_rationale="Generating weekly CEO briefing",
        execution_result="SUCCESS",
        result_data={
            "report_path": report_path,
            "sections_generated": len(briefing_data.keys()),
        },
        business_impact=f"Weekly briefing generated for week {briefing_data['period']['week_number']}",
    )

    return {
        "success": True,
        "briefing": briefing_data,
        "report_path": report_path,
    }


def _get_accounting_summary(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Get accounting summary from Odoo"""
    try:
        odoo_client = OdooClient()
        result = odoo_client.get_accounting_summary(
            start_date=start_date.date().isoformat(),
            end_date=end_date.date().isoformat(),
        )

        if result["status"] == "success":
            return result["data"]
        else:
            return {
                "error": result.get("message", "Odoo unavailable"),
                "queued": result["status"] == "queued",
            }

    except Exception as e:
        return {
            "error": str(e),
            "message": "Odoo client not available",
        }


def _get_task_statistics(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Get task completion statistics"""
    done_dir = Path("Done")
    needs_action_dir = Path("Needs_Action")

    # Count completed tasks
    completed_tasks = 0
    if done_dir.exists():
        for task_file in done_dir.glob("task_*.md"):
            try:
                # Check if file was modified in date range
                mtime = datetime.fromtimestamp(task_file.stat().st_mtime)
                if start_date <= mtime <= end_date:
                    completed_tasks += 1
            except Exception:
                continue

    # Count pending tasks
    pending_tasks = 0
    if needs_action_dir.exists():
        pending_tasks = len(list(needs_action_dir.glob("*.md")))

    # Calculate completion rate
    total_tasks = completed_tasks + pending_tasks
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    return {
        "completed": completed_tasks,
        "pending": pending_tasks,
        "total": total_tasks,
        "completion_rate": round(completion_rate, 1),
    }


def _get_audit_summary(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Get audit trail summary"""
    audit_dir = Path("Logs/Audit_Trail")

    total_actions = 0
    successful_actions = 0
    failed_actions = 0
    action_types = {}

    if audit_dir.exists():
        # Read audit logs for the date range
        for day in range((end_date - start_date).days + 1):
            current_date = start_date + timedelta(days=day)
            log_file = audit_dir / f"gold_audit_{current_date.strftime('%Y-%m-%d')}.jsonl"

            if log_file.exists():
                try:
                    with open(log_file, "r") as f:
                        for line in f:
                            entry = json.loads(line)
                            total_actions += 1

                            # Count by result
                            if entry.get("execution_result") == "SUCCESS":
                                successful_actions += 1
                            elif entry.get("execution_result") == "FAILURE":
                                failed_actions += 1

                            # Count by action type
                            action_type = entry.get("action_type", "UNKNOWN")
                            action_types[action_type] = action_types.get(action_type, 0) + 1

                except Exception:
                    continue

    # Calculate success rate
    success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0

    return {
        "total_actions": total_actions,
        "successful": successful_actions,
        "failed": failed_actions,
        "success_rate": round(success_rate, 1),
        "action_breakdown": action_types,
    }


def _generate_insights(briefing_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate key insights and recommendations"""
    insights = {
        "highlights": [],
        "concerns": [],
        "recommendations": [],
    }

    # Accounting insights
    if "accounting" in briefing_data and "revenue" in briefing_data["accounting"]:
        accounting = briefing_data["accounting"]
        revenue = accounting.get("revenue", 0)
        expenses = accounting.get("expenses", 0)
        cash_flow = accounting.get("cash_flow", 0)

        if cash_flow > 0:
            insights["highlights"].append(
                f"Positive cash flow of ${cash_flow:,.2f} this week"
            )
        else:
            insights["concerns"].append(
                f"Negative cash flow of ${abs(cash_flow):,.2f} - review expenses"
            )

        if revenue > 0:
            insights["highlights"].append(
                f"Generated ${revenue:,.2f} in revenue"
            )

    # Social media insights
    if "social_media" in briefing_data and "total_posts" in briefing_data["social_media"]:
        social = briefing_data["social_media"]
        total_posts = social.get("total_posts", 0)
        avg_engagement = social.get("avg_engagement_rate", 0)

        if total_posts > 0:
            insights["highlights"].append(
                f"Published {total_posts} social media posts"
            )

        if avg_engagement < 0.01:
            insights["concerns"].append(
                "Low social media engagement rate - review content strategy"
            )
            insights["recommendations"].append(
                "Increase posting frequency and experiment with different content types"
            )

    # Task completion insights
    if "tasks" in briefing_data and "completion_rate" in briefing_data["tasks"]:
        tasks = briefing_data["tasks"]
        completion_rate = tasks.get("completion_rate", 0)
        pending = tasks.get("pending", 0)

        if completion_rate >= 80:
            insights["highlights"].append(
                f"High task completion rate: {completion_rate}%"
            )
        elif completion_rate < 50:
            insights["concerns"].append(
                f"Low task completion rate: {completion_rate}%"
            )

        if pending > 10:
            insights["concerns"].append(
                f"{pending} tasks pending - prioritize high-value items"
            )

    # Audit insights
    if "audit" in briefing_data and "success_rate" in briefing_data["audit"]:
        audit = briefing_data["audit"]
        success_rate = audit.get("success_rate", 0)

        if success_rate >= 95:
            insights["highlights"].append(
                f"Excellent system reliability: {success_rate}% success rate"
            )
        elif success_rate < 80:
            insights["concerns"].append(
                f"System reliability concerns: {success_rate}% success rate"
            )
            insights["recommendations"].append(
                "Review error logs and improve error handling"
            )

    # Default recommendations if none generated
    if not insights["recommendations"]:
        insights["recommendations"].append(
            "Continue monitoring key metrics and maintain current performance"
        )

    return insights


def _generate_markdown_report(briefing_data: Dict[str, Any]) -> str:
    """Generate markdown report file"""
    period = briefing_data["period"]
    week_num = period["week_number"]
    year = period["year"]

    # Create report filename
    report_filename = f"CEO_Briefing_Week_{week_num}_{year}.md"
    report_path = Path("Done") / report_filename

    # Generate markdown content
    content = f"""# 📊 CEO Weekly Briefing - Week {week_num}, {year}

**Period:** {period['start'][:10]} to {period['end'][:10]}
**Generated:** {briefing_data['generated_at'][:19]}

---

## 💰 Financial Summary

"""

    # Accounting section
    if "accounting" in briefing_data and "revenue" in briefing_data["accounting"]:
        accounting = briefing_data["accounting"]
        content += f"""
| Metric | Amount |
|--------|--------|
| Revenue | ${accounting.get('revenue', 0):,.2f} |
| Expenses | ${accounting.get('expenses', 0):,.2f} |
| Cash Flow | ${accounting.get('cash_flow', 0):,.2f} |
| Outstanding Invoices | ${accounting.get('outstanding_invoices', 0):,.2f} |
"""
    else:
        content += "\n⚠️ Accounting data unavailable\n"

    # Social media section
    content += "\n---\n\n## 📱 Social Media Performance\n\n"

    if "social_media" in briefing_data and "total_posts" in briefing_data["social_media"]:
        social = briefing_data["social_media"]
        content += f"""
| Metric | Value |
|--------|-------|
| Total Posts | {social.get('total_posts', 0)} |
| Total Reach | {social.get('total_engagement', {}).get('reach', 0):,} |
| Total Likes | {social.get('total_engagement', {}).get('likes', 0):,} |
| Avg Engagement Rate | {social.get('avg_engagement_rate', 0):.2%} |

### Platform Breakdown

"""
        platform_breakdown = social.get("platform_breakdown", {})
        for platform, metrics in platform_breakdown.items():
            if metrics.get("posts", 0) > 0:
                content += f"- **{platform.title()}**: {metrics['posts']} posts, {metrics['reach']:,} reach\n"
    else:
        content += "\n⚠️ Social media data unavailable\n"

    # Task completion section
    content += "\n---\n\n## ✅ Task Completion\n\n"

    if "tasks" in briefing_data and "completion_rate" in briefing_data["tasks"]:
        tasks = briefing_data["tasks"]
        content += f"""
| Metric | Value |
|--------|-------|
| Completed | {tasks.get('completed', 0)} |
| Pending | {tasks.get('pending', 0)} |
| Completion Rate | {tasks.get('completion_rate', 0)}% |
"""
    else:
        content += "\n⚠️ Task statistics unavailable\n"

    # Audit section
    content += "\n---\n\n## 🔍 System Audit\n\n"

    if "audit" in briefing_data and "success_rate" in briefing_data["audit"]:
        audit = briefing_data["audit"]
        content += f"""
| Metric | Value |
|--------|-------|
| Total Actions | {audit.get('total_actions', 0):,} |
| Successful | {audit.get('successful', 0):,} |
| Failed | {audit.get('failed', 0):,} |
| Success Rate | {audit.get('success_rate', 0)}% |
"""
    else:
        content += "\n⚠️ Audit data unavailable\n"

    # Insights section
    content += "\n---\n\n## 💡 Key Insights\n\n"

    insights = briefing_data.get("insights", {})

    if insights.get("highlights"):
        content += "### ✅ Highlights\n\n"
        for highlight in insights["highlights"]:
            content += f"- {highlight}\n"

    if insights.get("concerns"):
        content += "\n### ⚠️ Concerns\n\n"
        for concern in insights["concerns"]:
            content += f"- {concern}\n"

    if insights.get("recommendations"):
        content += "\n### 🎯 Recommendations\n\n"
        for recommendation in insights["recommendations"]:
            content += f"- {recommendation}\n"

    content += "\n---\n\n**Report generated by Sana AI Employee (Gold Tier)**\n"

    # Write report to file
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(report_path)
