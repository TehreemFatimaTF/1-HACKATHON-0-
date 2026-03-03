"""
OdooInvoice model for Gold Tier Autonomous Employee

Represents a financial document for client billing with Odoo integration.
Includes comprehensive validation rules for tax calculations, amounts, and business logic.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional, Any
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json
import os


class PaymentStatus(str, Enum):
    """Invoice payment status"""
    DRAFT = "DRAFT"
    SENT = "SENT"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


@dataclass
class LineItem:
    """
    Invoice line item with quantity, price, and total
    """
    description: str
    quantity: float
    unit_price: float
    line_total: float
    product_id: Optional[int] = None

    def validate(self) -> bool:
        """
        Validate line item calculations

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        # Validate positive values
        if self.quantity <= 0:
            raise ValueError(f"Line item quantity must be positive, got {self.quantity}")

        if self.unit_price < 0:
            raise ValueError(f"Line item unit_price cannot be negative, got {self.unit_price}")

        # Validate line total calculation
        expected_total = round(self.quantity * self.unit_price, 2)
        if abs(self.line_total - expected_total) > 0.01:  # Allow 1 cent rounding tolerance
            raise ValueError(
                f"Line item total mismatch: expected {expected_total}, got {self.line_total}"
            )

        # Validate decimal precision (max 2 decimal places)
        if not self._has_valid_precision(self.unit_price):
            raise ValueError(f"Unit price must have at most 2 decimal places: {self.unit_price}")

        if not self._has_valid_precision(self.line_total):
            raise ValueError(f"Line total must have at most 2 decimal places: {self.line_total}")

        return True

    def _has_valid_precision(self, value: float) -> bool:
        """Check if value has at most 2 decimal places"""
        return round(value, 2) == value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "line_total": self.line_total,
            "product_id": self.product_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LineItem":
        """Create LineItem from dictionary"""
        return cls(
            description=data["description"],
            quantity=data["quantity"],
            unit_price=data["unit_price"],
            line_total=data["line_total"],
            product_id=data.get("product_id"),
        )


@dataclass
class OdooInvoice:
    """
    Financial document for client billing with Odoo integration

    Validation Rules:
    - subtotal must equal sum of line_items[].line_total
    - tax_amount must equal subtotal × tax_rate
    - total must equal subtotal + tax_amount
    - total >= 1000 triggers audit flag
    - due_date must be >= created_at
    - All monetary values must have exactly 2 decimal places
    """
    client_reference: str
    invoice_number: str
    line_items: List[LineItem]
    subtotal: float
    tax_rate: float
    tax_amount: float
    total: float
    currency: str
    due_date: date
    invoice_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    odoo_id: Optional[int] = None
    payment_status: PaymentStatus = PaymentStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    synced_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate invoice after initialization"""
        # Convert string dates to date objects if needed
        if isinstance(self.due_date, str):
            self.due_date = date.fromisoformat(self.due_date)

        # Convert LineItem dicts to LineItem objects if needed
        if self.line_items and isinstance(self.line_items[0], dict):
            self.line_items = [LineItem.from_dict(item) for item in self.line_items]

        # Normalize currency to uppercase
        self.currency = self.currency.upper()

        # Validate on creation
        self.validate()

    def validate(self) -> bool:
        """
        Validate invoice according to business rules

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        # Validate line items exist
        if not self.line_items:
            raise ValueError("Invoice must have at least one line item")

        # Validate each line item
        for i, item in enumerate(self.line_items):
            try:
                item.validate()
            except ValueError as e:
                raise ValueError(f"Line item {i + 1} validation failed: {e}")

        # Validate subtotal matches sum of line items
        expected_subtotal = sum(item.line_total for item in self.line_items)
        if abs(self.subtotal - expected_subtotal) > 0.01:  # Allow 1 cent rounding tolerance
            raise ValueError(
                f"Subtotal mismatch: expected {expected_subtotal:.2f}, got {self.subtotal:.2f}"
            )

        # Validate tax calculation
        if not self.validate_tax_calculation():
            expected_tax = round(self.subtotal * self.tax_rate, 2)
            expected_total = round(self.subtotal + expected_tax, 2)
            raise ValueError(
                f"Tax calculation error: subtotal={self.subtotal:.2f}, "
                f"tax_rate={self.tax_rate}, expected_tax={expected_tax:.2f}, "
                f"got tax_amount={self.tax_amount:.2f}, expected_total={expected_total:.2f}, "
                f"got total={self.total:.2f}"
            )

        # Validate positive amounts
        if self.subtotal < 0:
            raise ValueError(f"Subtotal cannot be negative: {self.subtotal}")

        if self.tax_amount < 0:
            raise ValueError(f"Tax amount cannot be negative: {self.tax_amount}")

        if self.total < 0:
            raise ValueError(f"Total cannot be negative: {self.total}")

        # Validate tax rate
        if self.tax_rate < 0 or self.tax_rate > 1:
            raise ValueError(f"Tax rate must be between 0 and 1: {self.tax_rate}")

        # Validate decimal precision
        if not self._has_valid_precision(self.subtotal):
            raise ValueError(f"Subtotal must have at most 2 decimal places: {self.subtotal}")

        if not self._has_valid_precision(self.tax_amount):
            raise ValueError(f"Tax amount must have at most 2 decimal places: {self.tax_amount}")

        if not self._has_valid_precision(self.total):
            raise ValueError(f"Total must have at most 2 decimal places: {self.total}")

        # Validate due date
        if self.due_date < self.created_at.date():
            raise ValueError(
                f"Due date ({self.due_date}) cannot be before creation date ({self.created_at.date()})"
            )

        # Validate currency
        valid_currencies = ["USD", "EUR", "GBP", "CAD", "AUD"]
        if self.currency not in valid_currencies:
            raise ValueError(
                f"Invalid currency: {self.currency}. Supported: {', '.join(valid_currencies)}"
            )

        return True

    def validate_tax_calculation(self) -> bool:
        """
        Validate that tax calculations are correct

        Returns:
            True if tax calculations are correct
        """
        expected_tax = round(self.subtotal * self.tax_rate, 2)
        expected_total = round(self.subtotal + expected_tax, 2)

        # Allow 1 cent tolerance for rounding
        tax_correct = abs(self.tax_amount - expected_tax) <= 0.01
        total_correct = abs(self.total - expected_total) <= 0.01

        return tax_correct and total_correct

    def _has_valid_precision(self, value: float) -> bool:
        """Check if value has at most 2 decimal places"""
        return round(value, 2) == value

    def requires_audit_flag(self) -> bool:
        """
        Check if invoice requires audit flag (total >= $1000)

        Returns:
            True if audit flag required
        """
        return self.total >= 1000.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert invoice to dictionary for JSON serialization"""
        return {
            "invoice_id": self.invoice_id,
            "odoo_id": self.odoo_id,
            "client_reference": self.client_reference,
            "invoice_number": self.invoice_number,
            "line_items": [item.to_dict() for item in self.line_items],
            "subtotal": self.subtotal,
            "tax_rate": self.tax_rate,
            "tax_amount": self.tax_amount,
            "total": self.total,
            "currency": self.currency,
            "due_date": self.due_date.isoformat(),
            "payment_status": self.payment_status.value,
            "created_at": self.created_at.isoformat(),
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
            "audit_flag": self.requires_audit_flag(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OdooInvoice":
        """Create invoice from dictionary"""
        return cls(
            invoice_id=data.get("invoice_id", str(uuid.uuid4())),
            odoo_id=data.get("odoo_id"),
            client_reference=data["client_reference"],
            invoice_number=data["invoice_number"],
            line_items=[LineItem.from_dict(item) for item in data["line_items"]],
            subtotal=data["subtotal"],
            tax_rate=data["tax_rate"],
            tax_amount=data["tax_amount"],
            total=data["total"],
            currency=data["currency"],
            due_date=date.fromisoformat(data["due_date"]) if isinstance(data["due_date"], str) else data["due_date"],
            payment_status=PaymentStatus(data.get("payment_status", "DRAFT")),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else data.get("created_at", datetime.utcnow()),
            synced_at=datetime.fromisoformat(data["synced_at"]) if data.get("synced_at") else None,
        )

    def save(self, directory: str = "Done") -> str:
        """
        Save invoice to JSON file

        Args:
            directory: Directory to save invoice file

        Returns:
            Path to saved file
        """
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"invoice_{self.invoice_id}.json")

        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        return filepath

    @classmethod
    def load(cls, invoice_id: str, directory: str = "Done") -> "OdooInvoice":
        """
        Load invoice from JSON file

        Args:
            invoice_id: Invoice ID to load
            directory: Directory containing invoice file

        Returns:
            Loaded OdooInvoice instance
        """
        filepath = os.path.join(directory, f"invoice_{invoice_id}.json")

        with open(filepath, "r") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def mark_sent(self) -> None:
        """Mark invoice as sent to client"""
        self.payment_status = PaymentStatus.SENT

    def mark_paid(self) -> None:
        """Mark invoice as paid"""
        self.payment_status = PaymentStatus.PAID

    def mark_overdue(self) -> None:
        """Mark invoice as overdue"""
        self.payment_status = PaymentStatus.OVERDUE

    def mark_cancelled(self) -> None:
        """Mark invoice as cancelled"""
        self.payment_status = PaymentStatus.CANCELLED

    def update_odoo_sync(self, odoo_id: int) -> None:
        """
        Update invoice with Odoo sync information

        Args:
            odoo_id: Odoo database record ID
        """
        self.odoo_id = odoo_id
        self.synced_at = datetime.utcnow()
