# ui/components/new_entry_form.py
import flet as ft
import asyncio
from datetime import date
from src.services import svc_add_transaction

def new_entry_form(page: ft.Page, refresh_all) -> ft.Column:
    amount = ft.TextField(label="Amount (R)", keyboard_type="number", expand=True)
    category = ft.Dropdown(
        label="Category",
        value="Groceries",
        options=[ft.dropdown.Option(c) for c in [
            "Salary", "Freelance", "Other Income",
            "Groceries", "Transport", "Entertainment", "Rent",
            "Subscriptions", "Savings", "Investment"
        ]],
        expand=True,
    )
    type_switch = ft.Switch(label="Income (on) / Expense (off)", value=False)
    notes = ft.TextField(label="Notes (optional)", multiline=True, min_lines=1, max_lines=3)
    message = ft.Text()

    async def save(e):
        try:
            amt = float(amount.value or "0")
            if not type_switch.value:
                amt = -abs(amt)
        except ValueError:
            message.value = "Invalid amount!"
            message.color = "red"
            page.update()
            return

        svc_add_transaction(date=date.today(), category=category.value or "Uncategorized", amount=amt, description=notes.value or "")
        amount.value = ""
        notes.value = ""
        message.value = "Saved!"
        message.color = "green"
        page.update()
        if refresh_all:
            await refresh_all()

    return ft.Column([
        ft.Text("Add Transaction", size=28, weight="bold"),
        amount,
        category,
        ft.Row([type_switch, ft.Text("Income          Expense")]),
        notes,
        ft.ElevatedButton("Save Transaction", on_click=lambda e: page.run_task(save, e)),
        message,
    ], scroll="auto")
