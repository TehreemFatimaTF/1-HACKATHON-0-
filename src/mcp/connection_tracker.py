"""
MCP Server Connection Health Tracker
Monitors and tracks health status of all MCP server connections
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ServerName(Enum):
    """Known MCP servers"""
    ODOO = "ODOO"
    GMAIL = "GMAIL"
    LINKEDIN = "LINKEDIN"
    TWITTER = "TWITTER"
    FACEBOOK = "FACEBOOK"
    INSTAGRAM = "INSTAGRAM"


class ConnectionTracker:
    """
    Tracks health and status of all MCP server connections.
    Maintains persistent state in Memory/mcp_connections.json
    """

    def __init__(self, state_file: str = "Memory/mcp_connections.json"):
        self.state_file = Path(state_file)
        self.connections: Dict[str, Dict[str, Any]] = {}
        self._load_state()

    def _load_state(self):
        """Load connection state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.connections = json.load(f)
                logger.info(f"Loaded connection state for {len(self.connections)} servers")
            except Exception as e:
                logger.error(f"Failed to load connection state: {e}")
                self.connections = {}
        else:
            self.connections = {}

    def _save_state(self):
        """Save connection state to file"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.connections, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save connection state: {e}")

    def update_connection(
        self,
        server_name: str,
        health_status: str,
        auth_state: str,
        last_success: Optional[float] = None,
        last_failure: Optional[float] = None,
        consecutive_failures: int = 0,
        total_calls: int = 0,
        successful_calls: int = 0,
        failed_calls: int = 0,
        success_rate: float = 0.0,
        average_response_time: float = 0.0,
        circuit_breaker_state: str = "CLOSED",
        rate_limit_info: Optional[Dict[str, Any]] = None
    ):
        """
        Update connection status for a server.

        Args:
            server_name: Name of the MCP server
            health_status: HEALTHY, DEGRADED, FAILED, RECOVERING, UNKNOWN
            auth_state: AUTHENTICATED, UNAUTHENTICATED, EXPIRED, INVALID
            last_success: Timestamp of last successful call
            last_failure: Timestamp of last failed call
            consecutive_failures: Count of consecutive failures
            total_calls: Total API calls made
            successful_calls: Count of successful calls
            failed_calls: Count of failed calls
            success_rate: Success rate (0.0 to 1.0)
            average_response_time: Average response time in milliseconds
            circuit_breaker_state: CLOSED, OPEN, HALF_OPEN
            rate_limit_info: Platform-specific rate limit data
        """
        self.connections[server_name] = {
            "server_name": server_name,
            "health_status": health_status,
            "auth_state": auth_state,
            "last_success": last_success,
            "last_failure": last_failure,
            "consecutive_failures": consecutive_failures,
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": success_rate,
            "average_response_time_ms": average_response_time,
            "circuit_breaker_state": circuit_breaker_state,
            "rate_limit_info": rate_limit_info or {},
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }

        self._save_state()
        logger.info(f"Updated connection status for {server_name}: {health_status}")

    def get_connection(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get connection status for a specific server"""
        return self.connections.get(server_name)

    def get_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all connections"""
        return self.connections.copy()

    def get_healthy_servers(self) -> list[str]:
        """Get list of healthy server names"""
        return [
            name for name, conn in self.connections.items()
            if conn.get('health_status') == 'HEALTHY'
        ]

    def get_failed_servers(self) -> list[str]:
        """Get list of failed server names"""
        return [
            name for name, conn in self.connections.items()
            if conn.get('health_status') == 'FAILED'
        ]

    def get_degraded_servers(self) -> list[str]:
        """Get list of degraded server names"""
        return [
            name for name, conn in self.connections.items()
            if conn.get('health_status') == 'DEGRADED'
        ]

    def is_server_healthy(self, server_name: str) -> bool:
        """Check if a specific server is healthy"""
        conn = self.get_connection(server_name)
        if not conn:
            return False
        return conn.get('health_status') == 'HEALTHY'

    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall health summary of all connections"""
        if not self.connections:
            return {
                "status": "UNKNOWN",
                "total_servers": 0,
                "healthy": 0,
                "degraded": 0,
                "failed": 0,
                "unknown": 0
            }

        healthy = len(self.get_healthy_servers())
        degraded = len(self.get_degraded_servers())
        failed = len(self.get_failed_servers())
        total = len(self.connections)
        unknown = total - (healthy + degraded + failed)

        # Determine overall status
        if failed > 0:
            overall_status = "DEGRADED"
        elif degraded > 0:
            overall_status = "DEGRADED"
        elif healthy == total:
            overall_status = "HEALTHY"
        else:
            overall_status = "UNKNOWN"

        return {
            "status": overall_status,
            "total_servers": total,
            "healthy": healthy,
            "degraded": degraded,
            "failed": failed,
            "unknown": unknown,
            "health_percentage": (healthy / total * 100) if total > 0 else 0
        }

    def reset_connection(self, server_name: str):
        """Reset connection state for a server"""
        if server_name in self.connections:
            self.connections[server_name] = {
                "server_name": server_name,
                "health_status": "UNKNOWN",
                "auth_state": "UNAUTHENTICATED",
                "last_success": None,
                "last_failure": None,
                "consecutive_failures": 0,
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "success_rate": 0.0,
                "average_response_time_ms": 0.0,
                "circuit_breaker_state": "CLOSED",
                "rate_limit_info": {},
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }
            self._save_state()
            logger.info(f"Reset connection state for {server_name}")


# Global tracker instance
_connection_tracker: Optional[ConnectionTracker] = None


def get_connection_tracker() -> ConnectionTracker:
    """Get or create global connection tracker instance"""
    global _connection_tracker
    if _connection_tracker is None:
        _connection_tracker = ConnectionTracker()
    return _connection_tracker
