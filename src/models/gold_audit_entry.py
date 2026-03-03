"""
GoldAuditEntry model with hash chain for tamper-evident logging
Test ID: T083 [P] [US4] Create GoldAuditEntry model with hash chain
File: src/models/gold_audit_entry.py
"""
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ActionType(Enum):
    TASK_START = "TASK_START"
    TASK_COMPLETE = "TASK_COMPLETE"
    STEP_EXECUTE = "STEP_EXECUTE"
    MCP_CALL = "MCP_CALL"
    ERROR = "ERROR"
    DECISION = "DECISION"


class ExecutionResult(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL = "PARTIAL"
    SKIPPED = "SKIPPED"


@dataclass
class ErrorDetails:
    error_type: str
    error_message: str
    stack_trace: str
    recovery_attempted: bool
    recovery_result: str


@dataclass
class GoldAuditEntry:
    """
    Tamper-evident log record for all autonomous actions
    """
    entry_id: str
    timestamp: datetime
    action_type: ActionType
    action_name: str
    parameters: Dict[str, Any]
    decision_rationale: str
    execution_result: ExecutionResult
    result_data: Dict[str, Any]
    business_impact: str
    error_details: Optional[ErrorDetails] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    task_id: Optional[str] = None
    previous_entry_hash: Optional[str] = None
    entry_hash: Optional[str] = None

    def __post_init__(self):
        """Calculate the entry hash after initialization."""
        if self.entry_hash is None:
            self.entry_hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of this entry's content."""
        # Create a dictionary with all fields except the entry_hash itself
        content = {
            'entry_id': self.entry_id,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            'action_type': self.action_type.value if isinstance(self.action_type, ActionType) else self.action_type,
            'action_name': self.action_name,
            'parameters': self.parameters,
            'decision_rationale': self.decision_rationale,
            'execution_result': self.execution_result.value if isinstance(self.execution_result, ExecutionResult) else self.execution_result,
            'result_data': self.result_data,
            'business_impact': self.business_impact,
            'error_details': {
                'error_type': self.error_details.error_type,
                'error_message': self.error_details.error_message,
                'stack_trace': self.error_details.stack_trace,
                'recovery_attempted': self.error_details.recovery_attempted,
                'recovery_result': self.error_details.recovery_result
            } if self.error_details else None,
            'related_entity_type': self.related_entity_type,
            'related_entity_id': self.related_entity_id,
            'task_id': self.task_id,
            'previous_entry_hash': self.previous_entry_hash
        }

        content_json = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(content_json.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the audit entry to a dictionary for JSON serialization."""
        return {
            'entry_id': self.entry_id,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            'action_type': self.action_type.value if isinstance(self.action_type, ActionType) else self.action_type,
            'action_name': self.action_name,
            'parameters': self.parameters,
            'decision_rationale': self.decision_rationale,
            'execution_result': self.execution_result.value if isinstance(self.execution_result, ExecutionResult) else self.execution_result,
            'result_data': self.result_data,
            'business_impact': self.business_impact,
            'error_details': {
                'error_type': self.error_details.error_type,
                'error_message': self.error_details.error_message,
                'stack_trace': self.error_details.stack_trace,
                'recovery_attempted': self.error_details.recovery_attempted,
                'recovery_result': self.error_details.recovery_result
            } if self.error_details else None,
            'related_entity_type': self.related_entity_type,
            'related_entity_id': self.related_entity_id,
            'task_id': self.task_id,
            'previous_entry_hash': self.previous_entry_hash,
            'entry_hash': self.entry_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GoldAuditEntry':
        """Create an audit entry from a dictionary."""
        # Convert string timestamps back to datetime
        if isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])

        # Convert string enums back to enum objects
        data['action_type'] = ActionType(data['action_type']) if data['action_type'] else None
        data['execution_result'] = ExecutionResult(data['execution_result']) if data['execution_result'] else None

        # Handle error_details if present
        if data['error_details']:
            error_data = data['error_details']
            data['error_details'] = ErrorDetails(
                error_type=error_data['error_type'],
                error_message=error_data['error_message'],
                stack_trace=error_data['stack_trace'],
                recovery_attempted=error_data['recovery_attempted'],
                recovery_result=error_data['recovery_result']
            )

        return cls(**data)