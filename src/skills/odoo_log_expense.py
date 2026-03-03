"""
Odoo Log Expense Skill

Logs business expenses in Odoo with categorization and $500+ flagging.
This skill can be executed autonomously as part of multi-step workflows.
"""

from typing import Dict, Any
from src.mcp.odoo_client import OdooClient
from src.models.odoo_expense import OdooExpense
from src.audit.gold_logger import GoldAuditLogger


def odoo_log_expense(input_params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log an expense in Odoo with categorization and flagging

    Args:
        input_params: Expense data (category, amount, vendor, etc.)
        context: Workflow context

    Returns:
        Dictionary with expense logging results
    """
    audit_logger = GoldAuditLogger()

    try:
        # Create OdooExpense model (validates automatically)
        expense = OdooExpense.from_dict(input_params)

        # Check if expense requires audit flag (>= $500)
        audit_flag = expense.requires_audit_flag()

        if audit_flag:
            # Log high-value transaction
            audit_logger.log_action(
                action_type="DECISION",
                action_name="expense_flagged_for_audit",
                parameters={
                    "expense_id": expense.expense_id,
                    "amount": expense.amount,
                    "threshold": 500.0,
                },
                decision_rationale=f"Expense amount ${expense.amount:.2f} exceeds $500 threshold",
                execution_result="SUCCESS",
                result_data={"audit_flag": True},
                business_impact=f"High-value expense flagged for review: ${expense.amount:.2f}",
            )

        # Initialize Odoo client
        odoo_client = OdooClient()

        # Log expense in Odoo
        result = odoo_client.log_expense(expense)

        if result["status"] == "success":
            # Save expense locally
            expense_path = expense.save(directory="Done")

            # Log success
            audit_logger.log_action(
                action_type="STEP_EXECUTE",
                action_name="odoo_log_expense",
                parameters=input_params,
                decision_rationale="Logging expense in Odoo",
                execution_result="SUCCESS",
                result_data={
                    "expense_id": expense.expense_id,
                    "odoo_id": expense.odoo_id,
                    "amount": expense.amount,
                    "category": expense.category.value,
                    "audit_flag": audit_flag,
                },
                business_impact=f"Expense logged: ${expense.amount:.2f} for {expense.category.value}",
            )

            return {
                "success": True,
                "expense_id": expense.expense_id,
                "odoo_id": expense.odoo_id,
                "amount": expense.amount,
                "category": expense.category.value,
                "audit_flag": audit_flag,
                "file_path": expense_path,
            }
        else:
            # Queued or failed
            # Still save locally even if Odoo sync failed
            expense_path = expense.save(directory="Needs_Action")

            return {
                "success": False,
                "expense_id": expense.expense_id,
                "message": result.get("message", "Expense logging failed"),
                "queued": result["status"] == "queued",
                "file_path": expense_path,
            }

    except ValueError as e:
        # Validation error
        audit_logger.log_action(
            action_type="ERROR",
            action_name="expense_validation_failed",
            parameters=input_params,
            decision_rationale="Expense validation failed",
            execution_result="FAILURE",
            result_data={},
            business_impact="Expense not logged due to validation error",
            error_details={
                "error_type": "ValidationError",
                "error_message": str(e),
                "recovery_attempted": False,
                "recovery_result": "N/A",
            },
        )

        raise

    except Exception as e:
        # Other error
        audit_logger.log_action(
            action_type="ERROR",
            action_name="odoo_log_expense_failed",
            parameters=input_params,
            decision_rationale="Expense logging failed",
            execution_result="FAILURE",
            result_data={},
            business_impact="Expense logging unavailable",
            error_details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "recovery_attempted": False,
                "recovery_result": "N/A",
            },
        )

        raise
