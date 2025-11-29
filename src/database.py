# src/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "finance.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
SessionLocal = sessionmaker(bind=engine, future=True)
Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, default=date.today)
    category = Column(String, nullable=False, default="Uncategorized")
    amount = Column(Float, nullable=False)
    description = Column(String)
    account = Column(String, default="Cash")

class Investment(Base):
    __tablename__ = "investments"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    current_value = Column(Float, nullable=False)
    monthly_contribution = Column(Float, default=0)
    expected_annual_return = Column(Float, default=10.0)
    target_year = Column(Integer, default=2050)
    notes = Column(String)

Base.metadata.create_all(engine)

# Auto-migrate
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

    print("Migrating old JSON to SQLite...")
    with open(json_path, "r") as f:
        old_entries = json.load(f)
    
    with SessionLocal() as db:
        for entry in old_entries:
            try:
                entry_date = date.fromisoformat(entry["date"])
            except:
                continue
            if entry.get("income", 0) > 0:
                db.add(Transaction(date=entry_date, category="Salary", amount=entry["income"], description=entry.get("notes","")))
            if entry.get("expense", 0) > 0:
                db.add(Transaction(date=entry_date, category="Expense", amount=-entry["expense"], description=entry.get("notes","")))
        db.commit()
    print("Migration complete!")
    _migration_done = True

_auto_migrate()