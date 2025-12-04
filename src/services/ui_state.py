# src/services/ui_state.py
from src.services.core import svc_get_balance
from src.services.core import svc_get_total_projected_wealth

def daily_message_inputs():
    balance = svc_get_balance()
    projected_wealth = svc_get_total_projected_wealth()
    return balance, projected_wealth
