# src/models.py
from .database import SessionLocal, Transaction, Investment
from datetime import date
from typing import List
from sqlalchemy import select, func, text

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

def calculate_future_value(investment: Investment, extra_monthly: float = 0) -> float:
    from math import pow
    today = date.today()
    target = date(investment.target_year, 12, 31)
    months = max(0, (target.year - today.year) * 12 + (target.month - today.month))
    monthly_rate = investment.expected_annual_return / 100 / 12
    total_monthly = investment.monthly_contribution + extra_monthly
    if monthly_rate == 0:
        return investment.current_value + total_monthly * months
    fv_current = investment.current_value * pow(1 + monthly_rate, months)
    fv_contributions = total_monthly * ((pow(1 + monthly_rate, months) - 1) / monthly_rate)
    return round(fv_current + fv_contributions, 2)

def get_total_projected_wealth(target_year: int = None) -> float:
    total = 0
    for inv in get_investments():
        if target_year is None or inv.target_year == target_year:
            total += calculate_future_value(inv)
    return total

def get_transactions_with_running_balance() -> List[dict]:
    """
    Returns all transactions ordered by date DESC,
    with an extra 'running_balance' field showing balance after each transaction.
    """
    with SessionLocal() as db:
        # Get all transactions ordered from OLDEST to NEWEST (for correct cumulative sum)
        transactions = db.query(Transaction).order_by(Transaction.date.asc(), Transaction.id.asc()).all()
        
        running_balance = 0
        result = []
        
        for t in transactions:
            running_balance += t.amount
            result.append({
                "transaction": t,
                "running_balance": round(running_balance, 2)
            })
        
        # Reverse so newest appears first (like current Diary tab)
        result.reverse()
        return result
    
def get_transactions_with_running_balance_date_to_date(from_date: date = None, to_date: date = None) -> List[dict]:
    with SessionLocal() as db:
        query = db.query(Transaction).order_by(Transaction.date.asc(), Transaction.id.asc())
        if from_date:
            query = query.filter(Transaction.date >= from_date)
        if to_date:
            query = query.filter(Transaction.date <= to_date)
        transactions = query.all()

        running_balance = 0
        result = []

        for t in transactions:
            running_balance += t.amount
            result.append({
                "transaction": t,
                "running_balance": round(running_balance, 2)
            })

        result.reverse()
        return result

def get_monthly_summary() -> List[dict]:
    with SessionLocal() as db:
        result = db.execute(text("""
            SELECT 
                strftime('%Y-%m', date) as month,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) as expenses
            FROM transactions 
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month DESC
            LIMIT 24
        """))
        return [{"month": r[0], "income": float(r[1] or 0), "expenses": float(r[2] or 0)} for r in result.fetchall()]