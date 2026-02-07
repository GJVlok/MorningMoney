# src/services/transactions.py
from typing import List
from ..models import (
    add_transaction as _add_transaction,
    get_all_transactions as _get_all_transactions,
    get_balance as _get_balance,
    get_monthly_summary as _get_monthly_summary,
)
from ..database import Transaction
from decimal import Decimal


# Service layer — provides a stable API for UI and prevents direct model imports.

def add_new_transaction(date, category: str, amount: Decimal, description: str = ""):
    """Add a new transaction through the model layer."""
    return _add_transaction(
        date=date,
        category=category,
        amount=amount,
        description=description,
    )


def get_all_transactions() -> List[Transaction]:
    """Return all transactions."""
    return _get_all_transactions()


def get_balance() -> Decimal:
    """Return total account balance."""
    return _get_balance()


def get_monthly_summary():
    """Return grouped monthly aggregates."""
    return _get_monthly_summary()
