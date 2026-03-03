"""
Odoo Create Invoice Skill

Creates invoices in Odoo with tax validation and $500+ transaction flagging.
This skill can be executed autonomously as part of multi-step workflows.
"""

from typing import Dict, Any
from src.mcp.odoo_client import OdooClient
from src.models.odoo_invoice import OdooInvoice
from src.audit.gold_logger import GoldAuditLogger


def odoo_create_invoice(input_params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create an invoice in Odoo with tax validation and flagging

    Args:
        input_params: Invoice data (client_reference, line_items, etc.)
        context: Workflow context

    Returns:
        Dictionary with invoice creation results
    """
    audit_logger = GoldAuditLogger()

    try:
        # Create OdooInvoice model (validates tax calculations automatically)
        invoice = OdooInvoice.from_dict(input_params)

        # Check if invoice requires audit flag (>= $1000)
        audit_flag = invoice.requires_audit_flag()

        if audit_flag:
            # Log high-value transaction
            audit_logger.log_action(
                action_type="DECISION",
                action_name="invoice_flagged_for_audit",
                parameters={
                    "invoice_id": invoice.invoice_id,
                    "total": invoice.total,
                    "threshold": 1000.0,
                },
                decision_rationale=f"Invoice total ${invoice.total:.2f} exceeds $1000 threshold",
                execution_result="SUCCESS",
                result_data={"audit_flag": True},
                business_impact=f"High-value invoice flagged for review: ${invoice.total:.2f}",
            )

        # Validate vendor/client cross-reference
        if not _validate_client_reference(invoice.client_reference):
            raise ValueError(f"Invalid client reference: {invoice.client_reference}")

        # Initialize Odoo client
        odoo_client = OdooClient()

        # Create invoice in Odoo
        result = odoo_client.create_invoice(invoice)

        if result["status"] == "success":
            # Save invoice locally
            invoice_path = invoice.save(directory="Done")

            # Log success
            audit_logger.log_action(
                action_type="STEP_EXECUTE",
                action_name="odoo_create_invoice",
                parameters=input_params,
                decision_rationale="Creating invoice in Odoo",
                execution_result="SUCCESS",
                result_data={
                    "invoice_id": invoice.invoice_id,
                    "odoo_id": invoice.odoo_id,
                    "total": invoice.total,
                    "audit_flag": audit_flag,
                },
                business_impact=f"Invoice created: ${invoice.total:.2f} for {invoice.client_reference}",
            )

            return {
                "success": True,
                "invoice_id": invoice.invoice_id,
                "odoo_id": invoice.odoo_id,
                "total": invoice.total,
                "audit_flag": audit_flag,
                "file_path": invoice_path,
            }
        else:
            # Queued or failed
            # Still save locally even if Odoo sync failed
            invoice_path = invoice.save(directory="Needs_Action")

            return {
                "success": False,
                "invoice_id": invoice.invoice_id,
                "message": result.get("message", "Invoice creation failed"),
                "queued": result["status"] == "queued",
                "file_path": invoice_path,
            }

    except ValueError as e:
        # Validation error
        audit_logger.log_action(
            action_type="ERROR",
            action_name="invoice_validation_failed",
            parameters=input_params,
            decision_rationale="Invoice validation failed",
            execution_result="FAILURE",
            result_data={},
            business_impact="Invoice not created due to validation error",
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
            action_name="odoo_create_invoice_failed",
            parameters=input_params,
            decision_rationale="Invoice creation failed",
            execution_result="FAILURE",
            result_data={},
            business_impact="Invoice creation unavailable",
            error_details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "recovery_attempted": False,
                "recovery_result": "N/A",
            },
        )

        raise


def _validate_client_reference(client_reference: str) -> bool:
    """
    Validate client reference exists in system

    Args:
        client_reference: Client identifier

    Returns:
        True if valid

    TODO: Implement actual client lookup from Odoo or local database
    """
    # For now, accept any non-empty string
    # In production, this would query Odoo for partner existence
    return bool(client_reference and client_reference.strip())
