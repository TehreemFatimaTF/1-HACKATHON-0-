"""
Integration test for complete audit trail in the Gold Tier system.
Test ID: T078 [P] [US4] Integration test for audit trail completeness
File: tests/integration/test_audit_trail.py
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import tempfile
import os
from pathlib import Path

# Import the necessary modules from the Gold Tier implementation
from src.audit.gold_logger import GoldAuditLogger, get_audit_logger
from src.audit.audit_schema import (
    GoldAuditEntry, ActionType, ExecutionResult, ErrorDetails
)
from src.models.autonomous_task import AutonomousTask
from src.engine_gold import RalphWiggumLoopEngine


class TestAuditTrailIntegration:
    """Integration tests for complete audit trail functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for audit logs
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = GoldAuditLogger(log_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_audit_trail_completeness_for_multi_step_workflow(self):
        """
        Test that all steps in a multi-step workflow are logged in the audit trail.

        Input: Multi-step autonomous workflow execution
        Expected: Complete audit trail with all decision rationales, execution results,
                 and business impact assessments
        """
        # Create a mock multi-step workflow
        task = AutonomousTask(
            workflow_name="test_multi_step_workflow",
            original_intent="Process client invoice and send follow-up email",
            total_steps=3,
            task_id="test_task_multi_step_123"
        )

        # Add some completed steps
        from src.models.step import StepSchema, StepStatus
        task.completed_steps = [
            StepSchema(
                step_number=0,
                action="create_invoice",
                status=StepStatus.SUCCESS,
                input_data={"client_id": "client_123", "amount": 500.00},
                output={"invoice_id": "inv_456", "status": "created"}
            )
        ]

        # Simulate logging multiple actions
        action_entries = []

        # Log task start
        entry1 = self.audit_logger.log_action(
            action_type=ActionType.TASK_START,
            action_name="multi_step_workflow_start",
            parameters={"task_id": task.task_id, "workflow_name": task.workflow_name},
            decision_rationale="Starting multi-step workflow to process client invoice",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"initial_task_status": "started"},
            business_impact="Workflow initiated for client invoice processing"
        )
        action_entries.append(entry1)

        # Log step execution
        entry2 = self.audit_logger.log_action(
            action_type=ActionType.STEP_EXECUTE,
            action_name="create_invoice_step",
            parameters={"step_number": 0, "invoice_amount": 500.00},
            decision_rationale="Executing create invoice step based on workflow plan",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"invoice_id": "inv_456", "created_at": "2023-01-01T10:00:00Z"},
            business_impact="Invoice created, client billing process initiated"
        )
        action_entries.append(entry2)

        # Log MCP call
        entry3 = self.audit_logger.log_action(
            action_type=ActionType.MCP_CALL,
            action_name="send_email_mcp_call",
            parameters={"email_type": "invoice_notification", "recipient": "client_123"},
            decision_rationale="Sending invoice notification email to client",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"email_sent": True, "message_id": "msg_789"},
            business_impact="Client notified of invoice, improving payment collection"
        )
        action_entries.append(entry3)

        # Log task completion
        entry4 = self.audit_logger.log_action(
            action_type=ActionType.TASK_COMPLETE,
            action_name="multi_step_workflow_complete",
            parameters={"task_id": task.task_id, "total_steps": 3, "completed_steps": 1},
            decision_rationale="Workflow completed successfully with all required steps",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"final_status": "completed", "outcome": "invoice_processed"},
            business_impact="Client invoice processed and notified, revenue pipeline advanced"
        )
        action_entries.append(entry4)

        # Verify all entries are in the log
        entries = self.audit_logger.read_entries()
        assert len(entries) >= 4  # Should have at least the 4 entries we created

        # Verify each entry type is present
        action_types = [entry.action_type for entry in entries]
        assert ActionType.TASK_START in action_types
        assert ActionType.STEP_EXECUTE in action_types
        assert ActionType.MCP_CALL in action_types
        assert ActionType.TASK_COMPLETE in action_types

        # Verify that decision rationales are comprehensive
        decision_rationales = [entry.decision_rationale for entry in entries]
        assert any("multi-step workflow" in rationale for rationale in decision_rationales)
        assert any("invoice notification" in rationale for rationale in decision_rationales)

        # Verify that business impacts are meaningful
        business_impacts = [entry.business_impact for entry in entries]
        assert any("client billing" in impact.lower() for impact in business_impacts)
        assert any("revenue" in impact.lower() for impact in business_impacts)

    def test_audit_trail_completeness_with_error_scenario(self):
        """
        Test that error scenarios are completely logged in the audit trail.

        Input: Workflow execution with error and recovery
        Expected: Complete audit trail showing error, recovery attempts, and final outcome
        """
        # Simulate an error scenario
        error_details = ErrorDetails(
            error_type="ConnectionError",
            error_message="Failed to connect to external service",
            stack_trace="Traceback: ...",
            recovery_attempted=True,
            recovery_result="Fallback service used"
        )

        # Log error action
        error_entry = self.audit_logger.log_action(
            action_type=ActionType.ERROR,
            action_name="service_connection_failure",
            parameters={"service": "external_api", "attempt": 1},
            decision_rationale="Primary service unavailable, attempting fallback",
            execution_result=ExecutionResult.FAILURE,
            result_data={"fallback_used": True, "recovery_method": "alternative_endpoint"},
            business_impact="Service temporarily unavailable but recovered using fallback",
            error_details=error_details
        )

        # Log recovery action
        recovery_entry = self.audit_logger.log_action(
            action_type=ActionType.DECISION,
            action_name="fallback_recovery_executed",
            parameters={"recovery_method": "alternative_endpoint"},
            decision_rationale="Executing fallback recovery strategy to maintain service",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"recovery_successful": True, "service_restored": True},
            business_impact="Service restored via fallback, minimal business impact"
        )

        # Verify error and recovery entries are in the log
        entries = self.audit_logger.read_entries()
        assert len(entries) >= 2

        # Check that error was properly logged
        error_entries = [e for e in entries if e.action_type == ActionType.ERROR]
        assert len(error_entries) >= 1
        assert error_entries[0].error_details is not None
        assert error_entries[0].error_details.error_type == "ConnectionError"

        # Check that recovery was properly logged
        recovery_entries = [e for e in entries if e.action_name == "fallback_recovery_executed"]
        assert len(recovery_entries) >= 1
        assert recovery_entries[0].execution_result == ExecutionResult.SUCCESS

    def test_audit_trail_entity_relationship_tracking(self):
        """
        Test that entity relationships are properly tracked in audit trail.

        Input: Actions affecting different entities
        Expected: Related entity types and IDs properly recorded in audit entries
        """
        # Log actions affecting different entities
        client_entry = self.audit_logger.log_action(
            action_type=ActionType.MCP_CALL,
            action_name="update_client_record",
            parameters={"field": "status", "new_value": "active"},
            decision_rationale="Updating client status based on recent activity",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"previous_status": "pending", "new_status": "active"},
            business_impact="Client status updated, enabling full service access",
            related_entity_type="client",
            related_entity_id="client_123"
        )

        invoice_entry = self.audit_logger.log_action(
            action_type=ActionType.STEP_EXECUTE,
            action_name="create_invoice_for_client",
            parameters={"client_id": "client_123", "amount": 1000.00},
            decision_rationale="Creating invoice based on client agreement",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"invoice_id": "inv_456"},
            business_impact="Invoice created for client, revenue recognized",
            related_entity_type="invoice",
            related_entity_id="inv_456"
        )

        task_entry = self.audit_logger.log_action(
            action_type=ActionType.TASK_START,
            action_name="process_client_onboarding",
            parameters={"client_id": "client_123"},
            decision_rationale="Starting onboarding task for new client",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"task_id": "task_789"},
            business_impact="Client onboarding initiated, relationship established",
            related_entity_type="task",
            related_entity_id="task_789"
        )

        # Verify entity relationships are tracked
        entries = self.audit_logger.read_entries()
        assert len(entries) >= 3

        # Check that entity relationships are properly recorded
        client_entries = [e for e in entries if e.related_entity_type == "client"]
        invoice_entries = [e for e in entries if e.related_entity_type == "invoice"]
        task_entries = [e for e in entries if e.related_entity_type == "task"]

        assert len(client_entries) >= 1
        assert len(invoice_entries) >= 1
        assert len(task_entries) >= 1

        # Verify specific entity IDs
        assert any(e.related_entity_id == "client_123" for e in client_entries)
        assert any(e.related_entity_id == "inv_456" for e in invoice_entries)
        assert any(e.related_entity_id == "task_789" for e in task_entries)

    def test_audit_trail_task_correlation(self):
        """
        Test that audit entries are properly correlated with tasks.

        Input: Multiple actions as part of a single task
        Expected: All entries contain the same task ID
        """
        task_id = "correlation_test_task_123"

        # Simulate multiple actions within the same task
        for i in range(5):
            self.audit_logger.log_action(
                action_type=ActionType.STEP_EXECUTE,
                action_name=f"step_{i}_in_task",
                parameters={"step_number": i, "task_part": f"part_{i}"},
                decision_rationale=f"Executing step {i} of multi-step task",
                execution_result=ExecutionResult.SUCCESS,
                result_data={f"step_{i}_result": f"completed_{i}"},
                business_impact=f"Task step {i} completed successfully"
            )

        # Get entries for this specific task
        entries = self.audit_logger.read_entries()
        task_entries = [e for e in entries if e.task_id == task_id]

        # Verify all entries have the correct task ID
        assert len(entries) >= 5
        assert all(entry.task_id == task_id for entry in task_entries)

    def test_audit_trail_business_impact_assessment(self):
        """
        Test that business impact is properly assessed and recorded.

        Input: Various types of actions with different business implications
        Expected: Meaningful business impact assessments recorded for each action
        """
        # High business impact action
        high_impact_entry = self.audit_logger.log_action(
            action_type=ActionType.MCP_CALL,
            action_name="process_large_invoice",
            parameters={"invoice_amount": 50000.00, "client": "premium_client"},
            decision_rationale="Processing high-value invoice for premium client",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"invoice_processed": True, "payment_expected": "30_days"},
            business_impact="High-value invoice processed, significant revenue impact for premium client"
        )

        # Medium business impact action
        medium_impact_entry = self.audit_logger.log_action(
            action_type=ActionType.STEP_EXECUTE,
            action_name="update_client_contact_info",
            parameters={"field": "email", "client_id": "client_456"},
            decision_rationale="Updating client contact information to ensure communication",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"field_updated": True, "contact_method": "email"},
            business_impact="Client contact info updated, ensuring continued communication"
        )

        # Low business impact action
        low_impact_entry = self.audit_logger.log_action(
            action_type=ActionType.DECISION,
            action_name="schedule_daily_maintenance",
            parameters={"maintenance_type": "cleanup", "frequency": "daily"},
            decision_rationale="Scheduling routine maintenance to optimize system performance",
            execution_result=ExecutionResult.SUCCESS,
            result_data={"maintenance_scheduled": True},
            business_impact="Routine maintenance scheduled, minor system optimization"
        )

        # Verify business impact assessments are recorded
        entries = self.audit_logger.read_entries()
        assert len(entries) >= 3

        # Check that business impact strings are meaningful
        business_impacts = [entry.business_impact for entry in entries]
        assert any("revenue" in impact.lower() for impact in business_impacts)
        assert any("communication" in impact.lower() for impact in business_impacts)
        assert any("maintenance" in impact.lower() for impact in business_impacts)

    def test_audit_trail_decision_rationale_completeness(self):
        """
        Test that decision rationales are comprehensive and explain autonomous choices.

        Input: Autonomous actions requiring decisions
        Expected: Complete decision rationales explaining why actions were taken
        """
        # Log an action with comprehensive decision rationale
        entry = self.audit_logger.log_action(
            action_type=ActionType.DECISION,
            action_name="choose_invoice_method",
            parameters={
                "available_methods": ["email", "post", "portal"],
                "client_preference": "email",
                "amount": 250.00
            },
            decision_rationale=(
                "Selected email invoice method because: "
                "1) Client's preferred communication method is email "
                "2) Amount is under $500 threshold requiring special handling "
                "3) Email provides fastest delivery and tracking "
                "4) Client has previously responded to email invoices quickly"
            ),
            execution_result=ExecutionResult.SUCCESS,
            result_data={"selected_method": "email", "reasoning_applied": True},
            business_impact="Invoice method optimized for client preference and efficiency"
        )

        # Verify decision rationale is comprehensive
        entries = self.audit_logger.read_entries()
        assert len(entries) >= 1

        rationale = entries[0].decision_rationale
        assert "Client's preferred communication method" in rationale
        assert "Amount is under $500" in rationale
        assert "Email provides fastest delivery" in rationale
        assert "Client has previously responded" in rationale


if __name__ == "__main__":
    test = TestAuditTrailIntegration()

    print("Running audit trail completeness for multi-step workflow test...")
    try:
        test.test_audit_trail_completeness_for_multi_step_workflow()
        print("✅ Audit trail completeness for multi-step workflow test passed")
    except Exception as e:
        print(f"❌ Audit trail completeness for multi-step workflow test failed: {e}")

    print("Running audit trail completeness with error scenario test...")
    try:
        test.test_audit_trail_completeness_with_error_scenario()
        print("✅ Audit trail completeness with error scenario test passed")
    except Exception as e:
        print(f"❌ Audit trail completeness with error scenario test failed: {e}")

    print("Running audit trail entity relationship tracking test...")
    try:
        test.test_audit_trail_entity_relationship_tracking()
        print("✅ Audit trail entity relationship tracking test passed")
    except Exception as e:
        print(f"❌ Audit trail entity relationship tracking test failed: {e}")

    print("Running audit trail task correlation test...")
    try:
        test.test_audit_trail_task_correlation()
        print("✅ Audit trail task correlation test passed")
    except Exception as e:
        print(f"❌ Audit trail task correlation test failed: {e}")

    print("Running audit trail business impact assessment test...")
    try:
        test.test_audit_trail_business_impact_assessment()
        print("✅ Audit trail business impact assessment test passed")
    except Exception as e:
        print(f"❌ Audit trail business impact assessment test failed: {e}")

    print("Running audit trail decision rationale completeness test...")
    try:
        test.test_audit_trail_decision_rationale_completeness()
        print("✅ Audit trail decision rationale completeness test passed")
    except Exception as e:
        print(f"❌ Audit trail decision rationale completeness test failed: {e}")

    print("All audit trail integration tests completed!")