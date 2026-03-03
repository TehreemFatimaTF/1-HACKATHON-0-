"""
Odoo Fetch Ledger Skill

Fetches accounting summaries and ledger data from Odoo.
This skill can be executed autonomously as part of multi-step workflows.
"""

from typing import Dict, Any, Optional
from datetime import date, timedelta
from src.mcp.odoo_client import OdooClient
from src.audit.gold_logger import GoldAuditLogger


def odoo_fetch_ledger(input_params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch accounting summary from Odoo

    Args:
        input_params: Optional date range filters (start_date, end_date)
        context: Workflow context

    Returns:
        Dictionary with accounting summary (revenue, expenses, cash flow)
    """
    audit_logger = GoldAuditLogger()

    try:
        # Extract date range from input params
        start_date = input_params.get("start_date")
        end_date = input_params.get("end_date")

        # Default to current month if no dates provided
        if not start_date:
            start_date = date.today().replace(day=1).isoformat()
        if not end_date:
            end_date = date.today().isoformat()

        # Initialize Odoo client
        odoo_client = OdooClient()

        # Fetch accounting summary
        result = odoo_client.get_accounting_summary(start_date, end_date)

        if result["status"] == "success":
            summary = result["data"]

            # Log success
            audit_logger.log_action(
                action_type="STEP_EXECUTE",
                action_name="odoo_fetch_ledger",
                parameters={"start_date": start_date, "end_date": end_date},
                decision_rationale="Fetching accounting summary from Odoo",
                execution_result="SUCCESS",
                result_data=summary,
                business_impact=f"Retrieved accounting data: Revenue ${summary['revenue']:.2f}, "
                               f"Expenses ${summary['expenses']:.2f}, "
                               f"Cash Flow ${summary['cash_flow']:.2f}",
            )

            return {
                "success": True,
                "summary": summary,
                "period": {
                    "start": start_date,
                    "end": end_date,
                },
            }
        else:
            # Queued or failed
            return {
                "success": False,
                "message": result.get("message", "Ledger fetch failed"),
                "queued": result["status"] == "queued",
            }

    except Exception as e:
        # Log error
        audit_logger.log_action(
            action_type="ERROR",
            action_name="odoo_fetch_ledger_failed",
            parameters=input_params,
            decision_rationale="Ledger fetch failed",
            execution_result="FAILURE",
            result_data={},
            business_impact="Accounting summary unavailable",
            error_details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "recovery_attempted": False,
                "recovery_result": "N/A",
            },
        )

        raise


def get_monthly_summary(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get current month's accounting summary

    Args:
        context: Workflow context

    Returns:
        Dictionary with monthly summary
    """
    today = date.today()
    start_date = today.replace(day=1).isoformat()
    end_date = today.isoformat()

    return odoo_fetch_ledger(
        {"start_date": start_date, "end_date": end_date},
        context
    )


def get_quarterly_summary(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get current quarter's accounting summary

    Args:
        context: Workflow context

    Returns:
        Dictionary with quarterly summary
    """
    today = date.today()
    quarter_start_month = ((today.month - 1) // 3) * 3 + 1
    start_date = today.replace(month=quarter_start_month, day=1).isoformat()
    end_date = today.isoformat()

    return odoo_fetch_ledger(
        {"start_date": start_date, "end_date": end_date},
        context
    )


def get_yearly_summary(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get current year's accounting summary

    Args:
        context: Workflow context

    Returns:
        Dictionary with yearly summary
    """
    today = date.today()
    start_date = today.replace(month=1, day=1).isoformat()
    end_date = today.isoformat()

    return odoo_fetch_ledger(
        {"start_date": start_date, "end_date": end_date},
        context
    )
