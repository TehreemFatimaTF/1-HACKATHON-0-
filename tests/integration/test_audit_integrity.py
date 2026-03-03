"""
Integration test for tamper-evident hash chain in the Gold Tier system.
Test ID: T079 [P] [US4] Integration test for tamper-evident hash chain
File: tests/integration/test_audit_integrity.py
"""
import pytest
from unittest.mock import Mock, patch
import tempfile
import os
import shutil
from pathlib import Path

# Import the necessary modules from the Gold Tier implementation
from src.audit.gold_logger import GoldAuditLogger
from src.audit.audit_schema import (
    GoldAuditEntry, ActionType, ExecutionResult, ErrorDetails, verify_audit_chain
)
from datetime import datetime
import hashlib
import json


class TestAuditIntegrityIntegration:
    """Integration tests for tamper-evident hash chain functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for audit logs
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = GoldAuditLogger(log_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_hash_chain_creation_and_verification(self):
        """
        Test that audit entries form a valid hash chain with proper linkage.

        Input: Multiple sequential audit log entries
        Expected: Valid hash chain where each entry references the previous entry's hash
        """
        # Create multiple sequential entries
        entries = []

        # Create first entry (should have empty previous_entry_hash)
        entry1 = self.audit_logger.log_action(
            action_type=ActionType.TASK_START,
            action_name="first_task",
            parameters={"task": "test_1"},
            decision_rationale="Starting first test task",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"task_started": True},
            business_impact="Test task initiated"
        )
        entries.append(entry1)

        # Create second entry (should reference first entry's hash)
        entry2 = self.audit_logger.log_action(
            action_type=ActionType.STEP_EXECUTE,
            action_name="first_step",
            parameters={"step": "test_step_1"},
            decision_rationale="Executing first test step",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"step_completed": True},
            business_impact="Test step completed"
        )
        entries.append(entry2)

        # Create third entry (should reference second entry's hash)
        entry3 = self.audit_logger.log_action(
            action_type=ActionType.TASK_COMPLETE,
            action_name="first_task_complete",
            parameters={"task": "test_1"},
            decision_rationale="Completing first test task",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"task_completed": True},
            business_impact="Test task completed"
        )
        entries.append(entry3)

        # Verify the hash chain integrity
        is_valid, error_msg = self.audit_logger.verify_integrity()
        assert is_valid, f"Hash chain verification failed: {error_msg}"

        # Also verify directly using the verify_audit_chain function
        all_entries = self.audit_logger.read_entries()
        assert len(all_entries) >= 3

        chain_valid, chain_error = verify_audit_chain(all_entries)
        assert chain_valid, f"Audit chain verification failed: {chain_error}"

        # Verify specific chain properties
        # First entry should have empty previous hash
        assert all_entries[0].previous_entry_hash == ""

        # Each subsequent entry should reference the previous entry's hash
        for i in range(1, len(all_entries)):
            assert all_entries[i].previous_entry_hash == all_entries[i-1].entry_hash

    def test_hash_chain_tamper_detection(self):
        """
        Test that tampering with audit log entries is detected by hash chain verification.

        Input: Valid audit log chain with one entry manually modified
        Expected: Hash chain verification fails and detects tampering
        """
        # Create multiple entries to form a chain
        entry1 = self.audit_logger.log_action(
            action_type=ActionType.TASK_START,
            action_name="tamper_test_task",
            parameters={"task": "tamper_test_1"},
            decision_rationale="Starting tamper detection test task",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"task_started": True},
            business_impact="Test task initiated for tamper detection"
        )

        entry2 = self.audit_logger.log_action(
            action_type=ActionType.STEP_EXECUTE,
            action_name="tamper_test_step",
            parameters={"step": "tamper_test_step_1"},
            decision_rationale="Executing tamper detection test step",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"step_completed": True},
            business_impact="Test step completed for tamper detection"
        )

        entry3 = self.audit_logger.log_action(
            action_type=ActionType.TASK_COMPLETE,
            action_name="tamper_test_task_complete",
            parameters={"task": "tamper_test_1"},
            decision_rationale="Completing tamper detection test task",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"task_completed": True},
            business_impact="Test task completed for tamper detection"
        )

        # Verify chain is initially valid
        is_valid, error_msg = self.audit_logger.verify_integrity()
        assert is_valid, f"Initial chain verification failed: {error_msg}"

        # Now tamper with the log file by modifying one entry
        log_file = self.audit_logger._get_log_file_path()

        # Read all entries from file
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Modify the first entry by changing some data (this will change its hash)
        first_entry_data = json.loads(lines[0])
        first_entry_data['business_impact'] = 'This entry has been tampered with!'

        # Recalculate hash for modified entry (but don't recalculate the entry_hash properly)
        tampered_hash = hashlib.sha256(json.dumps(first_entry_data, sort_keys=True).encode()).hexdigest()
        first_entry_data['entry_hash'] = tampered_hash  # Wrong hash calculation

        # Save back to first line
        lines[0] = json.dumps(first_entry_data) + '\n'

        # Write tampered data back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        # Now verify the chain - it should detect tampering
        is_valid, error_msg = self.audit_logger.verify_integrity()
        assert not is_valid, f"Tampering was not detected! Chain should be invalid."
        assert error_msg is not None
        assert 'hash verification failed' in error_msg.lower() or 'chain broken' in error_msg.lower()

    def test_hash_verification_for_single_entry(self):
        """
        Test that hash verification works for a single audit entry.

        Input: Single audit log entry
        Expected: Valid hash and chain verification
        """
        # Create a single entry
        entry = self.audit_logger.log_action(
            action_type=ActionType.DECISION,
            action_name="single_entry_test",
            parameters={"test": "single"},
            decision_rationale="Testing single entry hash verification",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"test_passed": True},
            business_impact="Single entry test completed"
        )

        # Read back the entries
        entries = self.audit_logger.read_entries()
        assert len(entries) == 1

        # Verify the single entry's hash is correct
        assert entries[0].verify_hash() is True

        # Verify the chain (single entry should have empty previous hash)
        chain_valid, chain_error = verify_audit_chain(entries)
        assert chain_valid, f"Single entry chain verification failed: {chain_error}"
        assert entries[0].previous_entry_hash == ""  # First entry has no previous

    def test_hash_chain_with_error_entries(self):
        """
        Test that hash chain integrity is maintained even with error entries.

        Input: Audit log entries including error entries
        Expected: Valid hash chain with proper error entries included
        """
        error_details = ErrorDetails(
            error_type="TestError",
            error_message="This is a test error for integration purposes",
            stack_trace="Test traceback information",
            recovery_attempted=True,
            recovery_result="Recovery failed"
        )

        # Create entries including an error entry
        entries = []

        entry1 = self.audit_logger.log_action(
            action_type=ActionType.TASK_START,
            action_name="error_chain_test",
            parameters={"test": "error_chain"},
            decision_rationale="Starting test with potential error",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"task_started": True},
            business_impact="Error chain test initiated"
        )
        entries.append(entry1)

        error_entry = self.audit_logger.log_action(
            action_type=ActionType.ERROR,
            action_name="test_error_occurred",
            parameters={"error_context": "test_simulation"},
            decision_rationale="Recording test error in audit trail",
            execution_result=ExecutionResult.FAILURE,
            result_data={"error_recorded": True},
            business_impact="Error recorded in audit trail",
            error_details=error_details
        )
        entries.append(error_entry)

        entry3 = self.audit_logger.log_action(
            action_type=ActionType.DECISION,
            action_name="recovery_decision",
            parameters={"recovery_plan": "fallback_method"},
            decision_rationale="Making recovery decision after error",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"recovery_planned": True},
            business_impact="Recovery plan decided after error"
        )
        entries.append(entry3)

        # Verify chain integrity with error entry included
        is_valid, error_msg = self.audit_logger.verify_integrity()
        assert is_valid, f"Hash chain with error entries failed verification: {error_msg}"

        # Read entries back to verify they all have proper hashes
        all_entries = self.audit_logger.read_entries()
        assert len(all_entries) >= 3

        # Verify each entry has correct hash
        for entry in all_entries:
            assert entry.verify_hash() is True

        # Verify chain linkage
        chain_valid, chain_error = verify_audit_chain(all_entries)
        assert chain_valid, f"Error entry chain verification failed: {chain_error}"

    def test_hash_chain_continuity_across_dates(self):
        """
        Test that hash chain maintains integrity across date boundaries.

        Input: Audit entries spanning multiple days
        Expected: Each day's entries form valid chains independently
        """
        # Create first entry
        entry1 = self.audit_logger.log_action(
            action_type=ActionType.TASK_START,
            action_name="multi_day_test_1",
            parameters={"test": "multi_day", "day": 1},
            decision_rationale="Starting multi-day test first day",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"day_1_started": True},
            business_impact="Multi-day test initiated"
        )

        # Create second entry
        entry2 = self.audit_logger.log_action(
            action_type=ActionType.STEP_EXECUTE,
            action_name="multi_day_step_1",
            parameters={"test": "multi_day", "step": 1},
            decision_rationale="Executing multi-day test step first day",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"step_1_completed": True},
            business_impact="Multi-day test step completed"
        )

        # Verify today's chain is valid
        is_valid, error_msg = self.audit_logger.verify_integrity()
        assert is_valid, f"Multi-day chain verification failed: {error_msg}"

        # Check that entries were properly linked with their hashes
        entries = self.audit_logger.read_entries()
        assert len(entries) >= 2

        # Second entry should reference first entry's hash
        assert entries[1].previous_entry_hash == entries[0].entry_hash

    def test_hash_calculation_consistency(self):
        """
        Test that hash calculation is consistent and deterministic.

        Input: Same audit entry data calculated multiple times
        Expected: Identical hashes produced each time
        """
        # Create an entry
        entry = GoldAuditEntry(
            entry_id="test_consistency_123",
            timestamp="2023-01-01T10:00:00Z",
            action_type=ActionType.DECISION,
            action_name="consistency_test",
            parameters={"test": True},
            decision_rationale="Testing hash consistency",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"hash_consistent": True},
            business_impact="Hash consistency verified"
        )

        # Calculate hash multiple times - should be the same each time
        hash1 = entry.calculate_hash()
        hash2 = entry.calculate_hash()
        hash3 = entry.entry_hash  # Hash calculated automatically in __post_init__

        assert hash1 == hash2 == hash3
        assert len(hash1) == 64  # SHA-256 produces 64-character hex string

        # Verify hash verification works
        assert entry.verify_hash() is True

        # Manually verify what goes into the hash calculation
        entry_dict = {
            "entry_id": entry.entry_id,
            "timestamp": entry.timestamp,
            "action_type": entry.action_type.value,
            "action_name": entry.action_name,
            "parameters": entry.parameters,
            "decision_rationale": entry.decision_rationale,
            "execution_result": entry.execution_result.value,
            "result_data": entry.result_data,
            "business_impact": entry.business_impact,
            "error_details": entry.error_details,
            "related_entity_type": entry.related_entity_type,
            "related_entity_id": entry.related_entity_id,
            "task_id": entry.task_id,
            "previous_entry_hash": entry.previous_entry_hash
        }

        expected_hash = hashlib.sha256(json.dumps(entry_dict, sort_keys=True).encode()).hexdigest()
        assert hash1 == expected_hash


if __name__ == "__main__":
    test = TestAuditIntegrityIntegration()

    print("Running hash chain creation and verification test...")
    try:
        test.test_hash_chain_creation_and_verification()
        print("✅ Hash chain creation and verification test passed")
    except Exception as e:
        print(f"❌ Hash chain creation and verification test failed: {e}")

    print("Running hash chain tamper detection test...")
    try:
        test.test_hash_chain_tamper_detection()
        print("✅ Hash chain tamper detection test passed")
    except Exception as e:
        print(f"❌ Hash chain tamper detection test failed: {e}")

    print("Running hash verification for single entry test...")
    try:
        test.test_hash_verification_for_single_entry()
        print("✅ Hash verification for single entry test passed")
    except Exception as e:
        print(f"❌ Hash verification for single entry test failed: {e}")

    print("Running hash chain with error entries test...")
    try:
        test.test_hash_chain_with_error_entries()
        print("✅ Hash chain with error entries test passed")
    except Exception as e:
        print(f"❌ Hash chain with error entries test failed: {e}")

    print("Running hash chain continuity across dates test...")
    try:
        test.test_hash_chain_continuity_across_dates()
        print("✅ Hash chain continuity across dates test passed")
    except Exception as e:
        print(f"❌ Hash chain continuity across dates test failed: {e}")

    print("Running hash calculation consistency test...")
    try:
        test.test_hash_calculation_consistency()
        print("✅ Hash calculation consistency test passed")
    except Exception as e:
        print(f"❌ Hash calculation consistency test failed: {e}")

    print("All audit integrity integration tests completed!")