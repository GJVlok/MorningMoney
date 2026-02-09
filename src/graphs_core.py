# src/graphs_core.py
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from src.services.core import svc_get_monthly_summary

# Should this be sync or async?
async def generate_chart():
    summaries = svc_get_monthly_summary()
    if not summaries:
        return "No data yet!"
    
    months = [s['month'] for s in summaries]
    incomes = [s['income'] for s in summaries]
    expenses = [s['expenses'] for s in summaries]

    plt.figure(figsize=(10, 5))
    plt.plot(months, incomes, label='Income', color='green')
    plt.plot(months, expenses, label='Expenses', color='red')
    plt.xlabel('Month')
    plt.ylabel('Amount (R)')
    plt.title('Monthly Income vs Expenses')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64, {img_base64}"