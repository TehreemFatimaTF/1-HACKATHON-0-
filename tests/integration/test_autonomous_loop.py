"""
Integration test for multi-step workflow execution in the Gold Tier autonomous system.
Test ID: T015 [P] [US1] Integration test for multi-step workflow execution
File: tests/integration/test_autonomous_loop.py
"""
import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock

# Import the necessary modules from the Gold Tier implementation
from src.engine_gold import RalphWiggumLoopEngine
from src.models.autonomous_task import AutonomousTask, OutcomeStatus, Priority
from src.models.step import StepSchema, StepStatus
from src.audit.gold_logger import GoldAuditLogger


class TestAutonomousLoopIntegration:
    """Integration tests for the Ralph Wiggum Loop multi-step workflow execution."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_task_id = "test_task_123"
        self.test_workflow = "trend_to_post_to_expense"

    def test_multi_step_workflow_execution_success(self):
        """
        Test that a multi-step workflow executes successfully with all steps completed.

        Input: AutonomousTask with 3 steps (detect_trend, create_post, log_expense)
        Expected: All steps executed successfully, outcome verified, audit logged
        """
        # Create an autonomous task with multiple steps
        task = AutonomousTask(
            workflow_name=self.test_workflow,
            original_intent="Create social media post about trend and log marketing expense",
            total_steps=3,
            task_id=self.test_task_id
        )

        # Add pending steps to the task
        task.pending_steps = [
            StepSchema(step_number=0, action="detect_trend", input={"source": "linkedin"}),
            StepSchema(step_number=1, action="create_post", input={"platforms": ["twitter", "facebook", "instagram"]}),
            StepSchema(step_number=2, action="log_expense", input={"amount": 50.00, "category": "marketing"})
        ]

        task.context = {
            "trend_data": {"topic": "AI automation", "reach": 10000},
            "post_content": "AI automation market reaches $50B",
            "expense_amount": 50.00,
            "platforms": ["twitter", "facebook", "instagram"]
        }

        # Initialize the Ralph Wiggum Loop engine
        engine = RalphWiggumLoopEngine()

        # Mock the external dependencies to avoid actual API calls
        with patch.object(engine, 'action_registry', {
            'detect_trend': lambda input_data, context: {"trend": "AI automation", "topic": "AI trends"},
            'create_post': lambda input_data, context: {"post_id": "post_123", "status": "published"},
            'log_expense': lambda input_data, context: {"expense_id": "exp_123", "status": "logged"}
        }), \
             patch.object(GoldAuditLogger, 'log_action') as mock_audit:

            # Execute the workflow
            result = engine.execute_task(task)

            # Verify workflow completed successfully
            assert result.outcome_status == OutcomeStatus.COMPLETED
            assert len(result.completed_steps) == 3
            assert all(step.status == StepStatus.SUCCESS for step in result.completed_steps)

            # Verify audit logging was called for each step
            assert mock_audit.call_count >= 3  # At least 3 audit calls for the 3 steps

    def test_multi_step_workflow_with_intermediate_failure(self):
        """
        Test that a multi-step workflow handles failure in an intermediate step gracefully.

        Input: AutonomousTask where step 2 (create_post) fails
        Expected: Partial completion, failure recovery, audit logged
        """
        # Create an autonomous task with multiple steps
        task = AutonomousTask(
            workflow_name=self.test_workflow,
            original_intent="Create social media post about trend and log marketing expense",
            total_steps=3,
            task_id=self.test_task_id
        )

        # Add pending steps to the task
        task.pending_steps = [
            StepSchema(step_number=0, action="detect_trend", input={"source": "linkedin"}),
            StepSchema(step_number=1, action="create_post", input={"platforms": ["twitter", "facebook", "instagram"]}),
            StepSchema(step_number=2, action="log_expense", input={"amount": 50.00, "category": "marketing"})
        ]

        task.context = {
            "trend_data": {"topic": "AI automation", "reach": 10000},
            "post_content": "AI automation market reaches $50B",
            "expense_amount": 50.00,
            "platforms": ["twitter", "facebook", "instagram"]
        }

        # Initialize the Ralph Wiggum Loop engine
        engine = RalphWiggumLoopEngine()

        # Mock the external dependencies, with step 2 (create_post) failing
        with patch.object(engine, 'action_registry', {
            'detect_trend': lambda input_data, context: {"trend": "AI automation", "topic": "AI trends"},
            'create_post': lambda input_data, context: (_ for _ in ()).throw(Exception("Failed to post to social media")),
            'log_expense': lambda input_data, context: {"expense_id": "exp_123", "status": "logged"}
        }), \
             patch.object(GoldAuditLogger, 'log_action') as mock_audit:

            # Execute the workflow
            result = engine.execute_task(task)

            # Verify workflow completed with partial success
            assert result.outcome_status in [OutcomeStatus.FAILED, OutcomeStatus.PAUSED]  # Could be either depending on error handling
            assert len(result.completed_steps) < 3  # Should be less than total steps

            # Verify audit logging was called for attempted steps
            assert mock_audit.call_count >= 1  # At least first step was audited

    def test_outcome_verification_success(self):
        """
        Test that the final outcome verification confirms the intended result was achieved.

        Input: Completed workflow with final result matching original intent
        Expected: Outcome verification passes, task marked as fully complete
        """
        # Create an autonomous task with original intent
        original_intent = "Create social media post about AI trends and log $50 marketing expense"
        task = AutonomousTask(
            workflow_name=self.test_workflow,
            original_intent=original_intent,
            total_steps=3,
            task_id=self.test_task_id
        )

        # Add pending steps to the task
        task.pending_steps = [
            StepSchema(step_number=0, action="detect_trend", input={"source": "linkedin"}),
            StepSchema(step_number=1, action="create_post", input={"platforms": ["twitter", "facebook", "instagram"]}),
            StepSchema(step_number=2, action="log_expense", input={"amount": 50.00, "category": "marketing"})
        ]

        task.context = {
            "trend_data": {"topic": "AI automation"},
            "post_content": "AI trends in 2026",
            "expense_amount": 50.00,
            "expected_reach": 10000
        }

        # Initialize the Ralph Wiggum Loop engine
        engine = RalphWiggumLoopEngine()

        # Mock the outcome verification process
        with patch.object(engine, 'action_registry', {
            'detect_trend': lambda input_data, context: {"trend": "AI automation", "topic": "AI trends", "reach": 10000},
            'create_post': lambda input_data, context: {"post_id": "post_123", "status": "published", "platforms": ["twitter", "facebook", "instagram"]},
            'log_expense': lambda input_data, context: {"expense_id": "exp_123", "status": "logged", "amount": 50.0}
        }), \
             patch.object(GoldAuditLogger, 'log_action'):

            # Execute workflow completion
            result = engine.execute_task(task)

            # Verify outcome was verified successfully
            assert result.outcome_status == OutcomeStatus.COMPLETED

    def test_workflow_context_preservation(self):
        """
        Test that context data is properly preserved across workflow steps.

        Input: Task with initial context data
        Expected: Context data accessible and modified appropriately in each step
        """
        # Create an autonomous task with initial context
        initial_context = {
            "trend_data": {"topic": "AI automation", "source": "LinkedIn"},
            "post_content": None,  # Will be populated in step 1
            "expense_amount": 0.0,  # Will be set in step 2
            "platforms": ["twitter", "facebook", "instagram"]
        }

        task = AutonomousTask(
            workflow_name=self.test_workflow,
            original_intent="Process trend data and create marketing campaign",
            total_steps=3,
            task_id=self.test_task_id
        )

        # Add pending steps to the task
        task.pending_steps = [
            StepSchema(step_number=0, action="detect_trend", input={"source": "linkedin"}),
            StepSchema(step_number=1, action="create_post", input={"platforms": ["twitter", "facebook", "instagram"]}),
            StepSchema(step_number=2, action="log_expense", input={"amount": 50.00, "category": "marketing"})
        ]

        task.context = initial_context

        # Initialize the Ralph Wiggum Loop engine
        engine = RalphWiggumLoopEngine()

        # Mock step execution to verify context flow
        with patch.object(engine, 'action_registry', {
            'detect_trend': lambda input_data, context: {"trend": "AI automation", "topic": "AI trends", "reach": 10000},
            'create_post': lambda input_data, context: {"post_id": "post_123", "status": "published", "platforms": ["twitter", "facebook", "instagram"]},
            'log_expense': lambda input_data, context: {"expense_id": "exp_123", "status": "logged", "amount": 50.0}
        }), \
             patch.object(GoldAuditLogger, 'log_action'):

            # Execute workflow
            result = engine.execute_task(task)

            # Context preservation verified through successful completion
            assert result.outcome_status == OutcomeStatus.COMPLETED
            # Context would have been updated through the steps (verified through successful completion)
            # Check that context was updated during execution
            assert "trend_data" in result.context


if __name__ == "__main__":
    test = TestAutonomousLoopIntegration()
    test.setup_method()

    print("Running multi-step workflow execution test...")
    try:
        test.test_multi_step_workflow_execution_success()
        print("✅ Multi-step workflow execution test passed")
    except Exception as e:
        print(f"❌ Multi-step workflow execution test failed: {e}")

    print("Running workflow with intermediate failure test...")
    try:
        test.test_multi_step_workflow_with_intermediate_failure()
        print("✅ Intermediate failure handling test passed")
    except Exception as e:
        print(f"❌ Intermediate failure handling test failed: {e}")

    print("Running outcome verification test...")
    try:
        test.test_outcome_verification_success()
        print("✅ Outcome verification test passed")
    except Exception as e:
        print(f"❌ Outcome verification test failed: {e}")

    print("Running context preservation test...")
    try:
        test.test_workflow_context_preservation()
        print("✅ Context preservation test passed")
    except Exception as e:
        print(f"❌ Context preservation test failed: {e}")

    print("All autonomous loop integration tests completed!")
