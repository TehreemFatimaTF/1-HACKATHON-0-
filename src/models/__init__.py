"""
Models package for Gold Tier Autonomous Employee
"""

from .autonomous_task import AutonomousTask, OutcomeStatus, Priority
from .step import StepSchema, StepStatus

# For backward compatibility, also export Step as alias to StepSchema
Step = StepSchema

__all__ = [
    "AutonomousTask",
    "OutcomeStatus",
    "Priority",
    "StepSchema",
    "Step",
    "StepStatus",
]
