# src/services/core.py
from typing import List
from ..models import (
    add_transaction,
    get_all_transactions,
    get_balance,
    add_or_update_investment,
    get_investments,
    calculate_future_value,
    get_total_projected_wealth,
    get_monthly_summary,
    get_transactions_with_running_balance,
    Transaction,
    Investment,
)
from ..database import SessionLocal


# -------------------------
# Transactions
# -------------------------

def svc_get_transactions_with_running_balance() -> List[dict]:
    return get_transactions_with_running_balance()


def svc_get_all_transactions() -> List[Transaction]:
    return get_all_transactions()


def svc_add_transaction(date, category, amount, description=""):
    add_transaction(
        date=date,
        category=category,
        amount=amount,
        description=description,
    )


def svc_update_transaction(transaction: Transaction):
    with SessionLocal() as db:
        db.merge(transaction)
        db.commit()


def svc_delete_transaction(transaction_id: int):
    with SessionLocal() as db:
        t = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if t:
            db.delete(t)
            db.commit()


def svc_get_balance() -> float:
    return get_balance()


# -------------------------
# Investments
# -------------------------

def svc_get_investments() -> List[Investment]:
    return get_investments()


def svc_add_or_update_investment(
    name: str,
    current_value: float,
    monthly: float = 0,
    return_rate: float = 10.0,
    target_year: int = 2050,
    notes: str = "",
):
    add_or_update_investment(
        name,
        current_value,
        monthly,
        return_rate,
        target_year,
        notes,
    )


def svc_delete_investment(investment_id: int):
    with SessionLocal() as db:
        inv = db.query(Investment).filter(Investment.id == investment_id).first()
        if inv:
            db.delete(inv)
            db.commit()


def svc_calculate_future_value(inv: Investment, extra_monthly: float = 0) -> float:
    return calculate_future_value(inv, extra_monthly)


def svc_get_total_projected_wealth(target_year: int = None) -> float:
    return get_total_projected_wealth(target_year)


# -------------------------
# Reporting
# -------------------------

def svc_get_monthly_summary():
    return get_monthly_summary()
