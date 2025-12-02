# src/services/ui_state.py
from .transactions import get_balance
from .investments import get_total_projected_wealth

def daily_message_inputs():
    bal = get_balance()
    proj = get_total_projected_wealth()
    return bal, proj
