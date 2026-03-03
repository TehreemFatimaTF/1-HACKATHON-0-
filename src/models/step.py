"""
Step schema for workflow execution in Gold Tier autonomous tasks
Represents a single step in a multi-step workflow
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional


class StepStatus(str, Enum):
    """Step execution status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class StepSchema:
    """
    Represents a single step in a multi-step workflow

    Attributes:
        step_number: Sequential step index (0-based)
        action: Action name (e.g., "detect_trend", "create_post", "log_expense")
        status: Current execution status
        input: Input parameters for this step
        output: Result data from this step
        error: Error message if step failed
        started_at: Step start timestamp
        completed_at: Step completion timestamp
        retry_count: Number of retry attempts
    """
    step_number: int
    action: str
    status: StepStatus = StepStatus.PENDING
    input: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary for JSON serialization"""
        return {
            "step_number": self.step_number,
            "action": self.action,
            "status": self.status.value,
            "input": self.input,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StepSchema":
        """Create step from dictionary"""
        return cls(
            step_number=data["step_number"],
            action=data["action"],
            status=StepStatus(data["status"]),
            input=data.get("input", {}),
            output=data.get("output", {}),
            error=data.get("error"),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            retry_count=data.get("retry_count", 0),
        )

    def start(self) -> None:
        """Mark step as started"""
        self.status = StepStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()

    def complete(self, output: Dict[str, Any]) -> None:
        """Mark step as successfully completed"""
        self.status = StepStatus.SUCCESS
        self.output = output
        self.completed_at = datetime.utcnow()

    def fail(self, error: str) -> None:
        """Mark step as failed"""
        self.status = StepStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()

    def skip(self, reason: str) -> None:
        """Mark step as skipped"""
        self.status = StepStatus.SKIPPED
        self.error = reason
        self.completed_at = datetime.utcnow()

    def increment_retry(self) -> None:
        """Increment retry counter"""
        self.retry_count += 1

    def can_retry(self, max_retries: int = 3) -> bool:
        """
        Check if step can be retried

        Args:
            max_retries: Maximum number of retry attempts allowed

        Returns:
            True if retry count is below max_retries
        """
        return self.retry_count < max_retries

    def reset_for_retry(self) -> None:
        """Reset step state for retry attempt"""
        self.status = StepStatus.PENDING
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.increment_retry()
