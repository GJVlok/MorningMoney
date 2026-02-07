# utils/config.py
import os
from decimal import Decimal

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "finance.db")
DEFAULT_RETURN_RATE = Decimal('11.0') # Use decimal for precision
DEFAULT_TARGET_YEAR = 2050
CURRENCY_SYMBOL = "R"
LOG_LEVEL = "DEBUG" # For future logging
