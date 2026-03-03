"""
Gold Audit Logger
Provides tamper-evident logging with hash chain verification for all autonomous actions
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

from src.audit.audit_schema import (
    GoldAuditEntry,
    ActionType,
    ExecutionResult,
    ErrorDetails,
    verify_audit_chain
)

logger = logging.getLogger(__name__)


class GoldAuditLogger:
    """
    Tamper-evident audit logger for autonomous actions.

    Maintains a blockchain-like chain of audit entries where each entry
    includes a hash of the previous entry, enabling tamper detection.
    """

    def __init__(self, log_dir: str = "Logs/Audit_Trail"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.last_entry_hash = ""
        self._load_last_entry_hash()

    def _get_log_file_path(self) -> Path:
        """Get path to today's audit log file"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"gold_audit_{today}.jsonl"

    def _load_last_entry_hash(self):
        """Load the hash of the last entry from today's log file"""
        log_file = self._get_log_file_path()

        if not log_file.exists():
            self.last_entry_hash = ""
            return

        try:
            # Read last line of log file
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    if last_line:
                        entry_data = json.loads(last_line)
                        self.last_entry_hash = entry_data.get('entry_hash', '')
        except Exception as e:
            logger.error(f"Failed to load last entry hash: {e}")
            self.last_entry_hash = ""

    def log_action(
        self,
        action_type: ActionType,
        action_name: str,
        parameters: Dict[str, Any],
        decision_rationale: str,
        execution_result: ExecutionResult,
        result_data: Dict[str, Any],
        business_impact: str,
        error_details: Optional[ErrorDetails] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> GoldAuditEntry:
        """
        Log an autonomous action to the audit trail.

        Args:
            action_type: Type of action (TASK_START, STEP_EXECUTE, etc.)
            action_name: Human-readable action name
            parameters: Input parameters for the action
            decision_rationale: Why this action was taken
            execution_result: SUCCESS, FAILURE, PARTIAL, or SKIPPED
            result_data: Output data from the action
            business_impact: Assessment of business value
            error_details: Error information if action failed
            related_entity_type: Type of entity affected
            related_entity_id: ID of affected entity
            task_id: AutonomousTask ID if part of workflow

        Returns:
            Created GoldAuditEntry
        """
        # Create entry
        entry = GoldAuditEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            action_type=action_type,
            action_name=action_name,
            parameters=parameters,
            decision_rationale=decision_rationale,
            execution_result=execution_result,
            result_data=result_data,
            business_impact=business_impact,
            error_details=error_details,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            task_id=task_id,
            previous_entry_hash=self.last_entry_hash
        )

        # Write to log file (append-only)
        log_file = self._get_log_file_path()
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(entry.to_json() + '\n')

            # Update last entry hash
            self.last_entry_hash = entry.entry_hash

            logger.info(
                f"Audit log entry created: {action_type.value} - {action_name} "
                f"(result: {execution_result.value})"
            )

        except Exception as e:
            logger.error(f"Failed to write audit log entry: {e}")
            raise

        return entry

    def read_entries(
        self,
        date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[GoldAuditEntry]:
        """
        Read audit entries from log file.

        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            limit: Maximum number of entries to return (most recent first)

        Returns:
            List of GoldAuditEntry objects
        """
        if date:
            log_file = self.log_dir / f"gold_audit_{date}.jsonl"
        else:
            log_file = self._get_log_file_path()

        if not log_file.exists():
            return []

        entries = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entry = GoldAuditEntry.from_json(line)
                        entries.append(entry)
        except Exception as e:
            logger.error(f"Failed to read audit log entries: {e}")
            return []

        # Apply limit (most recent first)
        if limit:
            entries = entries[-limit:]

        return entries

    def verify_integrity(self, date: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """
        Verify the integrity of the audit log chain.

        Args:
            date: Date in YYYY-MM-DD format (defaults to today)

        Returns:
            Tuple of (is_valid, error_message)
        """
        entries = self.read_entries(date=date)

        if not entries:
            return True, None

        return verify_audit_chain(entries)

    def get_entries_by_task(self, task_id: str) -> List[GoldAuditEntry]:
        """Get all audit entries for a specific task"""
        all_entries = self.read_entries()
        return [e for e in all_entries if e.task_id == task_id]

    def get_entries_by_action_type(
        self,
        action_type: ActionType,
        date: Optional[str] = None
    ) -> List[GoldAuditEntry]:
        """Get all audit entries of a specific action type"""
        all_entries = self.read_entries(date=date)
        return [e for e in all_entries if e.action_type == action_type]

    def get_failed_actions(self, date: Optional[str] = None) -> List[GoldAuditEntry]:
        """Get all failed actions"""
        all_entries = self.read_entries(date=date)
        return [
            e for e in all_entries
            if e.execution_result in [ExecutionResult.FAILURE, ExecutionResult.PARTIAL]
        ]


# Global logger instance
_audit_logger: Optional[GoldAuditLogger] = None


def get_audit_logger() -> GoldAuditLogger:
    """Get or create global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = GoldAuditLogger()
    return _audit_logger
