import pytest
from decimal import Decimal
from datetime import date
from src.database import Investment
from src.models import calculate_future_value

def test_lump_sum_no_contributions():
    """
    Test 1: R10,000 at 10% for 1 year with NO monthly contributions.
    Expected: 10000 * (1 + 0.10/12)^12
    Calculated manually: R11,047.13
    """
    inv = Investment(
        current_value=Decimal("10000.00"),
        monthly_contribution=Decimal("0.00"),
        expected_annual_return=Decimal("10.00"),
        target_year=date.today().year + 1
    )
    result = calculate_future_value(inv)
    assert result == Decimal("11047.13")

def test_monthly_contributions_no_initial():
    """
    Test 2: R0 initial, but R1,000/month at 12% for 1 year.
    Formula: PMT * (((1 + r)^n - 1) / r)
    Calculated manually: R12,682.50
    """
    inv = Investment(
        current_value=Decimal("0.00"),
        monthly_contribution=Decimal("1000.00"),
        expected_annual_return=Decimal("12.00"),
        target_year=date.today().year + 1
    )
    result = calculate_future_value(inv)
    # 12% annual = 1% monthly. 1000 * ((1.01^12 - 1) / 0.01) = 12682.503...
    assert result == Decimal("12682.50")

def test_zero_interest_growth():
    """
    Test 3: R1,000 initial + R100/month for 1 year at 0% interest.
    Expected: 1000 + (100 * 12) = 2200
    """
    inv = Investment(
        current_value=Decimal("1000.00"),
        monthly_contribution=Decimal("100.00"),
        expected_annual_return=Decimal("0.00"),
        target_year=date.today().year + 1
    )
    result = calculate_future_value(inv)
    assert result == Decimal("2200.00")