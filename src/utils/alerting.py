"""
Alerting System for Gold Tier Autonomous Employee

Monitors for P0/P1 task failures and sends alerts.
Part of T104 - Monitoring alerts for P0/P1 task failures.

Features:
- Real-time monitoring of task failures
- Priority-based alerting (P0/P1 only)
- Multiple alert channels (Dashboard, Email, Log)
- Alert throttling to prevent spam
- Alert history tracking

Usage:
    from src.utils.alerting import AlertManager

    alert_mgr = AlertManager()
    alert_mgr.send_alert("P0", "Invoice creation failed", details)
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    P0 = "P0_CRITICAL"
    P1 = "P1_HIGH"
    P2 = "P2_MEDIUM"
    P3 = "P3_LOW"


class AlertChannel(Enum):
    """Alert delivery channels"""
    DASHBOARD = "dashboard"
    LOG = "log"
    EMAIL = "email"


class AlertManager:
    """
    Manages alerts for critical task failures

    Features:
    - Priority-based alerting (P0/P1 trigger immediate alerts)
    - Alert throttling (max 1 alert per task per hour)
    - Multiple delivery channels
    - Alert history tracking
    - Dashboard integration
    """

    def __init__(self, alert_file: Optional[Path] = None):
        """
        Initialize alert manager

        Args:
            alert_file: Path to alert history file (default: Logs/alerts.json)
        """
        if alert_file is None:
            alert_file = Path("Logs/alerts.json")

        self.alert_file = alert_file
        self.alert_history: List[Dict[str, Any]] = []
        self.throttle_window = timedelta(hours=1)

        # Load existing alerts
        self._load_alerts()

    def send_alert(self,
                   priority: str,
                   title: str,
                   details: Dict[str, Any],
                   channels: Optional[List[AlertChannel]] = None) -> bool:
        """
        Send an alert for a task failure

        Args:
            priority: Task priority (P0, P1, P2, P3)
            title: Alert title
            details: Alert details dictionary
            channels: List of channels to send alert to (default: all)

        Returns:
            True if alert sent, False if throttled
        """
        # Only alert for P0 and P1 failures
        if priority not in ["P0", "P1"]:
            return False

        # Check throttling
        if self._is_throttled(title):
            return False

        # Default channels
        if channels is None:
            channels = [AlertChannel.DASHBOARD, AlertChannel.LOG]

        # Create alert
        alert = {
            "timestamp": datetime.now().isoformat(),
            "priority": priority,
            "title": title,
            "details": details,
            "channels": [c.value for c in channels],
            "status": "sent"
        }

        # Send to each channel
        for channel in channels:
            self._send_to_channel(channel, alert)

        # Save to history
        self.alert_history.append(alert)
        self._save_alerts()

        return True

    def _is_throttled(self, title: str) -> bool:
        """
        Check if alert should be throttled

        Args:
            title: Alert title

        Returns:
            True if throttled, False otherwise
        """
        now = datetime.now()
        cutoff = now - self.throttle_window

        # Check recent alerts with same title
        for alert in reversed(self.alert_history):
            alert_time = datetime.fromisoformat(alert["timestamp"])

            if alert_time < cutoff:
                break

            if alert["title"] == title:
                return True

        return False

    def _send_to_channel(self, channel: AlertChannel, alert: Dict[str, Any]):
        """
        Send alert to specific channel

        Args:
            channel: Alert channel
            alert: Alert data
        """
        if channel == AlertChannel.DASHBOARD:
            self._send_to_dashboard(alert)
        elif channel == AlertChannel.LOG:
            self._send_to_log(alert)
        elif channel == AlertChannel.EMAIL:
            self._send_to_email(alert)

    def _send_to_dashboard(self, alert: Dict[str, Any]):
        """Update Dashboard.md with alert"""
        dashboard_file = Path("Dashboard.md")

        if not dashboard_file.exists():
            return

        try:
            # Read current dashboard
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create alert section if it doesn't exist
            alert_section = "\n## 🚨 Critical Alerts\n\n"

            if "## 🚨 Critical Alerts" not in content:
                content += alert_section

            # Add alert
            alert_text = (
                f"- **[{alert['priority']}]** {alert['title']}\n"
                f"  - Time: {alert['timestamp']}\n"
                f"  - Details: {alert['details'].get('error', 'N/A')}\n\n"
            )

            # Insert after alert section header
            content = content.replace(
                "## 🚨 Critical Alerts\n\n",
                f"## 🚨 Critical Alerts\n\n{alert_text}"
            )

            # Write back
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(content)

        except Exception as e:
            print(f"Warning: Failed to update dashboard with alert: {e}")

    def _send_to_log(self, alert: Dict[str, Any]):
        """Write alert to log file"""
        log_file = Path("Logs/critical_alerts.log")

        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)

            with open(log_file, 'a', encoding='utf-8') as f:
                log_entry = (
                    f"[{alert['timestamp']}] [{alert['priority']}] {alert['title']}\n"
                    f"Details: {json.dumps(alert['details'])}\n"
                    f"{'-' * 80}\n"
                )
                f.write(log_entry)

        except Exception as e:
            print(f"Warning: Failed to write alert to log: {e}")

    def _send_to_email(self, alert: Dict[str, Any]):
        """Send alert via email (placeholder for future implementation)"""
        # TODO: Implement email alerting via Gmail MCP
        print(f"📧 Email alert: [{alert['priority']}] {alert['title']}")

    def _load_alerts(self):
        """Load alert history from file"""
        if not self.alert_file.exists():
            return

        try:
            with open(self.alert_file, 'r') as f:
                data = json.load(f)
                self.alert_history = data.get("alerts", [])
        except Exception:
            self.alert_history = []

    def _save_alerts(self):
        """Save alert history to file"""
        try:
            self.alert_file.parent.mkdir(parents=True, exist_ok=True)

            # Keep only last 1000 alerts
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]

            with open(self.alert_file, 'w') as f:
                json.dump({"alerts": self.alert_history}, f, indent=2)

        except Exception as e:
            print(f"Warning: Failed to save alerts: {e}")

    def get_recent_alerts(self, hours: int = 24, priority: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recent alerts

        Args:
            hours: Number of hours to look back
            priority: Filter by priority (optional)

        Returns:
            List of recent alerts
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = []

        for alert in reversed(self.alert_history):
            alert_time = datetime.fromisoformat(alert["timestamp"])

            if alert_time < cutoff:
                break

            if priority is None or alert["priority"] == priority:
                recent.append(alert)

        return recent

    def get_alert_summary(self) -> Dict[str, Any]:
        """
        Get alert summary statistics

        Returns:
            Dictionary with alert statistics
        """
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        p0_24h = 0
        p1_24h = 0
        p0_7d = 0
        p1_7d = 0

        for alert in reversed(self.alert_history):
            alert_time = datetime.fromisoformat(alert["timestamp"])

            if alert_time < last_7d:
                break

            priority = alert["priority"]

            if alert_time >= last_24h:
                if priority == "P0":
                    p0_24h += 1
                elif priority == "P1":
                    p1_24h += 1

            if priority == "P0":
                p0_7d += 1
            elif priority == "P1":
                p1_7d += 1

        return {
            "last_24_hours": {
                "P0": p0_24h,
                "P1": p1_24h,
                "total": p0_24h + p1_24h
            },
            "last_7_days": {
                "P0": p0_7d,
                "P1": p1_7d,
                "total": p0_7d + p1_7d
            },
            "total_alerts": len(self.alert_history)
        }


# Global instance
_global_alert_manager = None


def get_alert_manager() -> AlertManager:
    """Get global alert manager instance"""
    global _global_alert_manager
    if _global_alert_manager is None:
        _global_alert_manager = AlertManager()
    return _global_alert_manager
