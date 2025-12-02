# src/services/investments.py
from typing import List
from ..database import Investment
from ..models import (
    add_or_update_investment,
    get_investments as _get_investment,
    calculate_future_value as _calculate_future_value,
    get_total_projected_wealth as _get_total_projected_wealth,
)

def add_or_update(name: str, current_value: float, monthly: float = 0, return_rate: float = 10.0, target_year: int = 2050, notes: str = ""):
    add_or_update_investment(name=name, current_value=current_value, monthly=monthly, return_rate=return_rate, target_year=target_year, notes=notes)

def get_investments() -> List[Investment]:
    return _get_investment()

def calculate_future_value_for(inv: Investment, extra_monthly: float = 0) -> float:
    return _calculate_future_value(inv, extra_monthly)

def get_total_projected_wealth(target_year: int = None) -> float:
    """Service wrapper — can add logging, caching, etc. later"""
    return _get_total_projected_wealth(target_year)
