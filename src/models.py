# src/models.py
from .database import SessionLocal, Transaction, Investment
from datetime import date
from typing import List
from sqlalchemy import select, func, text
from decimal import Decimal, ROUND_HALF_UP

def add_transaction(date: date, category: str, amount: Decimal, description: str = "", account: str = "Cash"):
    with SessionLocal() as db:
        # Ensure amount is a Decimal before saving
        t = Transaction(date=date, category=category, amount=Decimal(str(amount)), description=description, account=account)
        db.add(t)
        db.commit()

def get_all_transactions() -> List[Transaction]:
    with SessionLocal() as db:
        return db.query(Transaction).order_by(Transaction.date.desc()).all()

def get_balance() -> Decimal:
    with SessionLocal() as db:
        total = db.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)))
        # Convert the SQLite result (float/int) back to Decimal
        return Decimal(str(total)).quantize(Decimal('0.01'))

def add_or_update_investment(name: str, current_value: Decimal, monthly: Decimal = 0, return_rate: Decimal = 10.0, target_year: int = 2050, notes: str = ""):
    with SessionLocal() as db:
        inv = db.query(Investment).filter(Investment.name == name).first()
        if inv:
            inv.current_value = Decimal(str(current_value))
            inv.monthly_contribution = Decimal(str(monthly))
            inv.expected_annual_return = Decimal(str(return_rate))
            inv.target_year = target_year
            inv.notes = notes
        else:
            inv = Investment(
                name=name, 
                current_value=Decimal(str(current_value)), 
                monthly_contribution=Decimal(str(monthly)),
                expected_annual_return=Decimal(str(return_rate)), 
                target_year=target_year, 
                notes=notes)
            db.add(inv)
        db.commit()

def get_investments():
    with SessionLocal() as db:
        return db.query(Investment).all()

def calculate_future_value(inv: Investment, extra_monthly: Decimal = Decimal('0')) -> Decimal:
    today = date.today()
    years = inv.target_year - today.year
    if years <= 0:
        return Decimal(str(inv.current_value))
    
    # Financial constants as Decimals
    monthly_rate = Decimal(str(inv.expected_annual_return)) / Decimal('12') / Decimal('100') # e.g, 10% -> 0.008333
    total_months = Decimal(str(years * 12))
    pmt = Decimal(str(inv.monthly_contribution)) * Decimal(str(extra_monthly))

    # Future value of principal: FV = P (1 + r)^n
    fv_principal = Decimal(str(inv.current_value)) * (Decimal('1') + monthly_rate) ** int(total_months)

    # Future value of contributions (annuity formula)
    if monthly_rate == 0:
        fv_contrib = pmt * total_months
    else:
        # FV = PMT * (((1 + r)^n - 1) / r)
        fv_contrib = pmt * (( (Decimal('1') + monthly_rate) ** int(total_months) - Decimal('1') ) / monthly_rate)

    total_fv = fv_principal + fv_contrib
    return total_fv.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) # Round to cents

def get_total_projected_wealth(target_year: int = None) -> Decimal:
    total = Decimal('0.00')
    for inv in get_investments():
        if target_year is None or inv.target_year == target_year:
            total += calculate_future_value(inv)
    return total

def get_transactions_with_running_balance() -> List[dict]:
    with SessionLocal() as db:
        # Get all transactions ordered from OLDEST to NEWEST (for correct cumulative sum)
        transactions = db.query(Transaction).order_by(Transaction.date.asc(), Transaction.id.asc()).all()
        
        running_balance = Decimal('0.00')
        result = []
        
        for t in transactions:
            # Convet t.amount (from DB) to Decimal to ensure math is precise
            amt = Decimal(str(t.amount))
            running_balance += amt
            result.append({
                "transaction": t,
                "running_balance": running_balance.quantize(Decimal('0.01'))
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

        running_balance = Decimal('0.00')
        result = []

        for t in transactions:
            amt = Decimal(str(t.amount))
            running_balance += amt
            result.append({
                "transaction": t,
                "running_balance": running_balance.quantize(Decimal('0.01'))
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
        
        summary = []
        for r in result.fetchall():
            summary.append({
                "month": r[0],
                # Convert SQL floats to Strings then Decimals for absolute precision
                "income": Decimal(str(r[1] or 0)).quantize(Decimal('0.01')),
                "expenses": Decimal(str(r[2] or 0)).quantize(Decimal('0.01'))
            })
        return summary