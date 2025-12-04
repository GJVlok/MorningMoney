# src/services/ui_state.py
from .transactions import get_balance
from .investments import get_total_projected_wealth

def daily_message_inputs():
    balance = get_balance()
    projected_wealth = get_total_projected_wealth()
    return balance, projected_wealth
