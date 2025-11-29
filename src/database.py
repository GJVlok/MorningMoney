from sqlalchemy import create_engine, Column, Integer, String, Float, Date, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "finance.db")

engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
SessionLocal = sessionmaker(bind=engine, future=True)
Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, default=date.today)
    category = Column(String, nullable=False, default="Uncategorized")  # Expense or Income category
    amount = Column(Float, nullable=False)  # Positive = income, Negative = expense
    description = Column(String)
    account = Column(String, default="Cash")  # Future: Bank, Credit Card, etc.

class Investment(Base):
    __tablename__ = "investments"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)           # e.g. "Retirement Annuity - Allan Gray"
    current_value = Column(Float, nullable=False)
    monthly_contribution = Column(Float, default=0)
    expected_annual_return = Column(Float, default=10.0)  # % per year
    target_year = Column(Integer, default=2050)
    notes = Column(String)

# Create tables if they don't exist
Base.metadata.create_all(engine)

# ---------- One-time JSON → SQLite migration ----------
def migrate_from_json():
    from sqlalchemy.orm import Session
    import json
    json_path = os.path.join(BASE_DIR, "data", "finance_diary.json")
    if not os.path.exists(json_path):
        print("No old JSON found – fresh start!")
        return
    
    with open(json_path, "r") as f:
        old_entries = json.load(f)
    
    with SessionLocal() as db:
        count = 0
        for entry in old_entries:
            try:
                entry_date = date.fromisoformat(entry["date"])
            except:
                continue
                
            # Income
            if entry["income"] > 0:
                db.add(Transaction(
                    date=entry_date,
                    category="Income",
                    amount=entry["income"],
                    description=entry.get("notes", "")
                ))
            # Expense
            if entry["expense"] > 0:
                db.add(Transaction(
                    date=entry_date,
                    category="Expense",
                    amount=-entry["expense"],
                    description=entry.get("notes", "")
                ))
            count += 1
        db.commit()
    print(f"Migrated {count} old entries! You can now delete finance_diary.json")

if __name__ == "__main__":
    migrate_from_json()