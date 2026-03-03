"""
Unit test for audit entry hash calculation in the Gold Tier system.
Test ID: T081 [P] [US4] Unit test for audit entry hash calculation
File: tests/unit/test_gold_logger.py
"""
import pytest
import hashlib
import json
from datetime import datetime
from src.audit.audit_schema import (
    GoldAuditEntry, ActionType, ExecutionResult, ErrorDetails, verify_audit_chain
)


class TestGoldLoggerUnit:
    """Unit tests for gold audit logger functionality."""

    def test_audit_entry_hash_calculation(self):
        """
        Test that audit entry hash is correctly calculated using SHA-256.

        Input: Audit entry with specific content
        Expected: Deterministic SHA-256 hash of entry content
        """
        entry = GoldAuditEntry(
            entry_id="test_entry_123",
            timestamp="2023-01-01T10:00:00Z",
            action_type=ActionType.TASK_START,
            action_name="test_action",
            parameters={"test": True, "value": 123},
            decision_rationale="Testing hash calculation",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"result": "ok"},
            business_impact="Test impact"
        )

        # Calculate hash
        calculated_hash = entry.calculate_hash()

        # Verify it's a valid SHA-256 hash (64 hex characters)
        assert len(calculated_hash) == 64
        assert all(c in '0123456789abcdef' for c in calculated_hash)

        # Verify hash verification passes
        assert entry.verify_hash() is True

        # Verify the hash is based on the content
        entry2 = GoldAuditEntry(
            entry_id="test_entry_123",
            timestamp="2023-01-01T10:00:00Z",
            action_type=ActionType.TASK_START,
            action_name="test_action",
            parameters={"test": True, "value": 123},
            decision_rationale="Testing hash calculation",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"result": "ok"},
            business_impact="Test impact"
        )

        assert entry.calculate_hash() == entry2.calculate_hash()

    def test_audit_entry_hash_changes_with_content(self):
        """
        Test that hash changes when entry content is modified.

        Input: Two similar entries with one different field
        Expected: Different hashes for different content
        """
        base_entry = GoldAuditEntry(
            entry_id="test_entry_123",
            timestamp="2023-01-01T10:00:00Z",
            action_type=ActionType.TASK_START,
            action_name="test_action",
            parameters={"test": True},
            decision_rationale="Testing hash sensitivity",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"result": "ok"},
            business_impact="Test impact"
        )

        # Entry with different parameter
        modified_entry = GoldAuditEntry(
            entry_id="test_entry_123",
            timestamp="2023-01-01T10:00:00Z",
            action_type=ActionType.TASK_START,
            action_name="test_action",
            parameters={"test": False},  # Different value
            decision_rationale="Testing hash sensitivity",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"result": "ok"},
            business_impact="Test impact"
        )

        original_hash = base_entry.calculate_hash()
        modified_hash = modified_entry.calculate_hash()

        assert original_hash != modified_hash

    def test_audit_entry_hash_consistency(self):
        """
        Test that hash calculation is consistent across multiple calls.

        Input: Same audit entry hashed multiple times
        Expected: Identical hash values
        """
        entry = GoldAuditEntry(
            entry_id="consistency_test_123",
            timestamp="2023-01-01T12:00:00Z",
            action_type=ActionType.DECISION,
            action_name="consistency_check",
            parameters={"check": "hash_consistency"},
            decision_rationale="Testing hash consistency across calls",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"consistency": "verified"},
            business_impact="Hash consistency confirmed"
        )

        # Calculate hash multiple times
        hash1 = entry.calculate_hash()
        hash2 = entry.calculate_hash()
        hash3 = entry.entry_hash  # Initial hash from __post_init__

        assert hash1 == hash2 == hash3
        assert entry.verify_hash() is True

    def test_audit_entry_hash_with_error_details(self):
        """
        Test that hash includes error details when present.

        Input: Audit entry with and without error details
        Expected: Different hashes due to error details inclusion
        """
        entry_without_error = GoldAuditEntry(
            entry_id="error_test_123",
            timestamp="2023-01-01T10:00:00Z",
            action_type=ActionType.ERROR,
            action_name="test_error_action",
            parameters={"test": True},
            decision_rationale="Testing with and without error details",
            execution_result=ExecutionResult.FAILURE,
            result_data={"error_occurred": True},
            business_impact="Error test"
        )

        error_details = ErrorDetails(
            error_type="TestError",
            error_message="This is a test error",
            stack_trace="Test stack trace info",
            recovery_attempted=False
        )

        entry_with_error = GoldAuditEntry(
            entry_id="error_test_123",
            timestamp="2023-01-01T10:00:00Z",
            action_type=ActionType.ERROR,
            action_name="test_error_action",
            parameters={"test": True},
            decision_rationale="Testing with and without error details",
            execution_result=ExecutionResult.FAILURE,
            result_data={"error_occurred": True},
            business_impact="Error test",
            error_details=error_details
        )

        hash_without_error = entry_without_error.calculate_hash()
        hash_with_error = entry_with_error.calculate_hash()

        assert hash_without_error != hash_with_error

    def test_verify_audit_chain_function(self):
        """
        Test the verify_audit_chain function with valid chain.

        Input: List of properly linked audit entries
        Expected: Chain verification passes as valid
        """
        # Create a chain of entries
        entries = []

        # First entry (has empty previous_entry_hash)
        entry1 = GoldAuditEntry(
            entry_id="chain_entry_1",
            timestamp="2023-01-01T10:00:00Z",
            action_type=ActionType.TASK_START,
            action_name="chain_test_1",
            parameters={"step": 1},
            decision_rationale="First entry in chain",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"chain_position": 1},
            business_impact="Chain test start",
            previous_entry_hash=""
        )
        entries.append(entry1)

        # Second entry (references first entry's hash)
        entry2 = GoldAuditEntry(
            entry_id="chain_entry_2",
            timestamp="2023-01-01T10:00:01Z",
            action_type=ActionType.STEP_EXECUTE,
            action_name="chain_test_2",
            parameters={"step": 2},
            decision_rationale="Second entry in chain",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"chain_position": 2},
            business_impact="Chain test continue",
            previous_entry_hash=entry1.entry_hash
        )
        entries.append(entry2)

        # Third entry (references second entry's hash)
        entry3 = GoldAuditEntry(
            entry_id="chain_entry_3",
            timestamp="2023-01-01T10:00:02Z",
            action_type=ActionType.TASK_COMPLETE,
            action_name="chain_test_3",
            parameters={"step": 3},
            decision_rationale="Third entry in chain",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"chain_position": 3},
            business_impact="Chain test end",
            previous_entry_hash=entry2.entry_hash
        )
        entries.append(entry3)

        # Verify the chain
        is_valid, error_msg = verify_audit_chain(entries)
        assert is_valid is True
        assert error_msg is None

    def test_verify_audit_chain_with_invalid_linkage(self):
        """
        Test the verify_audit_chain function with broken chain.

        Input: List of audit entries with incorrect linkage
        Expected: Chain verification fails and reports error
        """
        # Create entries but with incorrect linkage
        entry1 = GoldAuditEntry(
            entry_id="invalid_chain_1",
            timestamp="2023-01-01T10:00:00Z",
            action_type=ActionType.TASK_START,
            action_name="invalid_chain_1",
            parameters={"step": 1},
            decision_rationale="First entry in chain",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"chain_position": 1},
            business_impact="Chain test start",
            previous_entry_hash=""
        )

        # Second entry but with wrong previous hash (not entry1's hash)
        entry2 = GoldAuditEntry(
            entry_id="invalid_chain_2",
            timestamp="2023-01-01T10:00:01Z",
            action_type=ActionType.STEP_EXECUTE,
            action_name="invalid_chain_2",
            parameters={"step": 2},
            decision_rationale="Second entry in chain",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"chain_position": 2},
            business_impact="Chain test continue",
            previous_entry_hash="wrong_hash_value"  # Intentionally wrong
        )

        entries = [entry1, entry2]

        # Verify the chain should fail
        is_valid, error_msg = verify_audit_chain(entries)
        assert is_valid is False
        assert error_msg is not None
        assert "chain broken" in error_msg.lower() or "previous_entry_hash" in error_msg.lower()

    def test_verify_audit_chain_with_hash_mismatch(self):
        """
        Test the verify_audit_chain function with entries that have incorrect hashes.

        Input: List of entries where at least one has an incorrect hash
        Expected: Chain verification fails due to hash mismatch
        """
        # Create an entry with a bad hash
        entry = GoldAuditEntry(
            entry_id="bad_hash_123",
            timestamp="2023-01-01T10:00:00Z",
            action_type=ActionType.TASK_START,
            action_name="bad_hash_test",
            parameters={"test": True},
            decision_rationale="Testing bad hash detection",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"test_completed": True},
            business_impact="Hash test"
        )

        # Manually corrupt the hash to make it invalid
        original_hash = entry.entry_hash
        entry.entry_hash = "bad_hash_that_does_not_match_content"

        entries = [entry]

        # Verify the chain should fail due to hash mismatch
        is_valid, error_msg = verify_audit_chain(entries)
        assert is_valid is False
        assert error_msg is not None
        assert "hash verification failed" in error_msg.lower()

    def test_verify_audit_chain_empty_list(self):
        """
        Test the verify_audit_chain function with empty list.

        Input: Empty list of entries
        Expected: Chain verification passes as valid (trivially)
        """
        entries = []

        is_valid, error_msg = verify_audit_chain(entries)
        assert is_valid is True
        assert error_msg is None

    def test_audit_entry_hash_with_all_fields(self):
        """
        Test that audit entry hash includes all relevant fields.

        Input: Audit entry with all possible fields populated
        Expected: Hash that reflects all field values
        """
        error_details = ErrorDetails(
            error_type="ComprehensiveError",
            error_message="Comprehensive error test",
            stack_trace="Full stack trace",
            recovery_attempted=True,
            recovery_result="Recovery applied"
        )

        entry = GoldAuditEntry(
            entry_id="comprehensive_test_123",
            timestamp="2023-01-01T15:30:45.123456Z",
            action_type=ActionType.MCP_CALL,
            action_name="comprehensive_test",
            parameters={"param1": "value1", "param2": [1, 2, 3]},
            decision_rationale="Testing comprehensive hash calculation",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"result_key": "result_value", "nested": {"data": "value"}},
            business_impact="Comprehensive testing completed",
            error_details=error_details,
            related_entity_type="test_entity",
            related_entity_id="entity_456",
            task_id="task_789",
            previous_entry_hash="previous_hash_abc"
        )

        # Calculate hash multiple times to ensure consistency
        hash1 = entry.calculate_hash()
        hash2 = entry.calculate_hash()

        assert hash1 == hash2
        assert len(hash1) == 64
        assert entry.verify_hash() is True

        # Verify the hash changes if any field changes
        entry_different = GoldAuditEntry(
            entry_id="comprehensive_test_123",
            timestamp="2023-01-01T15:30:45.123456Z",
            action_type=ActionType.MCP_CALL,
            action_name="comprehensive_test",  # Same
            parameters={"param1": "value1", "param2": [1, 2, 3]},
            decision_rationale="Testing comprehensive hash calculation",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"result_key": "result_value", "nested": {"data": "value"}},
            business_impact="Comprehensive testing completed",
            error_details=error_details,
            related_entity_type="test_entity",
            related_entity_id="entity_456",
            task_id="task_789_different",  # Changed this field
            previous_entry_hash="previous_hash_abc"
        )

        different_hash = entry_different.calculate_hash()
        assert hash1 != different_hash

    def test_from_json_and_hash_verification(self):
        """
        Test that entries created from JSON maintain proper hash verification.

        Input: Audit entry serialized to JSON and deserialized back
        Expected: Deserialized entry has valid hash that matches its content
        """
        original_entry = GoldAuditEntry(
            entry_id="json_test_123",
            timestamp="2023-01-01T10:00:00Z",
            action_type=ActionType.DECISION,
            action_name="json_serialization_test",
            parameters={"serialization": True},
            decision_rationale="Testing JSON serialization roundtrip",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"serialization_ok": True},
            business_impact="JSON test completed"
        )

        # Serialize to JSON
        json_str = original_entry.to_json()

        # Deserialize from JSON
        deserialized_entry = GoldAuditEntry.from_json(json_str)

        # Check that the deserialized entry has valid hash
        assert deserialized_entry.verify_hash() is True
        assert original_entry.entry_hash == deserialized_entry.entry_hash
        assert original_entry.to_dict() == deserialized_entry.to_dict()


if __name__ == "__main__":
    test = TestGoldLoggerUnit()

    print("Running audit entry hash calculation test...")
    try:
        test.test_audit_entry_hash_calculation()
        print("✅ Audit entry hash calculation test passed")
    except Exception as e:
        print(f"❌ Audit entry hash calculation test failed: {e}")

    print("Running audit entry hash changes with content test...")
    try:
        test.test_audit_entry_hash_changes_with_content()
        print("✅ Audit entry hash changes with content test passed")
    except Exception as e:
        print(f"❌ Audit entry hash changes with content test failed: {e}")

    print("Running audit entry hash consistency test...")
    try:
        test.test_audit_entry_hash_consistency()
        print("✅ Audit entry hash consistency test passed")
    except Exception as e:
        print(f"❌ Audit entry hash consistency test failed: {e}")

    print("Running audit entry hash with error details test...")
    try:
        test.test_audit_entry_hash_with_error_details()
        print("✅ Audit entry hash with error details test passed")
    except Exception as e:
        print(f"❌ Audit entry hash with error details test failed: {e}")

    print("Running verify audit chain function test...")
    try:
        test.test_verify_audit_chain_function()
        print("✅ Verify audit chain function test passed")
    except Exception as e:
        print(f"❌ Verify audit chain function test failed: {e}")

    print("Running verify audit chain with invalid linkage test...")
    try:
        test.test_verify_audit_chain_with_invalid_linkage()
        print("✅ Verify audit chain with invalid linkage test passed")
    except Exception as e:
        print(f"❌ Verify audit chain with invalid linkage test failed: {e}")

    print("Running verify audit chain with hash mismatch test...")
    try:
        test.test_verify_audit_chain_with_hash_mismatch()
        print("✅ Verify audit chain with hash mismatch test passed")
    except Exception as e:
        print(f"❌ Verify audit chain with hash mismatch test failed: {e}")

    print("Running verify audit chain empty list test...")
    try:
        test.test_verify_audit_chain_empty_list()
        print("✅ Verify audit chain empty list test passed")
    except Exception as e:
        print(f"❌ Verify audit chain empty list test failed: {e}")

    print("Running audit entry hash with all fields test...")
    try:
        test.test_audit_entry_hash_with_all_fields()
        print("✅ Audit entry hash with all fields test passed")
    except Exception as e:
        print(f"❌ Audit entry hash with all fields test failed: {e}")

    print("Running from JSON and hash verification test...")
    try:
        test.test_from_json_and_hash_verification()
        print("✅ From JSON and hash verification test passed")
    except Exception as e:
        print(f"❌ From JSON and hash verification test failed: {e}")

    print("All gold logger unit tests completed!")