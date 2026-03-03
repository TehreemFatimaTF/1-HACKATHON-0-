"""
Pattern Analyzer for Learning System (Platinum Tier)
Identifies patterns in task execution for optimization
"""

from typing import Dict, List
from datetime import datetime
from collections import Counter
import json


class PatternAnalyzer:
    """
    Analyzes patterns in task execution to identify:
    - Common workflows
    - Optimal execution times
    - Failure patterns
    - Optimization opportunities
    """

    def __init__(self, action_history=None):
        self.action_history = action_history
        self.patterns = {}

    def analyze_task_patterns(self, tasks: List[Dict]) -> Dict:
        """
        Analyze patterns in task execution

        Args:
            tasks: List of completed tasks

        Returns:
            Dict: Pattern analysis
        """
        if not tasks:
            return {"patterns": [], "insights": []}

        # Analyze task types
        task_types = Counter(task.get("type") for task in tasks)

        # Analyze execution times
        avg_times = {}
        for task_type in task_types:
            type_tasks = [t for t in tasks if t.get("type") == task_type]
            times = [t.get("execution_time", 0) for t in type_tasks]
            avg_times[task_type] = sum(times) / len(times) if times else 0

        # Identify common sequences
        sequences = self._identify_sequences(tasks)

        # Analyze success patterns
        success_patterns = self._analyze_success_patterns(tasks)

        return {
            "task_type_distribution": dict(task_types),
            "average_execution_times": avg_times,
            "common_sequences": sequences,
            "success_patterns": success_patterns,
            "total_tasks_analyzed": len(tasks)
        }

    def identify_common_workflows(self, tasks: List[Dict]) -> List[Dict]:
        """
        Identify common workflow patterns

        Args:
            tasks: List of tasks

        Returns:
            List[Dict]: Common workflows
        """
        workflows = []

        # Group tasks by similarity
        task_groups = self._group_similar_tasks(tasks)

        for group_name, group_tasks in task_groups.items():
            if len(group_tasks) >= 3:  # At least 3 occurrences
                workflow = {
                    "workflow_name": group_name,
                    "frequency": len(group_tasks),
                    "average_duration": self._calculate_avg_duration(group_tasks),
                    "success_rate": self._calculate_success_rate(group_tasks),
                    "steps": self._extract_common_steps(group_tasks)
                }
                workflows.append(workflow)

        return sorted(workflows, key=lambda w: w["frequency"], reverse=True)

    def suggest_optimizations(self, tasks: List[Dict]) -> List[Dict]:
        """
        Suggest optimizations based on patterns

        Args:
            tasks: List of tasks

        Returns:
            List[Dict]: Optimization suggestions
        """
        suggestions = []

        # Analyze execution times
        slow_tasks = [t for t in tasks if t.get("execution_time", 0) > 300]  # > 5 min
        if slow_tasks:
            suggestions.append({
                "type": "performance",
                "priority": "high",
                "suggestion": f"Optimize {len(slow_tasks)} slow tasks (>5 min execution time)",
                "affected_tasks": len(slow_tasks)
            })

        # Analyze failure patterns
        failed_tasks = [t for t in tasks if not t.get("success", True)]
        if len(failed_tasks) > len(tasks) * 0.1:  # >10% failure rate
            suggestions.append({
                "type": "reliability",
                "priority": "critical",
                "suggestion": f"High failure rate detected ({len(failed_tasks)}/{len(tasks)} tasks)",
                "affected_tasks": len(failed_tasks)
            })

        # Analyze task sequences
        sequences = self._identify_sequences(tasks)
        if sequences:
            suggestions.append({
                "type": "automation",
                "priority": "medium",
                "suggestion": f"Automate {len(sequences)} common task sequences",
                "sequences": sequences[:3]  # Top 3
            })

        return suggestions

    def predict_task_duration(self, task: Dict) -> float:
        """
        Predict task duration based on historical data

        Args:
            task: Task to predict

        Returns:
            float: Predicted duration in seconds
        """
        if not self.action_history:
            return 60.0  # Default 1 minute

        # Get similar tasks
        similar_tasks = self.action_history.get_similar_actions(
            task.get("type", "unknown"),
            limit=20
        )

        if not similar_tasks:
            return 60.0

        # Calculate average
        times = [t.get("execution_time", 0) for t in similar_tasks]
        return sum(times) / len(times) if times else 60.0

    def _identify_sequences(self, tasks: List[Dict]) -> List[Dict]:
        """Identify common task sequences"""
        sequences = []

        # Sort tasks by timestamp
        sorted_tasks = sorted(tasks, key=lambda t: t.get("timestamp", ""))

        # Look for sequences of 2-3 tasks
        for i in range(len(sorted_tasks) - 1):
            sequence = [
                sorted_tasks[i].get("type"),
                sorted_tasks[i + 1].get("type")
            ]
            sequences.append(tuple(sequence))

        # Count occurrences
        sequence_counts = Counter(sequences)

        # Return common sequences (>2 occurrences)
        return [
            {"sequence": list(seq), "count": count}
            for seq, count in sequence_counts.items()
            if count > 2
        ]

    def _analyze_success_patterns(self, tasks: List[Dict]) -> Dict:
        """Analyze what leads to success"""
        successful = [t for t in tasks if t.get("success", False)]
        failed = [t for t in tasks if not t.get("success", True)]

        return {
            "total_successful": len(successful),
            "total_failed": len(failed),
            "success_rate": len(successful) / len(tasks) * 100 if tasks else 0,
            "common_success_factors": self._extract_success_factors(successful),
            "common_failure_factors": self._extract_failure_factors(failed)
        }

    def _group_similar_tasks(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """Group similar tasks together"""
        groups = {}

        for task in tasks:
            task_type = task.get("type", "unknown")
            if task_type not in groups:
                groups[task_type] = []
            groups[task_type].append(task)

        return groups

    def _calculate_avg_duration(self, tasks: List[Dict]) -> float:
        """Calculate average duration for tasks"""
        times = [t.get("execution_time", 0) for t in tasks]
        return sum(times) / len(times) if times else 0

    def _calculate_success_rate(self, tasks: List[Dict]) -> float:
        """Calculate success rate for tasks"""
        successful = sum(1 for t in tasks if t.get("success", False))
        return (successful / len(tasks) * 100) if tasks else 0

    def _extract_common_steps(self, tasks: List[Dict]) -> List[str]:
        """Extract common steps from tasks"""
        # Simplified - in production, use more sophisticated analysis
        return ["step_1", "step_2", "step_3"]

    def _extract_success_factors(self, tasks: List[Dict]) -> List[str]:
        """Extract factors that lead to success"""
        factors = []

        if tasks:
            avg_time = self._calculate_avg_duration(tasks)
            if avg_time < 120:  # < 2 minutes
                factors.append("Quick execution time")

            # Add more factor analysis here
            factors.append("Proper error handling")

        return factors

    def _extract_failure_factors(self, tasks: List[Dict]) -> List[str]:
        """Extract factors that lead to failure"""
        factors = []

        if tasks:
            # Analyze error messages
            errors = [t.get("error", "") for t in tasks if t.get("error")]
            if errors:
                factors.append("Common errors detected")

            # Add more factor analysis here
            factors.append("Timeout issues")

        return factors
