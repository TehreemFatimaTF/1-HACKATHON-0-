"""
OdooExpense model for Gold Tier Autonomous Employee

Represents a financial transaction for business expenses with Odoo integration.
Includes comprehensive validation rules for amounts, categories, and business logic.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Dict, Optional, Any
import uuid
import json
import os


class ExpenseCategory(str, Enum):
    """Expense category enumeration"""
    MARKETING = "MARKETING"
    OPERATIONS = "OPERATIONS"
    TRAVEL = "TRAVEL"
    SUPPLIES = "SUPPLIES"
    SOFTWARE = "SOFTWARE"
    OTHER = "OTHER"


class ApprovalStatus(str, Enum):
    """Expense approval status"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class OdooExpense:
    """
    Financial transaction for business expenses with Odoo integration

    Validation Rules:
    - amount > 0
    - amount >= 500 triggers audit flag
    - category must be in approved list
    - date must be <= current date (no future expenses)
    - All monetary values must have exactly 2 decimal places
    """
    category: ExpenseCategory
    subcategory: str
    amount: float
    currency: str
    date: date
    description: str
    vendor: str
    expense_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    odoo_id: Optional[int] = None
    receipt_url: Optional[str] = None
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    synced_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate expense after initialization"""
        # Convert string dates to date objects if needed
        if isinstance(self.date, str):
            self.date = date.fromisoformat(self.date)

        # Convert string enums to enum objects if needed
        if isinstance(self.category, str):
            self.category = ExpenseCategory(self.category.upper())

        if isinstance(self.approval_status, str):
            self.approval_status = ApprovalStatus(self.approval_status.upper())

        # Normalize currency to uppercase
        self.currency = self.currency.upper()

        # Validate on creation
        self.validate()

    def validate(self) -> bool:
        """
        Validate expense according to business rules

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        # Validate positive amount
        if self.amount <= 0:
            raise ValueError(f"Expense amount must be positive, got {self.amount}")

        # Validate decimal precision (max 2 decimal places)
        if not self._has_valid_precision(self.amount):
            raise ValueError(f"Amount must have at most 2 decimal places: {self.amount}")

        # Validate category
        if not isinstance(self.category, ExpenseCategory):
            valid_categories = [c.value for c in ExpenseCategory]
            raise ValueError(
                f"Invalid category: {self.category}. Valid categories: {', '.join(valid_categories)}"
            )

        # Validate subcategory for OTHER category
        if self.category == ExpenseCategory.OTHER and not self.subcategory:
            raise ValueError("Subcategory is required when category is OTHER")

        # Validate date (no future expenses)
        if self.date > date.today():
            raise ValueError(
                f"Expense date cannot be in the future: {self.date} > {date.today()}"
            )

        # Validate currency
        valid_currencies = ["USD", "EUR", "GBP", "CAD", "AUD"]
        if self.currency not in valid_currencies:
            raise ValueError(
                f"Invalid currency: {self.currency}. Supported: {', '.join(valid_currencies)}"
            )

        # Validate required fields
        if not self.description:
            raise ValueError("Expense description is required")

        if not self.vendor:
            raise ValueError("Expense vendor is required")

        return True

    def _has_valid_precision(self, value: float) -> bool:
        """Check if value has at most 2 decimal places"""
        return round(value, 2) == value

    def requires_audit_flag(self) -> bool:
        """
        Check if expense requires audit flag (amount >= $500)

        Returns:
            True if audit flag required
        """
        return self.amount >= 500.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert expense to dictionary for JSON serialization"""
        return {
            "expense_id": self.expense_id,
            "odoo_id": self.odoo_id,
            "category": self.category.value,
            "subcategory": self.subcategory,
            "amount": self.amount,
            "currency": self.currency,
            "date": self.date.isoformat(),
            "description": self.description,
            "vendor": self.vendor,
            "receipt_url": self.receipt_url,
            "approval_status": self.approval_status.value,
            "approved_by": self.approved_by,
            "created_at": self.created_at.isoformat(),
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
            "audit_flag": self.requires_audit_flag(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OdooExpense":
        """Create expense from dictionary"""
        return cls(
            expense_id=data.get("expense_id", str(uuid.uuid4())),
            odoo_id=data.get("odoo_id"),
            category=ExpenseCategory(data["category"].upper() if isinstance(data["category"], str) else data["category"]),
            subcategory=data["subcategory"],
            amount=data["amount"],
            currency=data["currency"],
            date=date.fromisoformat(data["date"]) if isinstance(data["date"], str) else data["date"],
            description=data["description"],
            vendor=data["vendor"],
            receipt_url=data.get("receipt_url"),
            approval_status=ApprovalStatus(data.get("approval_status", "PENDING").upper() if isinstance(data.get("approval_status"), str) else data.get("approval_status", ApprovalStatus.PENDING)),
            approved_by=data.get("approved_by"),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else data.get("created_at", datetime.utcnow()),
            synced_at=datetime.fromisoformat(data["synced_at"]) if data.get("synced_at") else None,
        )

    def save(self, directory: str = "Done") -> str:
        """
        Save expense to JSON file

        Args:
            directory: Directory to save expense file

        Returns:
            Path to saved file
        """
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"expense_{self.expense_id}.json")

        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        return filepath

    @classmethod
    def load(cls, expense_id: str, directory: str = "Done") -> "OdooExpense":
        """
        Load expense from JSON file

        Args:
            expense_id: Expense ID to load
            directory: Directory containing expense file

        Returns:
            Loaded OdooExpense instance
        """
        filepath = os.path.join(directory, f"expense_{expense_id}.json")

        with open(filepath, "r") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def approve(self, approved_by: str) -> None:
        """
        Approve the expense

        Args:
            approved_by: Name/ID of approver
        """
        self.approval_status = ApprovalStatus.APPROVED
        self.approved_by = approved_by

    def reject(self, rejected_by: str) -> None:
        """
        Reject the expense

        Args:
            rejected_by: Name/ID of rejector
        """
        self.approval_status = ApprovalStatus.REJECTED
        self.approved_by = rejected_by  # Store who rejected it

    def update_odoo_sync(self, odoo_id: int) -> None:
        """
        Update expense with Odoo sync information

        Args:
            odoo_id: Odoo database record ID
        """
        self.odoo_id = odoo_id
        self.synced_at = datetime.utcnow()

    def attach_receipt(self, receipt_url: str) -> None:
        """
        Attach receipt to expense

        Args:
            receipt_url: URL or path to receipt image
        """
        self.receipt_url = receipt_url

    def get_category_display(self) -> str:
        """
        Get human-readable category display

        Returns:
            Category with subcategory if applicable
        """
        if self.subcategory:
            return f"{self.category.value} - {self.subcategory}"
        return self.category.value

    def is_marketing_expense(self) -> bool:
        """
        Check if this is a marketing expense

        Returns:
            True if category is MARKETING
        """
        return self.category == ExpenseCategory.MARKETING

    def requires_approval(self) -> bool:
        """
        Check if expense requires manual approval

        Returns:
            True if amount >= $500 or status is PENDING
        """
        return self.requires_audit_flag() or self.approval_status == ApprovalStatus.PENDING
