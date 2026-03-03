"""
Multi-Agent Base Class for Platinum Tier
Provides foundation for specialized AI agents
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class AgentStatus(Enum):
    """Agent operational status"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class AgentCapability(Enum):
    """Agent capabilities"""
    EMAIL_PROCESSING = "email_processing"
    SOCIAL_MEDIA = "social_media"
    ANALYTICS = "analytics"
    ACCOUNTING = "accounting"
    COORDINATION = "coordination"
    LEARNING = "learning"


class BaseAgent:
    """
    Base class for all AI agents in the system.
    Each agent is specialized for specific tasks.
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "BaseAgent",
        specialization: str = "general",
        capabilities: List[AgentCapability] = None
    ):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name
        self.specialization = specialization
        self.capabilities = capabilities or []
        self.status = AgentStatus.IDLE
        self.task_queue: List[Dict] = []
        self.completed_tasks: List[Dict] = []
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_completion_time": 0,
            "success_rate": 0
        }
        self.created_at = datetime.now()
        self.last_active = datetime.now()

    def can_handle(self, task: Dict) -> bool:
        """
        Check if agent can handle the given task

        Args:
            task: Task dictionary with type and requirements

        Returns:
            bool: True if agent can handle task
        """
        task_type = task.get("type", "")
        required_capability = task.get("required_capability")

        if required_capability:
            return required_capability in self.capabilities

        # Default capability check based on specialization
        return self._matches_specialization(task_type)

    def _matches_specialization(self, task_type: str) -> bool:
        """Check if task type matches agent specialization"""
        specialization_map = {
            "email": AgentCapability.EMAIL_PROCESSING,
            "social_media": AgentCapability.SOCIAL_MEDIA,
            "analytics": AgentCapability.ANALYTICS,
            "accounting": AgentCapability.ACCOUNTING
        }

        required_cap = specialization_map.get(task_type)
        return required_cap in self.capabilities if required_cap else False

    def add_task(self, task: Dict) -> bool:
        """
        Add task to agent's queue

        Args:
            task: Task dictionary

        Returns:
            bool: True if task added successfully
        """
        if not self.can_handle(task):
            return False

        task["queued_at"] = datetime.now().isoformat()
        task["agent_id"] = self.agent_id
        self.task_queue.append(task)
        return True

    def execute_task(self, task: Dict) -> Dict:
        """
        Execute a task (to be overridden by specialized agents)

        Args:
            task: Task to execute

        Returns:
            Dict: Execution result
        """
        self.status = AgentStatus.BUSY
        self.last_active = datetime.now()

        try:
            # Base implementation - override in specialized agents
            result = self._execute_task_impl(task)

            # Record success
            self._record_completion(task, result, success=True)
            self.status = AgentStatus.IDLE

            return result

        except Exception as e:
            # Record failure
            error_result = {
                "success": False,
                "error": str(e),
                "task_id": task.get("task_id")
            }
            self._record_completion(task, error_result, success=False)
            self.status = AgentStatus.ERROR

            return error_result

    def _execute_task_impl(self, task: Dict) -> Dict:
        """
        Actual task execution logic (override in subclasses)

        Args:
            task: Task to execute

        Returns:
            Dict: Execution result
        """
        return {
            "success": True,
            "message": f"Task executed by {self.name}",
            "task_id": task.get("task_id")
        }

    def _record_completion(self, task: Dict, result: Dict, success: bool):
        """Record task completion and update metrics"""
        completion_record = {
            "task_id": task.get("task_id"),
            "task_type": task.get("type"),
            "completed_at": datetime.now().isoformat(),
            "success": success,
            "result": result,
            "execution_time": self._calculate_execution_time(task)
        }

        self.completed_tasks.append(completion_record)

        # Update metrics
        if success:
            self.metrics["tasks_completed"] += 1
        else:
            self.metrics["tasks_failed"] += 1

        self._update_metrics()

    def _calculate_execution_time(self, task: Dict) -> float:
        """Calculate task execution time in seconds"""
        queued_at = task.get("queued_at")
        if not queued_at:
            return 0

        queued_time = datetime.fromisoformat(queued_at)
        execution_time = (datetime.now() - queued_time).total_seconds()
        return execution_time

    def _update_metrics(self):
        """Update agent performance metrics"""
        total_tasks = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]

        if total_tasks > 0:
            self.metrics["success_rate"] = (
                self.metrics["tasks_completed"] / total_tasks * 100
            )

        # Calculate average completion time
        if self.completed_tasks:
            total_time = sum(
                task["execution_time"]
                for task in self.completed_tasks
                if task["success"]
            )
            successful_tasks = self.metrics["tasks_completed"]

            if successful_tasks > 0:
                self.metrics["average_completion_time"] = (
                    total_time / successful_tasks
                )

    def get_status(self) -> Dict:
        """
        Get agent status and metrics

        Returns:
            Dict: Agent status information
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specialization": self.specialization,
            "status": self.status.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "queue_length": len(self.task_queue),
            "metrics": self.metrics,
            "last_active": self.last_active.isoformat(),
            "uptime_hours": (datetime.now() - self.created_at).total_seconds() / 3600
        }

    def communicate(self, target_agent_id: str, message: Dict) -> bool:
        """
        Send message to another agent (via message bus)

        Args:
            target_agent_id: Target agent ID
            message: Message to send

        Returns:
            bool: True if message sent successfully
        """
        # This will be implemented via MessageBus
        # For now, just log the communication
        print(f"[{self.name}] Sending message to {target_agent_id}: {message}")
        return True

    def report_status(self) -> Dict:
        """
        Generate status report for monitoring

        Returns:
            Dict: Detailed status report
        """
        return {
            "agent_info": self.get_status(),
            "recent_tasks": self.completed_tasks[-5:],  # Last 5 tasks
            "current_queue": [
                {
                    "task_id": task.get("task_id"),
                    "type": task.get("type"),
                    "queued_at": task.get("queued_at")
                }
                for task in self.task_queue
            ]
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"id={self.agent_id[:8]}... "
            f"name={self.name} "
            f"status={self.status.value}>"
        )
