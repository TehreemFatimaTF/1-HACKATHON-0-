"""
Odoo Sync Contacts Skill

Synchronizes contacts between local system and Odoo.
This skill can be executed autonomously as part of multi-step workflows.
"""

from typing import Dict, Any
from src.mcp.odoo_client import OdooClient
from src.audit.gold_logger import GoldAuditLogger


def odoo_sync_contacts(input_params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sync contacts with Odoo

    Args:
        input_params: Input parameters (optional filters)
        context: Workflow context

    Returns:
        Dictionary with sync results
    """
    audit_logger = GoldAuditLogger()

    try:
        # Initialize Odoo client
        odoo_client = OdooClient()

        # Get contacts from Odoo
        result = odoo_client.call("contacts/sync", input_params)

        if result["status"] == "success":
            contacts = result["data"]

            # Log success
            audit_logger.log_action(
                action_type="STEP_EXECUTE",
                action_name="odoo_sync_contacts",
                parameters=input_params,
                decision_rationale="Syncing contacts from Odoo",
                execution_result="SUCCESS",
                result_data={"contact_count": len(contacts)},
                business_impact=f"Synced {len(contacts)} contacts from Odoo",
            )

            return {
                "success": True,
                "contacts": contacts,
                "count": len(contacts),
            }
        else:
            # Queued or failed
            return {
                "success": False,
                "message": result.get("message", "Sync failed"),
                "queued": result["status"] == "queued",
            }

    except Exception as e:
        # Log error
        audit_logger.log_action(
            action_type="ERROR",
            action_name="odoo_sync_contacts_failed",
            parameters=input_params,
            decision_rationale="Contact sync failed",
            execution_result="FAILURE",
            result_data={},
            business_impact="Contact sync unavailable",
            error_details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "recovery_attempted": False,
                "recovery_result": "N/A",
            },
        )

        raise
