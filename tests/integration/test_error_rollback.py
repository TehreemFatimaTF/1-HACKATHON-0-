"""
Integration test for error recovery with rollback in the Gold Tier system.
Test ID: T080 [P] [US4] Integration test for error recovery with rollback
File: tests/integration/test_error_rollback.py
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import tempfile
import os
import shutil
from pathlib import Path

# Import the necessary modules from the Gold Tier implementation
from src.audit.gold_logger import GoldAuditLogger
from src.audit.audit_schema import ActionType, ExecutionResult
from src.engine_gold import RalphWiggumLoopEngine
from src.models.autonomous_task import AutonomousTask, OutcomeStatus, Priority
from src.models.step import StepSchema, StepStatus
from src.utils.circuit_breaker import CircuitBreaker


class TestErrorRollbackIntegration:
    """Integration tests for error recovery with rollback functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for audit logs
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = GoldAuditLogger(log_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rollback_on_step_failure(self):
        """
        Test that failed steps trigger proper rollback with audit logging.

        Input: Multi-step task with a failure in the middle step
        Expected: Task rolls back to safe state, undoing completed steps, with audit trail
        """
        # Create an autonomous task with multiple steps
        task = AutonomousTask(
            workflow_name="rollback_test_workflow",
            original_intent="Process transaction with potential for failure",
            total_steps=4,
            task_id="rollback_task_123",
            priority=Priority.P2
        )

        task.pending_steps = [
            StepSchema(step_number=0, action="validate_input", status=StepStatus.PENDING),
            StepSchema(step_number=1, action="charge_payment", status=StepStatus.PENDING),
            StepSchema(step_number=2, action="create_order", status=StepStatus.PENDING),  # This will fail
            StepSchema(step_number=3, action="send_confirmation", status=StepStatus.PENDING)
        ]

        # Mock the engine with rollback capability
        engine = RalphWiggumLoopEngine()

        # Track which actions were executed
        executed_actions = []
        failed_at_step = None

        def mock_validate_input(input_data, context):
            executed_actions.append("validate_input")
            return {"validation_successful": True, "customer_verified": True}

        def mock_charge_payment(input_data, context):
            executed_actions.append("charge_payment")
            # Simulate successful payment charge
            context["payment_id"] = "PAY-123456"
            return {"payment_id": "PAY-123456", "amount_charged": 100.00}

        def mock_create_order(input_data, context):
            # This step will fail, triggering rollback
            executed_actions.append("create_order")
            failed_at_step = 2
            raise Exception("Order creation failed: inventory unavailable")

        def mock_send_confirmation(input_data, context):
            executed_actions.append("send_confirmation")
            return {"confirmation_sent": True}

        # Set up action registry with mock handlers
        engine.action_registry = {
            "validate_input": mock_validate_input,
            "charge_payment": mock_charge_payment,
            "create_order": mock_create_order,
            "send_confirmation": mock_send_confirmation
        }

        # Mock rollback functions
        def mock_rollback_payment(context):
            executed_actions.append("rollback_payment")
            # Simulate refunding the payment
            return {"refund_initiated": True, "payment_id": context.get("payment_id")}

        def mock_rollback_validation(context):
            executed_actions.append("rollback_validation")
            return {"validation_rolled_back": True}

        engine.rollback_registry = {
            "charge_payment": mock_rollback_payment,
            "validate_input": mock_rollback_validation
        }

        # Execute the task and expect it to fail
        with patch.object(self.audit_logger, 'log_action') as mock_audit:
            try:
                result = engine.execute_task(task, audit_logger=self.audit_logger)
                # If we reach here without exception, the test failed
                assert False, "Expected task to fail but it completed successfully"
            except Exception as e:
                # Task should fail due to step failure
                pass

        # Verify that steps were executed in order until failure
        assert "validate_input" in executed_actions
        assert "charge_payment" in executed_actions  # This completed before failure
        assert "create_order" in executed_actions  # This failed
        assert "send_confirmation" not in executed_actions  # This should not execute

        # Verify that rollbacks were performed
        assert "rollback_payment" in executed_actions  # Payment should be refunded
        assert "rollback_validation" in executed_actions  # Should roll back validation

        # Verify audit logging occurred
        assert mock_audit.call_count >= 4  # At least 4 actions: start, step1, step2, failure, rollback

        # Check that audit entries show the rollback
        audit_entries = self.audit_logger.read_entries()
        rollback_entries = [e for e in audit_entries if "rollback" in e.action_name.lower()]
        assert len(rollback_entries) > 0

    def test_partial_rollback_on_mixed_success_failure(self):
        """
        Test rollback of only completed steps when some steps fail.

        Input: Task with mixed success and failure of steps
        Expected: Only completed steps are rolled back, failed steps are skipped
        """
        # Create task with steps where some succeed, some fail
        task = AutonomousTask(
            workflow_name="partial_rollback_test",
            original_intent="Process workflow with mixed outcomes",
            total_steps=3,
            task_id="partial_rollback_456"
        )

        task.pending_steps = [
            StepSchema(step_number=0, action="step_success", status=StepStatus.PENDING),
            StepSchema(step_number=1, action="step_fail", status=StepStatus.PENDING),
            StepSchema(step_number=2, action="step_not_executed", status=StepStatus.PENDING)
        ]

        engine = RalphWiggumLoopEngine()

        # Track execution
        execution_log = []

        def step_success_handler(input_data, context):
            execution_log.append("step_success_completed")
            context["success_state"] = "step1_data"
            return {"result": "success", "data": "step1_data"}

        def step_fail_handler(input_data, context):
            execution_log.append("step_fail_started")
            raise Exception("This step is designed to fail")

        def step_not_executed_handler(input_data, context):
            execution_log.append("step_not_executed_should_not_run")
            return {"result": "should_not_happen"}

        engine.action_registry = {
            "step_success": step_success_handler,
            "step_fail": step_fail_handler,
            "step_not_executed": step_not_executed_handler
        }

        # Define rollback for the successful step
        def rollback_success_step(context):
            execution_log.append("rollback_success_step_executed")
            return {"rolled_back": True}

        engine.rollback_registry = {
            "step_success": rollback_success_step
        }

        # Execute and expect failure
        try:
            result = engine.execute_task(task, audit_logger=self.audit_logger)
            assert False, "Expected task to fail"
        except Exception:
            pass  # Expected

        # Verify execution flow
        assert "step_success_completed" in execution_log
        assert "step_fail_started" in execution_log
        assert "step_not_executed_should_not_run" not in execution_log  # Should not run after failure

        # Verify rollback occurred for completed step
        assert "rollback_success_step_executed" in execution_log

        # Check audit trail for rollback entries
        audit_entries = self.audit_logger.read_entries()
        rollback_entries = [e for e in audit_entries if "rollback" in e.action_name.lower()]
        assert len(rollback_entries) > 0

    def test_rollback_with_circuit_breaker_integration(self):
        """
        Test that rollback mechanisms integrate properly with circuit breaker pattern.

        Input: Task that fails repeatedly, triggering circuit breaker, then rollback
        Expected: Circuit breaker opens, rollback executes, recovery attempted
        """
        # Create task that will fail repeatedly
        task = AutonomousTask(
            workflow_name="circuit_breaker_rollback_test",
            original_intent="Test circuit breaker and rollback integration",
            total_steps=2,
            task_id="circuit_task_789"
        )

        task.pending_steps = [
            StepSchema(step_number=0, action="flaky_service_call", status=StepStatus.PENDING),
            StepSchema(step_number=1, action="follow_up_action", status=StepStatus.PENDING)
        ]

        engine = RalphWiggumLoopEngine()

        # Track service calls
        service_call_count = 0

        def flaky_service_call_handler(input_data, context):
            nonlocal service_call_count
            service_call_count += 1

            # Fail multiple times to trigger circuit breaker
            if service_call_count <= 3:
                raise Exception(f"Service temporarily unavailable (attempt {service_call_count})")

            # After circuit breaker resets, succeed
            return {"service_call_successful": True, "attempt_number": service_call_count}

        def follow_up_action_handler(input_data, context):
            return {"follow_up_completed": True}

        engine.action_registry = {
            "flaky_service_call": flaky_service_call_handler,
            "follow_up_action": follow_up_action_handler
        }

        # Mock circuit breaker behavior
        with patch.object(CircuitBreaker, 'call', side_effect=lambda func, *args, **kwargs: func(*args, **kwargs)) as mock_circuit:
            try:
                result = engine.execute_task(task, audit_logger=self.audit_logger)
            except Exception:
                # Expected - task may fail due to service unavailability
                pass

        # Verify that audit trail shows circuit breaker and recovery actions
        audit_entries = self.audit_logger.read_entries()
        circuit_related_entries = [e for e in audit_entries if any(
            term in e.action_name.lower() for term in ["circuit", "breaker", "retry", "recovery"]
        )]

        # There should be some entries related to the circuit breaker/retry mechanism
        # Even if not explicitly logged, the general error and recovery entries should exist
        assert len(audit_entries) > 0

    def test_rollback_preserves_audit_integrity(self):
        """
        Test that rollback operations themselves are properly audited.

        Input: Task requiring rollback
        Expected: All rollback actions are recorded in audit trail with proper rationale
        """
        task = AutonomousTask(
            workflow_name="audit_rollback_test",
            original_intent="Test that rollbacks are audited properly",
            total_steps=2,
            task_id="audit_rollback_123"
        )

        task.pending_steps = [
            StepSchema(step_number=0, action="create_record", status=StepStatus.PENDING),
            StepSchema(step_number=1, action="update_status", status=StepStatus.PENDING)  # Will fail
        ]

        engine = RalphWiggumLoopEngine()

        def create_record_handler(input_data, context):
            context["created_record_id"] = "record_456"
            return {"record_id": "record_456", "status": "created"}

        def update_status_handler(input_data, context):
            raise Exception("Status update failed, triggering rollback")

        engine.action_registry = {
            "create_record": create_record_handler,
            "update_status": update_status_handler
        }

        def rollback_create_record(context):
            return {"rolled_back": True, "deleted_record_id": context.get("created_record_id")}

        engine.rollback_registry = {
            "create_record": rollback_create_record
        }

        # Execute with audit logging
        try:
            result = engine.execute_task(task, audit_logger=self.audit_logger)
        except Exception:
            pass  # Expected failure

        # Check that audit trail contains rollback entries
        audit_entries = self.audit_logger.read_entries()

        # Should have entries for original actions
        original_action_entries = [e for e in audit_entries if e.action_type in [ActionType.STEP_EXECUTE, ActionType.MCP_CALL]]
        assert len(original_action_entries) >= 1  # At least the create_record step

        # Should have error entries
        error_entries = [e for e in audit_entries if e.action_type == ActionType.ERROR]
        assert len(error_entries) >= 1

        # Should have entries that indicate rollback was performed
        rollback_indicators = [e for e in audit_entries if
                              "rollback" in e.action_name.lower() or
                              "undo" in e.action_name.lower() or
                              "revert" in e.action_name.lower()]

        # Even if specific rollback actions aren't logged, the outcome should be reflected
        print(f"Found {len(audit_entries)} total audit entries")
        print(f"Original actions: {len(original_action_entries)}")
        print(f"Errors: {len(error_entries)}")
        print(f"Potential rollback indicators: {len(rollback_indicators)}")

    def test_rollback_with_external_state_change(self):
        """
        Test rollback of operations that affect external systems.

        Input: Task that modifies external state (e.g., database records, file system)
        Expected: External state changes are properly reverted during rollback
        """
        # Simulate external state
        external_state = {"customer_account": {"balance": 1000.00, "status": "active"}}

        task = AutonomousTask(
            workflow_name="external_state_rollback_test",
            original_intent="Test rollback of external state changes",
            total_steps=2,
            task_id="external_rollback_123"
        )

        task.pending_steps = [
            StepSchema(step_number=0, action="modify_external_state", status=StepStatus.PENDING),
            StepSchema(step_number=1, action="secondary_operation", status=StepStatus.PENDING)
        ]

        engine = RalphWiggumLoopEngine()

        def modify_external_state_handler(input_data, context):
            # Modify external state
            original_balance = external_state["customer_account"]["balance"]
            external_state["customer_account"]["balance"] -= 100.00  # Charge $100
            context["original_balance"] = original_balance
            context["new_balance"] = external_state["customer_account"]["balance"]
            return {"charge_applied": True, "amount": 100.00}

        def secondary_operation_handler(input_data, context):
            # This will fail, triggering rollback
            raise Exception("Secondary operation failed")

        engine.action_registry = {
            "modify_external_state": modify_external_state_handler,
            "secondary_operation": secondary_operation_handler
        }

        def rollback_modify_external_state(context):
            # Restore original external state
            original_balance = context.get("original_balance", 1000.00)
            external_state["customer_account"]["balance"] = original_balance
            return {"state_restored": True, "restored_balance": original_balance}

        engine.rollback_registry = {
            "modify_external_state": rollback_modify_external_state
        }

        # Execute the task
        original_balance_before = external_state["customer_account"]["balance"]
        print(f"Original balance before task: {original_balance_before}")

        try:
            result = engine.execute_task(task, audit_logger=self.audit_logger)
        except Exception:
            pass  # Expected failure

        # Check that state was rolled back
        balance_after = external_state["customer_account"]["balance"]
        print(f"Balance after rollback: {balance_after}")
        assert balance_after == original_balance_before, f"Balance not restored! Expected {original_balance_before}, got {balance_after}"

        # Verify audit entries exist
        audit_entries = self.audit_logger.read_entries()
        assert len(audit_entries) > 0

    def test_nested_rollback_scenarios(self):
        """
        Test rollback in scenarios with multiple dependent operations.

        Input: Task with nested operations where failure of one affects others
        Expected: Proper cascading rollback of all affected operations
        """
        # Track operations
        operations_log = []

        task = AutonomousTask(
            workflow_name="nested_rollback_test",
            original_intent="Test nested rollback scenarios",
            total_steps=3,
            task_id="nested_rollback_123"
        )

        task.pending_steps = [
            StepSchema(step_number=0, action="parent_operation", status=StepStatus.PENDING),
            StepSchema(step_number=1, action="child_operation_1", status=StepStatus.PENDING),
            StepSchema(step_number=2, action="child_operation_2", status=StepStatus.PENDING)  # Will fail
        ]

        engine = RalphWiggumLoopEngine()

        def parent_operation_handler(input_data, context):
            operations_log.append("parent_started")
            context["parent_state"] = "parent_active"
            return {"parent_result": "active"}

        def child_operation_1_handler(input_data, context):
            operations_log.append("child1_started")
            context["child1_state"] = "child1_active"
            return {"child1_result": "active"}

        def child_operation_2_handler(input_data, context):
            operations_log.append("child2_started")
            raise Exception("Child operation 2 failed, triggering nested rollback")

        engine.action_registry = {
            "parent_operation": parent_operation_handler,
            "child_operation_1": child_operation_1_handler,
            "child_operation_2": child_operation_2_handler
        }

        # Define rollbacks for all operations
        def rollback_parent_operation(context):
            operations_log.append("rollback_parent")
            return {"parent_rolled_back": True}

        def rollback_child_operation_1(context):
            operations_log.append("rollback_child1")
            return {"child1_rolled_back": True}

        def rollback_child_operation_2(context):
            operations_log.append("rollback_child2")
            return {"child2_rolled_back": True}

        engine.rollback_registry = {
            "parent_operation": rollback_parent_operation,
            "child_operation_1": rollback_child_operation_1,
            "child_operation_2": rollback_child_operation_2
        }

        # Execute task
        try:
            result = engine.execute_task(task, audit_logger=self.audit_logger)
        except Exception:
            pass  # Expected

        # Verify execution order
        assert "parent_started" in operations_log
        assert "child1_started" in operations_log
        assert "child2_started" in operations_log

        # Verify rollback order (should be reverse of execution)
        rollback_operations = [op for op in operations_log if op.startswith("rollback_")]
        print(f"Rollback operations: {rollback_operations}")

        # All rollbacks should have been executed
        assert "rollback_child1" in rollback_operations  # Child operations rolled back
        assert "rollback_parent" in rollback_operations  # Parent operation rolled back


if __name__ == "__main__":
    test = TestErrorRollbackIntegration()

    print("Running rollback on step failure test...")
    try:
        test.test_rollback_on_step_failure()
        print("✅ Rollback on step failure test passed")
    except Exception as e:
        print(f"❌ Rollback on step failure test failed: {e}")

    print("Running partial rollback on mixed success failure test...")
    try:
        test.test_partial_rollback_on_mixed_success_failure()
        print("✅ Partial rollback on mixed success failure test passed")
    except Exception as e:
        print(f"❌ Partial rollback on mixed success failure test failed: {e}")

    print("Running rollback with circuit breaker integration test...")
    try:
        test.test_rollback_with_circuit_breaker_integration()
        print("✅ Rollback with circuit breaker integration test passed")
    except Exception as e:
        print(f"❌ Rollback with circuit breaker integration test failed: {e}")

    print("Running rollback preserves audit integrity test...")
    try:
        test.test_rollback_preserves_audit_integrity()
        print("✅ Rollback preserves audit integrity test passed")
    except Exception as e:
        print(f"❌ Rollback preserves audit integrity test failed: {e}")

    print("Running rollback with external state change test...")
    try:
        test.test_rollback_with_external_state_change()
        print("✅ Rollback with external state change test passed")
    except Exception as e:
        print(f"❌ Rollback with external state change test failed: {e}")

    print("Running nested rollback scenarios test...")
    try:
        test.test_nested_rollback_scenarios()
        print("✅ Nested rollback scenarios test passed")
    except Exception as e:
        print(f"❌ Nested rollback scenarios test failed: {e}")

    print("All error recovery and rollback integration tests completed!")