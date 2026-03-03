"""
Odoo Skills Integration with Ralph Wiggum Loop Engine

This module registers all Odoo skills with the autonomous execution engine,
allowing them to be called as part of multi-step workflows.
"""

from src.engine_gold import RalphWiggumLoopEngine
from src.skills.odoo_sync_contacts import odoo_sync_contacts
from src.skills.odoo_create_invoice import odoo_create_invoice
from src.skills.odoo_log_expense import odoo_log_expense
from src.skills.odoo_fetch_ledger import odoo_fetch_ledger


def register_odoo_skills(engine: RalphWiggumLoopEngine) -> None:
    """
    Register all Odoo skills with the autonomous execution engine

    Args:
        engine: RalphWiggumLoopEngine instance

    Skills registered:
    - odoo_sync_contacts: Sync contacts from Odoo
    - odoo_create_invoice: Create invoice with tax validation
    - odoo_log_expense: Log expense with categorization
    - odoo_fetch_ledger: Fetch accounting summary
    """
    # Register Odoo skills
    engine.register_action("odoo_sync_contacts", odoo_sync_contacts)
    engine.register_action("odoo_create_invoice", odoo_create_invoice)
    engine.register_action("odoo_log_expense", odoo_log_expense)
    engine.register_action("odoo_fetch_ledger", odoo_fetch_ledger)

    # Register rollback actions for Odoo operations
    engine.register_action("delete_invoice", _rollback_invoice)
    engine.register_action("delete_expense", _rollback_expense)

    print("[Odoo Integration] Registered 4 Odoo skills with autonomous engine")


def _rollback_invoice(output: dict, context: dict) -> dict:
    """
    Rollback action for invoice creation

    Args:
        output: Output from invoice creation (contains invoice_id)
        context: Workflow context

    Returns:
        Rollback result
    """
    from src.models.odoo_invoice import OdooInvoice
    import os

    invoice_id = output.get("invoice_id")

    if not invoice_id:
        return {"success": False, "error": "No invoice_id in output"}

    try:
        # Load invoice
        invoice = OdooInvoice.load(invoice_id, directory="Done")

        # Mark as cancelled
        invoice.mark_cancelled()

        # Save updated state
        invoice.save(directory="Done")

        # If synced to Odoo, we should also cancel in Odoo
        # TODO: Implement Odoo cancellation via API

        return {
            "success": True,
            "message": f"Invoice {invoice_id} marked as cancelled",
        }

    except FileNotFoundError:
        # Invoice file not found, check Needs_Action
        try:
            invoice = OdooInvoice.load(invoice_id, directory="Needs_Action")
            invoice.mark_cancelled()
            invoice.save(directory="Needs_Action")
            return {"success": True, "message": f"Invoice {invoice_id} cancelled"}
        except FileNotFoundError:
            return {"success": False, "error": f"Invoice {invoice_id} not found"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _rollback_expense(output: dict, context: dict) -> dict:
    """
    Rollback action for expense logging

    Args:
        output: Output from expense logging (contains expense_id)
        context: Workflow context

    Returns:
        Rollback result
    """
    from src.models.odoo_expense import OdooExpense
    import os

    expense_id = output.get("expense_id")

    if not expense_id:
        return {"success": False, "error": "No expense_id in output"}

    try:
        # Load expense
        expense = OdooExpense.load(expense_id, directory="Done")

        # Mark as rejected
        expense.reject("system_rollback")

        # Save updated state
        expense.save(directory="Done")

        # If synced to Odoo, we should also delete/reject in Odoo
        # TODO: Implement Odoo deletion via API

        return {
            "success": True,
            "message": f"Expense {expense_id} marked as rejected",
        }

    except FileNotFoundError:
        # Expense file not found, check Needs_Action
        try:
            expense = OdooExpense.load(expense_id, directory="Needs_Action")
            expense.reject("system_rollback")
            expense.save(directory="Needs_Action")
            return {"success": True, "message": f"Expense {expense_id} rejected"}
        except FileNotFoundError:
            return {"success": False, "error": f"Expense {expense_id} not found"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def initialize_odoo_integration(engine: RalphWiggumLoopEngine) -> None:
    """
    Initialize complete Odoo integration with autonomous engine

    This function:
    1. Registers all Odoo skills
    2. Sets up circuit breaker for Odoo client
    3. Configures retry policies
    4. Initializes offline queue processing

    Args:
        engine: RalphWiggumLoopEngine instance
    """
    from src.mcp.odoo_client import OdooClient
    from src.utils.circuit_breaker import CircuitBreaker

    # Register skills
    register_odoo_skills(engine)

    # Create circuit breaker for Odoo
    odoo_circuit_breaker = CircuitBreaker(
        failure_threshold=3,
        timeout=60.0,
        name="OdooCircuitBreaker"
    )

    # Register circuit breaker with engine
    engine.register_circuit_breaker("odoo", odoo_circuit_breaker)

    # Initialize Odoo client (will authenticate and load queue)
    try:
        odoo_client = OdooClient()

        # Process any queued operations from previous sessions
        queue_result = odoo_client.process_queue()

        if queue_result["processed"] > 0:
            print(f"[Odoo Integration] Processed {queue_result['processed']} queued operations")

        if queue_result["remaining"] > 0:
            print(f"[Odoo Integration] {queue_result['remaining']} operations still queued")

    except Exception as e:
        print(f"[Odoo Integration] Warning: Could not initialize Odoo client: {e}")
        print("[Odoo Integration] Client will operate in offline mode")

    print("[Odoo Integration] Initialization complete")
