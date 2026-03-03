"""
Ralph Wiggum Loop Engine for Gold Tier Autonomous Execution

This engine implements the core autonomous reasoning loop:
1. Execute current step
2. Check "Is there a next step?"
3. If yes, continue to next step
4. If no, check "Did I achieve the final outcome?"
5. Mark task as completed or failed based on outcome verification

Key Features:
- Multi-step workflow execution with state persistence
- Automatic error recovery with retry logic
- Circuit breaker integration for MCP server failures
- Comprehensive audit logging for all actions
- Priority-based task execution (P0-P3)
- Graceful degradation when services fail
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import json
import os
from pathlib import Path

from src.models.autonomous_task import AutonomousTask, OutcomeStatus, Priority
from src.models.step import StepSchema, StepStatus
from src.audit.gold_logger import GoldAuditLogger
from src.utils.circuit_breaker import CircuitBreaker
from src.utils.retry import retry_with_backoff
from src.utils.dashboard_updater import DashboardUpdater


class RalphWiggumLoopEngine:
    """
    Core autonomous execution engine implementing the Ralph Wiggum Loop pattern

    The engine executes multi-step workflows autonomously by:
    1. Loading task state from persistent storage
    2. Executing each step with error handling and retry logic
    3. Checking for next steps after each execution
    4. Verifying final outcome when all steps complete
    5. Logging all actions to tamper-evident audit trail
    """

    def __init__(
        self,
        audit_logger: Optional[GoldAuditLogger] = None,
        dashboard_updater: Optional[DashboardUpdater] = None,
        state_directory: str = "Needs_Action",
        done_directory: str = "Done",
    ):
        """
        Initialize the Ralph Wiggum Loop engine

        Args:
            audit_logger: Gold audit logger for tamper-evident logging
            dashboard_updater: Dashboard updater for real-time status
            state_directory: Directory for active task state files
            done_directory: Directory for completed task archives
        """
        self.audit_logger = audit_logger or GoldAuditLogger()
        self.dashboard_updater = dashboard_updater or DashboardUpdater()
        self.state_directory = state_directory
        self.done_directory = done_directory

        # Create directories if they don't exist
        os.makedirs(self.state_directory, exist_ok=True)
        os.makedirs(self.done_directory, exist_ok=True)

        # Action registry: maps action names to callable functions
        self.action_registry: Dict[str, Callable] = {}

        # Circuit breakers for external services
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

        # Active workflows counter
        self.active_workflows = 0

    def register_action(self, action_name: str, action_func: Callable) -> None:
        """
        Register an action handler for workflow steps

        Args:
            action_name: Name of the action (e.g., "detect_trend", "create_post")
            action_func: Callable that executes the action
        """
        self.action_registry[action_name] = action_func
        print(f"[Engine] Registered action: {action_name}")

    def register_circuit_breaker(self, service_name: str, circuit_breaker: CircuitBreaker) -> None:
        """
        Register a circuit breaker for an external service

        Args:
            service_name: Name of the service (e.g., "odoo", "twitter")
            circuit_breaker: CircuitBreaker instance for the service
        """
        self.circuit_breakers[service_name] = circuit_breaker
        print(f"[Engine] Registered circuit breaker: {service_name}")

    def execute_task(self, task: AutonomousTask) -> AutonomousTask:
        """
        Execute a multi-step autonomous task using the Ralph Wiggum Loop

        This is the main entry point for autonomous execution. It:
        1. Validates the task
        2. Executes steps sequentially
        3. Checks for next steps after each execution
        4. Verifies final outcome
        5. Persists state after each step

        Args:
            task: AutonomousTask to execute

        Returns:
            Updated AutonomousTask with execution results
        """
        # Log task start
        self.audit_logger.log_action(
            action_type="TASK_START",
            action_name=f"start_workflow_{task.workflow_name}",
            parameters={
                "task_id": task.task_id,
                "workflow_name": task.workflow_name,
                "original_intent": task.original_intent,
                "total_steps": task.total_steps,
                "priority": task.priority.value,
            },
            decision_rationale=f"Starting autonomous execution of {task.workflow_name} workflow",
            execution_result="SUCCESS",
            result_data={"task_id": task.task_id},
            business_impact=f"Initiated {task.total_steps}-step workflow for: {task.original_intent}",
        )

        # Update dashboard
        self.active_workflows += 1
        self._update_dashboard_status(task)

        try:
            # Execute the Ralph Wiggum Loop
            while True:
                # Get current step
                current_step = task.get_current_step()

                if current_step is None:
                    # No more steps to execute
                    break

                # Execute the step
                step_result = self._execute_step(task, current_step)

                # Check if step failed
                if step_result["status"] == StepStatus.FAILED:
                    # Attempt error recovery
                    recovery_result = self._attempt_recovery(task, current_step, step_result["error"])

                    if not recovery_result["recovered"]:
                        # Recovery failed, mark task as failed
                        task.mark_failed(f"Step {current_step.step_number} failed: {step_result['error']}")
                        self._save_task_state(task)

                        # Log task failure
                        self.audit_logger.log_action(
                            action_type="TASK_COMPLETE",
                            action_name=f"fail_workflow_{task.workflow_name}",
                            parameters={"task_id": task.task_id},
                            decision_rationale="Task failed due to unrecoverable step failure",
                            execution_result="FAILURE",
                            result_data={"failure_reason": step_result["error"]},
                            business_impact=f"Workflow failed at step {current_step.step_number}",
                            error_details={
                                "error_type": "StepExecutionError",
                                "error_message": step_result["error"],
                                "recovery_attempted": True,
                                "recovery_result": recovery_result["message"],
                            },
                        )

                        break

                # Step succeeded, advance to next step
                task.advance_step()
                self._save_task_state(task)

                # Ralph Wiggum Loop Check #1: "Is there a next step?"
                if not task.has_next_step():
                    # No more steps, proceed to outcome verification
                    break

            # Ralph Wiggum Loop Check #2: "Did I achieve the final outcome?"
            if task.outcome_status == OutcomeStatus.IN_PROGRESS:
                outcome_verified = self._verify_final_outcome(task)

                if outcome_verified:
                    task.mark_completed()
                    self._archive_completed_task(task)

                    # Log task completion
                    self.audit_logger.log_action(
                        action_type="TASK_COMPLETE",
                        action_name=f"complete_workflow_{task.workflow_name}",
                        parameters={"task_id": task.task_id},
                        decision_rationale="All steps completed and final outcome verified",
                        execution_result="SUCCESS",
                        result_data={
                            "completed_steps": len(task.completed_steps),
                            "total_steps": task.total_steps,
                        },
                        business_impact=f"Successfully completed workflow: {task.original_intent}",
                    )
                else:
                    task.mark_failed("Final outcome verification failed")
                    self._save_task_state(task)

                    # Log outcome verification failure
                    self.audit_logger.log_action(
                        action_type="TASK_COMPLETE",
                        action_name=f"fail_workflow_{task.workflow_name}",
                        parameters={"task_id": task.task_id},
                        decision_rationale="Final outcome did not match original intent",
                        execution_result="FAILURE",
                        result_data={"reason": "outcome_verification_failed"},
                        business_impact="Workflow completed but did not achieve intended outcome",
                    )

        finally:
            # Update dashboard
            self.active_workflows -= 1
            self._update_dashboard_status(task)

        return task

    def _execute_step(self, task: AutonomousTask, step: StepSchema) -> Dict[str, Any]:
        """
        Execute a single workflow step with retry logic

        Args:
            task: Parent AutonomousTask
            step: Step to execute

        Returns:
            Dictionary with execution result
        """
        # Mark step as started
        step.start()

        # Log step execution start
        self.audit_logger.log_action(
            action_type="STEP_EXECUTE",
            action_name=step.action,
            parameters={
                "task_id": task.task_id,
                "step_number": step.step_number,
                "input": step.input,
            },
            decision_rationale=f"Executing step {step.step_number + 1}/{task.total_steps}: {step.action}",
            execution_result="SUCCESS",
            result_data={},
            business_impact=f"Processing step: {step.action}",
        )

        # Get action handler
        action_func = self.action_registry.get(step.action)

        if action_func is None:
            error_msg = f"No handler registered for action: {step.action}"
            step.fail(error_msg)
            return {"status": StepStatus.FAILED, "error": error_msg}

        # Execute action with retry logic
        try:
            @retry_with_backoff(max_attempts=3, exceptions=(Exception,))
            def execute_with_retry():
                return action_func(step.input, task.context)

            result = execute_with_retry()

            # Mark step as completed
            step.complete(result)

            # Update task context with step output
            task.update_context(f"step_{step.step_number}_output", result)

            return {"status": StepStatus.SUCCESS, "output": result}

        except Exception as e:
            error_msg = f"Step execution failed: {str(e)}"
            step.fail(error_msg)

            # Log step failure
            self.audit_logger.log_action(
                action_type="ERROR",
                action_name=f"step_failed_{step.action}",
                parameters={
                    "task_id": task.task_id,
                    "step_number": step.step_number,
                },
                decision_rationale="Step execution encountered an error",
                execution_result="FAILURE",
                result_data={},
                business_impact=f"Step {step.step_number} failed",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "recovery_attempted": False,
                    "recovery_result": "pending",
                },
            )

            return {"status": StepStatus.FAILED, "error": error_msg}

    def _attempt_recovery(
        self,
        task: AutonomousTask,
        failed_step: StepSchema,
        error: str,
    ) -> Dict[str, Any]:
        """
        Attempt to recover from a failed step

        Recovery strategies:
        1. Retry with exponential backoff (already attempted in _execute_step)
        2. Try alternative execution path if available
        3. Skip non-critical steps
        4. Pause for human intervention if critical

        Args:
            task: Parent AutonomousTask
            failed_step: Step that failed
            error: Error message

        Returns:
            Dictionary with recovery result
        """
        # Log recovery attempt
        self.audit_logger.log_action(
            action_type="ERROR",
            action_name="attempt_recovery",
            parameters={
                "task_id": task.task_id,
                "failed_step": failed_step.step_number,
                "error": error,
            },
            decision_rationale="Attempting automatic error recovery",
            execution_result="SUCCESS",
            result_data={},
            business_impact="Initiating error recovery",
        )

        # Check if step can be skipped (non-critical steps)
        if self._is_step_skippable(failed_step):
            failed_step.skip(f"Skipped due to error: {error}")
            return {
                "recovered": True,
                "strategy": "skip",
                "message": "Step skipped as non-critical",
            }

        # Check if alternative path exists
        alternative_action = self._get_alternative_action(failed_step.action)
        if alternative_action:
            # Try alternative action
            try:
                alt_func = self.action_registry.get(alternative_action)
                if alt_func:
                    result = alt_func(failed_step.input, task.context)
                    failed_step.complete(result)
                    return {
                        "recovered": True,
                        "strategy": "alternative_path",
                        "message": f"Used alternative action: {alternative_action}",
                    }
            except Exception as e:
                pass  # Alternative also failed

        # Recovery failed, pause for human intervention if critical
        if task.priority in [Priority.P0, Priority.P1]:
            task.mark_paused(f"Critical step failed: {error}")
            return {
                "recovered": False,
                "strategy": "pause_for_human",
                "message": "Critical step failed, paused for human intervention",
            }

        # No recovery possible
        return {
            "recovered": False,
            "strategy": "none",
            "message": "No recovery strategy available",
        }

    def _verify_final_outcome(self, task: AutonomousTask) -> bool:
        """
        Verify that the final outcome matches the original intent

        This is the second Ralph Wiggum Loop check: "Did I achieve the final outcome?"

        Args:
            task: Completed AutonomousTask

        Returns:
            True if outcome verified, False otherwise
        """
        # Log outcome verification
        self.audit_logger.log_action(
            action_type="DECISION",
            action_name="verify_outcome",
            parameters={
                "task_id": task.task_id,
                "original_intent": task.original_intent,
                "completed_steps": len(task.completed_steps),
            },
            decision_rationale="Verifying final outcome matches original intent",
            execution_result="SUCCESS",
            result_data={},
            business_impact="Outcome verification in progress",
        )

        # Check that all steps completed successfully
        all_steps_successful = all(
            step.status == StepStatus.SUCCESS
            for step in task.completed_steps
        )

        if not all_steps_successful:
            return False

        # Check that we completed all expected steps
        if len(task.completed_steps) != task.total_steps:
            return False

        # Workflow-specific outcome verification
        # This can be extended with custom verification logic per workflow
        outcome_checks = {
            "trend_to_post_to_expense": self._verify_trend_to_post_outcome,
            "invoice_creation": self._verify_invoice_outcome,
            "social_broadcast": self._verify_social_broadcast_outcome,
        }

        verification_func = outcome_checks.get(task.workflow_name)
        if verification_func:
            return verification_func(task)

        # Default: if all steps succeeded, outcome is verified
        return True

    def _verify_trend_to_post_outcome(self, task: AutonomousTask) -> bool:
        """Verify trend-to-post-to-expense workflow outcome"""
        # Check that we have post output and expense output
        post_output = task.get_context("step_1_output")  # Assuming step 1 is create_post
        expense_output = task.get_context("step_2_output")  # Assuming step 2 is log_expense

        return post_output is not None and expense_output is not None

    def _verify_invoice_outcome(self, task: AutonomousTask) -> bool:
        """Verify invoice creation workflow outcome"""
        # Check that invoice was created and synced to Odoo
        invoice_output = task.get_context("step_0_output")
        return invoice_output is not None and "invoice_id" in invoice_output

    def _verify_social_broadcast_outcome(self, task: AutonomousTask) -> bool:
        """Verify social media broadcast workflow outcome"""
        # Check that post was published to at least one platform
        post_output = task.get_context("step_0_output")
        if post_output is None:
            return False

        platforms_published = post_output.get("platforms_published", [])
        return len(platforms_published) > 0

    def _is_step_skippable(self, step: StepSchema) -> bool:
        """Check if a step can be skipped (non-critical)"""
        # Define skippable actions (e.g., optional notifications, analytics)
        skippable_actions = [
            "send_notification",
            "update_analytics",
            "log_metrics",
        ]
        return step.action in skippable_actions

    def _get_alternative_action(self, action: str) -> Optional[str]:
        """Get alternative action for graceful degradation"""
        # Define alternative actions for common failures
        alternatives = {
            "post_to_twitter": "queue_twitter_post",
            "post_to_facebook": "queue_facebook_post",
            "post_to_instagram": "queue_instagram_post",
            "sync_to_odoo": "queue_odoo_sync",
        }
        return alternatives.get(action)

    def _save_task_state(self, task: AutonomousTask) -> None:
        """Save task state to persistent storage"""
        task.save(directory=self.state_directory)

    def _archive_completed_task(self, task: AutonomousTask) -> None:
        """Move completed task to archive directory"""
        # Save to Done directory
        task.save(directory=self.done_directory)

        # Remove from active state directory
        state_file = os.path.join(self.state_directory, f"state_{task.task_id}.json")
        if os.path.exists(state_file):
            os.remove(state_file)

    def _update_dashboard_status(self, task: AutonomousTask) -> None:
        """Update Dashboard.md with current task status"""
        self.dashboard_updater.update_gold_tier_status(
            autonomous_mode=True,
            active_workflows=self.active_workflows,
            current_task=task.workflow_name if task.outcome_status == OutcomeStatus.IN_PROGRESS else None,
            priority=task.priority.value,
        )

    def load_task(self, task_id: str) -> Optional[AutonomousTask]:
        """
        Load a task from persistent storage

        Args:
            task_id: Task ID to load

        Returns:
            AutonomousTask or None if not found
        """
        try:
            return AutonomousTask.load(task_id, directory=self.state_directory)
        except FileNotFoundError:
            return None

    def list_active_tasks(self) -> List[AutonomousTask]:
        """
        List all active tasks in the state directory

        Returns:
            List of AutonomousTask instances
        """
        tasks = []
        state_dir = Path(self.state_directory)

        for state_file in state_dir.glob("state_*.json"):
            try:
                with open(state_file, "r") as f:
                    data = json.load(f)
                    task = AutonomousTask.from_dict(data)
                    tasks.append(task)
            except Exception as e:
                print(f"[Engine] Error loading task from {state_file}: {e}")

        return tasks

    def resume_task(self, task_id: str) -> Optional[AutonomousTask]:
        """
        Resume a paused task

        Args:
            task_id: Task ID to resume

        Returns:
            Updated AutonomousTask or None if not found
        """
        task = self.load_task(task_id)

        if task is None:
            return None

        if task.outcome_status != OutcomeStatus.PAUSED:
            print(f"[Engine] Task {task_id} is not paused (status: {task.outcome_status})")
            return task

        # Resume the task
        task.resume()

        # Continue execution
        return self.execute_task(task)

    def rollback_task(self, task: AutonomousTask, rollback_to_step: Optional[int] = None) -> bool:
        """
        Rollback a failed workflow to a previous state

        This implements the rollback capability for failed workflows by:
        1. Identifying which steps need to be undone
        2. Executing rollback actions for each step (if defined)
        3. Restoring task state to the rollback point
        4. Logging all rollback actions to audit trail

        Args:
            task: AutonomousTask to rollback
            rollback_to_step: Step number to rollback to (None = rollback all)

        Returns:
            True if rollback successful, False otherwise
        """
        # Log rollback initiation
        self.audit_logger.log_action(
            action_type="ERROR",
            action_name="initiate_rollback",
            parameters={
                "task_id": task.task_id,
                "current_step": task.current_step,
                "rollback_to_step": rollback_to_step,
                "completed_steps": len(task.completed_steps),
            },
            decision_rationale=f"Initiating rollback for failed workflow: {task.workflow_name}",
            execution_result="SUCCESS",
            result_data={},
            business_impact="Starting rollback to restore system state",
        )

        # Determine which steps to rollback
        if rollback_to_step is None:
            # Rollback all completed steps
            steps_to_rollback = list(reversed(task.completed_steps))
        else:
            # Rollback to specific step
            steps_to_rollback = [
                step for step in reversed(task.completed_steps)
                if step.step_number > rollback_to_step
            ]

        rollback_success = True
        rollback_errors = []

        # Execute rollback for each step
        for step in steps_to_rollback:
            try:
                rollback_result = self._rollback_step(task, step)

                if not rollback_result["success"]:
                    rollback_success = False
                    rollback_errors.append({
                        "step": step.step_number,
                        "action": step.action,
                        "error": rollback_result["error"],
                    })

                    # Log rollback failure
                    self.audit_logger.log_action(
                        action_type="ERROR",
                        action_name=f"rollback_failed_{step.action}",
                        parameters={
                            "task_id": task.task_id,
                            "step_number": step.step_number,
                        },
                        decision_rationale=f"Failed to rollback step {step.step_number}",
                        execution_result="FAILURE",
                        result_data=rollback_result,
                        business_impact=f"Rollback incomplete for step: {step.action}",
                        error_details={
                            "error_type": "RollbackError",
                            "error_message": rollback_result["error"],
                            "recovery_attempted": False,
                            "recovery_result": "N/A",
                        },
                    )

            except Exception as e:
                rollback_success = False
                error_msg = f"Exception during rollback of step {step.step_number}: {str(e)}"
                rollback_errors.append({
                    "step": step.step_number,
                    "action": step.action,
                    "error": error_msg,
                })

                # Log exception
                self.audit_logger.log_action(
                    action_type="ERROR",
                    action_name="rollback_exception",
                    parameters={
                        "task_id": task.task_id,
                        "step_number": step.step_number,
                    },
                    decision_rationale="Exception occurred during rollback",
                    execution_result="FAILURE",
                    result_data={},
                    business_impact="Rollback interrupted by exception",
                    error_details={
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "recovery_attempted": False,
                        "recovery_result": "N/A",
                    },
                )

        # Update task state after rollback
        if rollback_to_step is not None:
            # Restore to specific step
            task.completed_steps = [
                step for step in task.completed_steps
                if step.step_number <= rollback_to_step
            ]
            task.current_step = rollback_to_step
        else:
            # Complete rollback - reset to initial state
            task.completed_steps = []
            task.current_step = 0
            task.outcome_status = OutcomeStatus.PENDING

        # Save rolled-back state
        self._save_task_state(task)

        # Log rollback completion
        self.audit_logger.log_action(
            action_type="ERROR",
            action_name="complete_rollback",
            parameters={
                "task_id": task.task_id,
                "rollback_success": rollback_success,
                "steps_rolled_back": len(steps_to_rollback),
                "errors": rollback_errors,
            },
            decision_rationale="Rollback operation completed",
            execution_result="SUCCESS" if rollback_success else "PARTIAL",
            result_data={
                "final_step": task.current_step,
                "remaining_completed_steps": len(task.completed_steps),
            },
            business_impact=f"Rollback {'successful' if rollback_success else 'partially successful'} - {len(steps_to_rollback)} steps processed",
        )

        return rollback_success

    def _rollback_step(self, task: AutonomousTask, step: StepSchema) -> Dict[str, Any]:
        """
        Rollback a single step by executing its inverse action

        Args:
            task: Parent AutonomousTask
            step: Step to rollback

        Returns:
            Dictionary with rollback result
        """
        # Define rollback actions for each action type
        rollback_actions = {
            "create_invoice": "delete_invoice",
            "create_expense": "delete_expense",
            "create_social_post": "delete_social_post",
            "post_to_twitter": "delete_twitter_post",
            "post_to_facebook": "delete_facebook_post",
            "post_to_instagram": "delete_instagram_post",
            "sync_to_odoo": "unsync_from_odoo",
            "send_email": None,  # Cannot rollback sent emails
            "send_notification": None,  # Cannot rollback notifications
        }

        rollback_action = rollback_actions.get(step.action)

        if rollback_action is None:
            # No rollback action defined (irreversible action)
            return {
                "success": True,
                "message": f"Step {step.action} is irreversible, skipping rollback",
                "skipped": True,
            }

        # Get rollback handler
        rollback_func = self.action_registry.get(rollback_action)

        if rollback_func is None:
            return {
                "success": False,
                "error": f"No rollback handler registered for: {rollback_action}",
                "skipped": False,
            }

        # Execute rollback action
        try:
            # Use step output as input for rollback (e.g., invoice_id to delete)
            rollback_result = rollback_func(step.output, task.context)

            return {
                "success": True,
                "message": f"Successfully rolled back {step.action}",
                "result": rollback_result,
                "skipped": False,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Rollback failed: {str(e)}",
                "skipped": False,
            }
