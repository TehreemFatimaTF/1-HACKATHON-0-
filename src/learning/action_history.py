"""
Action History Tracker for Learning System (Platinum Tier)
Records and analyzes past actions for continuous improvement
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path
import sqlite3


class ActionHistory:
    """
    Tracks all actions and their outcomes for learning purposes.
    Enables the system to learn from past successes and failures.
    """

    def __init__(self, db_path: str = "Logs/action_history.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for action history"""
        Path(self.db_path).parent.mkdir(exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                action_data TEXT,
                outcome TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                execution_time REAL,
                timestamp TEXT NOT NULL,
                agent_id TEXT,
                metrics TEXT
            )
        """)

        conn.commit()
        conn.close()

    def record_action(
        self,
        action_type: str,
        action_data: Dict,
        outcome: Dict,
        success: bool,
        execution_time: float = 0,
        agent_id: str = None,
        metrics: Dict = None
    ) -> int:
        """
        Record an action and its outcome

        Args:
            action_type: Type of action (e.g., "email_send", "social_post")
            action_data: Action parameters
            outcome: Result of the action
            success: Whether action succeeded
            execution_time: Time taken to execute (seconds)
            agent_id: ID of agent that executed action
            metrics: Additional metrics

        Returns:
            int: Action record ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO actions
            (action_type, action_data, outcome, success, execution_time, timestamp, agent_id, metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            action_type,
            json.dumps(action_data),
            json.dumps(outcome),
            success,
            execution_time,
            datetime.now().isoformat(),
            agent_id,
            json.dumps(metrics) if metrics else None
        ))

        action_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return action_id

    def get_similar_actions(
        self,
        action_type: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get similar past actions

        Args:
            action_type: Type of action to find
            limit: Maximum number of results

        Returns:
            List[Dict]: Similar actions
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM actions
            WHERE action_type = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (action_type, limit))

        columns = [desc[0] for desc in cursor.description]
        results = []

        for row in cursor.fetchall():
            action = dict(zip(columns, row))
            # Parse JSON fields
            action['action_data'] = json.loads(action['action_data'])
            action['outcome'] = json.loads(action['outcome'])
            if action['metrics']:
                action['metrics'] = json.loads(action['metrics'])
            results.append(action)

        conn.close()
        return results

    def calculate_success_rate(
        self,
        action_type: str,
        time_window_days: int = 30
    ) -> float:
        """
        Calculate success rate for action type

        Args:
            action_type: Type of action
            time_window_days: Time window in days

        Returns:
            float: Success rate (0-100)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Calculate date threshold
        from datetime import timedelta
        threshold = (datetime.now() - timedelta(days=time_window_days)).isoformat()

        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
            FROM actions
            WHERE action_type = ? AND timestamp > ?
        """, (action_type, threshold))

        result = cursor.fetchone()
        conn.close()

        if result[0] == 0:
            return 0.0

        return (result[1] / result[0]) * 100

    def get_best_practices(self, action_type: str) -> Dict:
        """
        Get best practices based on successful actions

        Args:
            action_type: Type of action

        Returns:
            Dict: Best practices and recommendations
        """
        successful_actions = self.get_similar_actions(action_type, limit=50)
        successful_actions = [a for a in successful_actions if a['success']]

        if not successful_actions:
            return {
                "action_type": action_type,
                "best_practices": [],
                "average_execution_time": 0,
                "success_rate": 0
            }

        # Calculate average execution time
        avg_time = sum(a['execution_time'] for a in successful_actions) / len(successful_actions)

        # Extract common patterns
        best_practices = []

        # Analyze action data for patterns
        # (This is simplified - in production, use ML for pattern detection)
        if action_type == "email_send":
            best_practices.append("Keep subject lines under 50 characters")
            best_practices.append("Send emails during business hours")
        elif action_type == "social_post":
            best_practices.append("Include hashtags for better reach")
            best_practices.append("Post during peak engagement hours")

        return {
            "action_type": action_type,
            "best_practices": best_practices,
            "average_execution_time": avg_time,
            "success_rate": self.calculate_success_rate(action_type),
            "sample_size": len(successful_actions)
        }

    def get_action_trends(self, days: int = 7) -> Dict:
        """
        Get action trends over time

        Args:
            days: Number of days to analyze

        Returns:
            Dict: Trend analysis
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        from datetime import timedelta
        threshold = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT
                action_type,
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                AVG(execution_time) as avg_time
            FROM actions
            WHERE timestamp > ?
            GROUP BY action_type
        """, (threshold,))

        trends = {}
        for row in cursor.fetchall():
            action_type, total, successful, avg_time = row
            trends[action_type] = {
                "total_actions": total,
                "successful_actions": successful,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "average_execution_time": avg_time
            }

        conn.close()
        return trends

    def get_statistics(self) -> Dict:
        """
        Get overall statistics

        Returns:
            Dict: Statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                AVG(execution_time) as avg_time
            FROM actions
        """)

        result = cursor.fetchone()
        total, successful, avg_time = result

        cursor.execute("SELECT DISTINCT action_type FROM actions")
        action_types = [row[0] for row in cursor.fetchall()]

        conn.close()

        return {
            "total_actions": total,
            "successful_actions": successful,
            "failed_actions": total - successful,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "average_execution_time": avg_time or 0,
            "action_types": action_types
        }
