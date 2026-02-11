from typing import List
from decimal import Decimal
from ..models import (
    add_transaction,
    get_all_transactions,
    get_balance,
    add_or_update_investment,
    get_investments,
    calculate_future_value,
    get_total_projected_wealth,
    get_monthly_summary,
    get_tag_summary,
    get_transactions_with_running_balance,
    get_transactions_with_running_balance_date_to_date,
    Transaction,
    Investment,
)
from ..database import SessionLocal

# -------------------------
# Transactions
# -------------------------

def svc_get_transactions_with_running_balance() -> List[dict]:
    return get_transactions_with_running_balance()

def svc_get_transactions_with_running_balance_date_to_date(from_date=None, to_date=None) -> List[dict]:
    return get_transactions_with_running_balance_date_to_date(from_date, to_date)

def svc_get_all_transactions() -> List[Transaction]:
    return get_all_transactions()

def svc_add_transaction(date,
                        category,
                        amount,
                        description="",
                        tags=""):
    # Ensure amount is a Decimal string-conversion safe
    add_transaction(
        date=date,
        category=category,
        amount=Decimal(str(amount)),
        description=description,
        tags=tags
    )
    # Add helper: svc_get_tags_for_transaction(id) if needed later.

def svc_update_transaction(transaction_id: int, **fields):
    with SessionLocal() as db:
        t = db.get(Transaction, transaction_id) # Using modern .get() for simplicity
        if t:
            for k, v in fields.items():
                # If updating 'amount', ensure it's a Decimal
                if k == "amount":
                    v = Decimal(str(v))
                setattr(t, k, v)
            db.commit()

def svc_delete_transaction(transaction_id: int):
    with SessionLocal() as db:
        t = db.get(Transaction, transaction_id)
        if t:
            db.delete(t)
            db.commit()

def svc_get_balance() -> Decimal:
    return get_balance()

# -------------------------
# Investments
# -------------------------

def svc_get_investments() -> List[Investment]:
    return get_investments()

def svc_add_or_update_investment(
    name: str,
    current_value: Decimal,
    monthly: Decimal = Decimal("0.00"),
    return_rate: Decimal = Decimal("10.00"),
    target_year: int = 2050,
    notes: str = "",
):
    # Enforce Decimal types on all currency/rate inputs
    add_or_update_investment(
        name=name,
        current_value=Decimal(str(current_value)),
        monthly=Decimal(str(monthly)),
        return_rate=Decimal(str(return_rate)),
        target_year=target_year,
        notes=notes,
    )

def svc_delete_investment(investment_id: int):
    with SessionLocal() as db:
        inv = db.get(Investment, investment_id)
        if inv:
            db.delete(inv)
            db.commit()

def svc_calculate_future_value(inv: Investment, extra_monthly: Decimal = Decimal("0.00")) -> Decimal:
    return calculate_future_value(inv, Decimal(str(extra_monthly)))

def svc_get_total_projected_wealth(target_year: int = None) -> Decimal:
    return get_total_projected_wealth(target_year)

# -------------------------
# Reporting
# -------------------------

def svc_get_monthly_summary():
    return get_monthly_summary()

def svc_get_tag_summary():
    return get_tag_summary()
