# src/database.py
import os
from datetime import date
from decimal import Decimal
# Import TypeDecorator to ensure SQLite handles Decimals as strings/floats correctly
# SQLite does not have a native DECIMAL type. Defaults to storing values as floats anyway.
from sqlalchemy.types import Numeric
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# A Quick Tip on SQLite
# SQLite is "type-less." It will store these numbers as floating-point values internally.
# However, because you are now using SQLAlchemy's Numeric type, the library will automatically 
# convert those values back into Python Decimal objects whenever you query the database, 
# preserving your precision during calculations in your app.

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "finance.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
SessionLocal = sessionmaker(bind=engine, future=True)
Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    description = Column(String)
    account = Column(String, default="Cash")
    tags = Column(String)

class Investment(Base):
    __tablename__ = "investments"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    current_value = Column(Numeric(precision=15, scale=2), nullable=False)
    monthly_contribution = Column(Numeric(precision=15, scale=2), default=Decimal("0.00"))
    # Annual return is a percentage; keep as Numeric for precision in compounding
    expected_annual_return = Column(Numeric(precision=4, scale=2), default=Decimal(10.00)) # e.g., 10.00%
    target_year = Column(Integer, default=2050)
    notes = Column(String)

Base.metadata.create_all(engine)

# Migration Logic
_migration_done = False

def _auto_migrate():
    global _migration_done
    if _migration_done:
        return
    import json
    json_path = os.path.join(BASE_DIR, "data", "finance_diary.json")
    if not os.path.exists(json_path):
        _migration_done = True
        return

    with open(json_path, "r") as f:
        old_entries = json.load(f)
    
    with SessionLocal() as db:
        for entry in old_entries:
            try:
                entry_date = date.fromisoformat(entry["date"])
            except:
                continue

            # Handle Income
            income_val = entry.get("income", 0)
            if income_val and float(income_val) > 0:
                db.add(
                    Transaction(
                        date=entry_date,
                        category="Salary",
                        amount=Decimal(str(income_val)), # Convert via string for safety
                        description=entry.get("notes","")
                    )
                )

            # Handle Expense
            expense_val = entry.get("expense", 0)
            if expense_val and float(expense_val) > 0:
                db.add(
                    Transaction(
                        date=entry_date,
                        category="Expense",
                        # Multiply by -1 using Decimal to maintain type consistency
                        amount=Decimal(str(expense_val)) * Decimal("-1.00"),
                        description=entry.get("notes","")
                    )
                )
        db.commit()
    _migration_done = True

_auto_migrate()