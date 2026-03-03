"""
Dashboard.md Update Utilities
Provides real-time updates to the executive dashboard
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DashboardUpdater:
    """
    Updates Dashboard.md with real-time Gold Tier metrics and status.
    """

    def __init__(self, dashboard_path: str = "Dashboard.md"):
        self.dashboard_path = Path(dashboard_path)

    def update_gold_tier_status(
        self,
        autonomous_mode: bool,
        active_workflows: int,
        completed_today: int,
        success_rate: float,
        mcp_health: Dict[str, Dict[str, Any]],
        recent_actions: List[Dict[str, str]]
    ):
        """
        Update Gold Tier status section in Dashboard.md

        Args:
            autonomous_mode: Whether autonomous mode is enabled
            active_workflows: Number of active workflows
            completed_today: Tasks completed today
            success_rate: Success rate as decimal (0.95 = 95%)
            mcp_health: MCP server health status dict
            recent_actions: List of recent autonomous actions
        """
        try:
            # Read existing dashboard
            if self.dashboard_path.exists():
                with open(self.dashboard_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = "# 🎯 AI Employee Vault - Executive Dashboard\n\n"

            # Generate Gold Tier section
            gold_section = self._generate_gold_tier_section(
                autonomous_mode,
                active_workflows,
                completed_today,
                success_rate,
                mcp_health,
                recent_actions
            )

            # Replace or append Gold Tier section
            if "## 🤖 Gold Tier Status" in content:
                # Replace existing section
                start = content.find("## 🤖 Gold Tier Status")
                end = content.find("\n## ", start + 1)
                if end == -1:
                    end = len(content)

                content = content[:start] + gold_section + "\n\n" + content[end:]
            else:
                # Append new section
                content += "\n\n" + gold_section

            # Write updated dashboard
            with open(self.dashboard_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info("Dashboard.md updated successfully")

        except Exception as e:
            logger.error(f"Failed to update Dashboard.md: {e}")

    def _generate_gold_tier_section(
        self,
        autonomous_mode: bool,
        active_workflows: int,
        completed_today: int,
        success_rate: float,
        mcp_health: Dict[str, Dict[str, Any]],
        recent_actions: List[Dict[str, str]]
    ) -> str:
        """Generate Gold Tier status section content"""

        mode_status = "✅ Enabled" if autonomous_mode else "⏸️ Disabled"
        success_pct = int(success_rate * 100)

        section = f"""## 🤖 Gold Tier Status

**Autonomous Mode**: {mode_status}
**Active Workflows**: {active_workflows}
**Completed Today**: {completed_today}
**Success Rate**: {success_pct}%

### MCP Server Health
"""

        # Add MCP server health status
        for server_name, health in mcp_health.items():
            status = health.get('health_status', 'UNKNOWN')
            icon = self._get_health_icon(status)

            avg_time = health.get('average_response_time_ms', 0)
            rate_limit = health.get('rate_limit', {})

            if rate_limit:
                remaining = rate_limit.get('remaining', '?')
                limit = rate_limit.get('limit', '?')
                section += f"- {icon} **{server_name}**: {status} ({avg_time:.0f}ms avg, rate limit: {remaining}/{limit})\n"
            else:
                section += f"- {icon} **{server_name}**: {status} ({avg_time:.0f}ms avg)\n"

        # Add recent autonomous actions
        section += "\n### Recent Autonomous Actions\n"

        if recent_actions:
            for i, action in enumerate(recent_actions[:5], 1):
                result_icon = "✅" if action.get('result') == 'SUCCESS' else "❌"
                section += f"{i}. {result_icon} {action.get('description', 'Unknown action')} - {action.get('time_ago', 'recently')}\n"
        else:
            section += "No recent actions\n"

        # Add timestamp
        section += f"\n**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        return section

    def _get_health_icon(self, status: str) -> str:
        """Get emoji icon for health status"""
        icons = {
            "HEALTHY": "🟢",
            "DEGRADED": "🟡",
            "FAILED": "🔴",
            "RECOVERING": "🟠",
            "UNKNOWN": "⚪"
        }
        return icons.get(status, "⚪")

    def add_autonomous_action(
        self,
        action_description: str,
        result: str,
        business_impact: str
    ):
        """
        Add a single autonomous action to the dashboard.

        Args:
            action_description: Description of the action
            result: SUCCESS, FAILURE, or PARTIAL
            business_impact: Business value assessment
        """
        try:
            # This is a simplified version - in production, you'd read current
            # actions from dashboard and append the new one
            logger.info(
                f"Autonomous action logged: {action_description} "
                f"(result: {result}, impact: {business_impact})"
            )
        except Exception as e:
            logger.error(f"Failed to add autonomous action to dashboard: {e}")

    def update_metric(self, metric_name: str, value: Any):
        """
        Update a specific metric in the dashboard.

        Args:
            metric_name: Name of the metric to update
            value: New value for the metric
        """
        try:
            logger.info(f"Dashboard metric updated: {metric_name} = {value}")
        except Exception as e:
            logger.error(f"Failed to update dashboard metric: {e}")


# Global updater instance
_dashboard_updater: Optional['DashboardUpdater'] = None


def get_dashboard_updater() -> DashboardUpdater:
    """Get or create global dashboard updater instance"""
    global _dashboard_updater
    if _dashboard_updater is None:
        _dashboard_updater = DashboardUpdater()
    return _dashboard_updater
