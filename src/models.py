from .database import SessionLocal, Transaction, Investment
from datetime import date
from typing import List
from sqlalchemy import select, func

def add_transaction(date: date, category: str, amount: float, description: str = "", account: str = "Cash"):
    with SessionLocal() as db:
        t = Transaction(date=date, category=category, amount=amount, description=description, account=account)
        db.add(t)
        db.commit()

def get_all_transactions() -> List[Transaction]:
    with SessionLocal() as db:
        return db.query(Transaction).order_by(Transaction.date.desc()).all()

def get_balance() -> float:
    with SessionLocal() as db:
        total = db.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)))
        return float(total)

# Investments
def add_or_update_investment(name: str, current_value: float, monthly: float = 0, return_rate: float = 10.0, target_year: int = 2050, notes: str = ""):
    with SessionLocal() as db:
        inv = db.query(Investment).filter(Investment.name == name).first()
        if inv:
            inv.current_value = current_value
            inv.monthly_contribution = monthly
            inv.expected_annual_return = return_rate
            inv.target_year = target_year
            inv.notes = notes
        else:
            inv = Investment(name=name, current_value=current_value, monthly_contribution=monthly,
                           expected_annual_return=return_rate, target_year=target_year, notes=notes)
            db.add(inv)
        db.commit()

def get_investments():
    with SessionLocal() as db:
        return db.query(Investment).all()

def calculate_future_value(investment: Investment) -> float:
    from math import pow
    years = investment.target_year - date.today().year
    if years <= 0:
        return investment.current_value
    monthly_rate = investment.expected_annual_return / 100 / 12
    months = years * 12
    fv_contributions = investment.monthly_contribution * ((pow(1 + monthly_rate, months) - 1) / monthly_rate)
    fv_current = investment.current_value * pow(1 + monthly_rate, months)
    return fv_current + fv_contributions