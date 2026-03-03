"""
Gold Audit Entry Schema
Defines the structure for tamper-evident audit log entries
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import hashlib
import json


class ActionType(Enum):
    """Types of actions that can be audited"""
    TASK_START = "TASK_START"
    TASK_COMPLETE = "TASK_COMPLETE"
    STEP_EXECUTE = "STEP_EXECUTE"
    MCP_CALL = "MCP_CALL"
    ERROR = "ERROR"
    DECISION = "DECISION"


class ExecutionResult(Enum):
    """Execution result status"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL = "PARTIAL"
    SKIPPED = "SKIPPED"


@dataclass
class ErrorDetails:
    """Error information for failed actions"""
    error_type: str
    error_message: str
    stack_trace: str
    recovery_attempted: bool
    recovery_result: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GoldAuditEntry:
    """
    Tamper-evident audit log entry for autonomous actions.

    Each entry includes a hash of its content and the hash of the previous entry,
    creating a blockchain-like chain for tamper detection.
    """

    # Core identification
    entry_id: str
    timestamp: str  # ISO 8601 format with microsecond precision

    # Action details
    action_type: ActionType
    action_name: str
    parameters: Dict[str, Any]
    decision_rationale: str

    # Execution results
    execution_result: ExecutionResult
    result_data: Dict[str, Any]
    business_impact: str

    # Error handling
    error_details: Optional[ErrorDetails] = None

    # Entity relationships
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    task_id: Optional[str] = None

    # Hash chain for tamper-evidence
    previous_entry_hash: str = ""
    entry_hash: str = field(default="", init=False)

    def __post_init__(self):
        """Calculate entry hash after initialization"""
        if not self.entry_hash:
            self.entry_hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """
        Calculate SHA-256 hash of entry content.
        Excludes entry_hash itself to avoid circular dependency.
        """
        # Create dict without entry_hash
        entry_dict = {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "action_type": self.action_type.value if isinstance(self.action_type, ActionType) else self.action_type,
            "action_name": self.action_name,
            "parameters": self.parameters,
            "decision_rationale": self.decision_rationale,
            "execution_result": self.execution_result.value if isinstance(self.execution_result, ExecutionResult) else self.execution_result,
            "result_data": self.result_data,
            "business_impact": self.business_impact,
            "error_details": self.error_details.to_dict() if self.error_details else None,
            "related_entity_type": self.related_entity_type,
            "related_entity_id": self.related_entity_id,
            "task_id": self.task_id,
            "previous_entry_hash": self.previous_entry_hash
        }

        # Convert to JSON with sorted keys for consistent hashing
        content_json = json.dumps(entry_dict, sort_keys=True)
        return hashlib.sha256(content_json.encode()).hexdigest()

    def verify_hash(self) -> bool:
        """Verify that stored hash matches calculated hash"""
        calculated = self.calculate_hash()
        return calculated == self.entry_hash

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for JSON serialization"""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "action_type": self.action_type.value if isinstance(self.action_type, ActionType) else self.action_type,
            "action_name": self.action_name,
            "parameters": self.parameters,
            "decision_rationale": self.decision_rationale,
            "execution_result": self.execution_result.value if isinstance(self.execution_result, ExecutionResult) else self.execution_result,
            "result_data": self.result_data,
            "business_impact": self.business_impact,
            "error_details": self.error_details.to_dict() if self.error_details else None,
            "related_entity_type": self.related_entity_type,
            "related_entity_id": self.related_entity_id,
            "task_id": self.task_id,
            "previous_entry_hash": self.previous_entry_hash,
            "entry_hash": self.entry_hash
        }

    def to_json(self) -> str:
        """Convert entry to JSON string"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GoldAuditEntry':
        """Create entry from dictionary"""
        # Convert string enums back to enum types
        if isinstance(data.get('action_type'), str):
            data['action_type'] = ActionType(data['action_type'])
        if isinstance(data.get('execution_result'), str):
            data['execution_result'] = ExecutionResult(data['execution_result'])

        # Convert error_details dict to ErrorDetails object
        if data.get('error_details'):
            data['error_details'] = ErrorDetails(**data['error_details'])

        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'GoldAuditEntry':
        """Create entry from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


def verify_audit_chain(entries: list[GoldAuditEntry]) -> tuple[bool, Optional[str]]:
    """
    Verify the integrity of an audit log chain.

    Args:
        entries: List of audit entries in chronological order

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if chain is valid
        - (False, error_message) if tampering detected
    """
    if not entries:
        return True, None

    # Verify first entry has no previous hash
    if entries[0].previous_entry_hash != "":
        return False, f"First entry {entries[0].entry_id} has non-empty previous_entry_hash"

    # Verify each entry's hash
    for entry in entries:
        if not entry.verify_hash():
            return False, f"Entry {entry.entry_id} hash verification failed"

    # Verify chain linkage
    for i in range(1, len(entries)):
        if entries[i].previous_entry_hash != entries[i-1].entry_hash:
            return False, (
                f"Chain broken at entry {entries[i].entry_id}: "
                f"previous_entry_hash does not match previous entry's hash"
            )

    return True, None
