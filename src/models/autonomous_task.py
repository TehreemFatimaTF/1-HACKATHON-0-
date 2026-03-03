"""
AutonomousTask model for Gold Tier multi-step workflow execution
Represents a workflow with state tracking for autonomous execution
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import json


class OutcomeStatus(str, Enum):
    """Task outcome status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"


class StepStatus(str, Enum):
    """Step execution status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class Priority(str, Enum):
    """4-Tier Priority Matrix"""
    P0 = "P0"  # Critical/Revenue
    P1 = "P1"  # Client Retention
    P2 = "P2"  # Operational
    P3 = "P3"  # General/Growth


@dataclass
class Step:
    """
    Represents a single step in a multi-step workflow
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
    def from_dict(cls, data: Dict[str, Any]) -> "Step":
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


@dataclass
class AutonomousTask:
    """
    Represents a multi-step workflow with state tracking for autonomous execution

    Validation Rules:
    - task_id must be unique
    - current_step must be < total_steps
    - completed_steps.length + pending_steps.length must equal total_steps
    - outcome_status transitions: PENDING → IN_PROGRESS → (COMPLETED | FAILED | PAUSED)
    """
    workflow_name: str
    original_intent: str
    total_steps: int
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_step: int = 0
    completed_steps: List[Step] = field(default_factory=list)
    pending_steps: List[Step] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    outcome_status: OutcomeStatus = OutcomeStatus.PENDING
    priority: Priority = Priority.P2
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate task after initialization"""
        self.validate()

    def validate(self) -> None:
        """
        Validate task state according to business rules

        Raises:
            ValueError: If validation fails
        """
        if self.current_step >= self.total_steps:
            raise ValueError(f"current_step ({self.current_step}) must be < total_steps ({self.total_steps})")

        total_defined_steps = len(self.completed_steps) + len(self.pending_steps)
        if total_defined_steps > 0 and total_defined_steps != self.total_steps:
            raise ValueError(
                f"completed_steps ({len(self.completed_steps)}) + pending_steps ({len(self.pending_steps)}) "
                f"must equal total_steps ({self.total_steps})"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization"""
        return {
            "task_id": self.task_id,
            "workflow_name": self.workflow_name,
            "original_intent": self.original_intent,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "completed_steps": [step.to_dict() for step in self.completed_steps],
            "pending_steps": [step.to_dict() for step in self.pending_steps],
            "context": self.context,
            "outcome_status": self.outcome_status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AutonomousTask":
        """Create task from dictionary"""
        return cls(
            task_id=data["task_id"],
            workflow_name=data["workflow_name"],
            original_intent=data["original_intent"],
            current_step=data["current_step"],
            total_steps=data["total_steps"],
            completed_steps=[Step.from_dict(s) for s in data.get("completed_steps", [])],
            pending_steps=[Step.from_dict(s) for s in data.get("pending_steps", [])],
            context=data.get("context", {}),
            outcome_status=OutcomeStatus(data["outcome_status"]),
            priority=Priority(data["priority"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
        )

    def save(self, directory: str = "Needs_Action") -> str:
        """
        Save task state to JSON file

        Args:
            directory: Directory to save task file (default: Needs_Action)

        Returns:
            Path to saved file
        """
        import os

        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"state_{self.task_id}.json")

        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        return filepath

    @classmethod
    def load(cls, task_id: str, directory: str = "Needs_Action") -> "AutonomousTask":
        """
        Load task state from JSON file

        Args:
            task_id: Task ID to load
            directory: Directory containing task file (default: Needs_Action)

        Returns:
            Loaded AutonomousTask instance
        """
        import os

        filepath = os.path.join(directory, f"state_{task_id}.json")

        with open(filepath, "r") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def has_next_step(self) -> bool:
        """
        Check if there is a next step to execute (Ralph Wiggum Loop check)

        Returns:
            True if more steps remain, False if at final step
        """
        return self.current_step < self.total_steps - 1

    def get_current_step(self) -> Optional[Step]:
        """
        Get the current step to execute

        Returns:
            Current Step or None if no pending steps
        """
        if self.pending_steps:
            return self.pending_steps[0]
        return None

    def advance_step(self) -> None:
        """
        Move to the next step in the workflow

        Raises:
            ValueError: If no more steps available
        """
        if not self.pending_steps:
            raise ValueError("No pending steps to advance to")

        # Move current step from pending to completed
        current = self.pending_steps.pop(0)
        self.completed_steps.append(current)

        # Increment step counter
        self.current_step += 1
        self.updated_at = datetime.utcnow()

        # Update status
        if self.current_step >= self.total_steps:
            # All steps completed, but outcome not yet verified
            self.outcome_status = OutcomeStatus.IN_PROGRESS
        elif self.outcome_status == OutcomeStatus.PENDING:
            self.outcome_status = OutcomeStatus.IN_PROGRESS

    def mark_completed(self) -> None:
        """Mark task as successfully completed"""
        self.outcome_status = OutcomeStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_failed(self, reason: str) -> None:
        """Mark task as failed"""
        self.outcome_status = OutcomeStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.context["failure_reason"] = reason

    def mark_paused(self, reason: str) -> None:
        """Mark task as paused (requires human input)"""
        self.outcome_status = OutcomeStatus.PAUSED
        self.updated_at = datetime.utcnow()
        self.context["pause_reason"] = reason

    def resume(self) -> None:
        """Resume a paused task"""
        if self.outcome_status != OutcomeStatus.PAUSED:
            raise ValueError(f"Cannot resume task with status {self.outcome_status}")

        self.outcome_status = OutcomeStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()
        if "pause_reason" in self.context:
            del self.context["pause_reason"]

    def update_context(self, key: str, value: Any) -> None:
        """
        Update workflow context data (preserved across steps)

        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
        self.updated_at = datetime.utcnow()

    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get workflow context data

        Args:
            key: Context key
            default: Default value if key not found

        Returns:
            Context value or default
        """
        return self.context.get(key, default)
