# ui/dialogs.py
import flet as ft
import asyncio
from src.database import SessionLocal, Transaction, Investment
from controls.common import money_text
from src.services.investments import add_or_update, get_investments, calculate_future_value_for
from src.services.transactions import get_all_transactions

async def edit_transaction_dialog(page: ft.Page, transaction: Transaction, refresh_all):
    async def save_changes(e):
        try:
            new_amount = float(amount_field.value)
            if not switch.value:
                new_amount = -abs(new_amount)
            transaction.category = category.value
            transaction.amount = new_amount
            transaction.description = notes.value or ""
            with SessionLocal() as db:
                db.merge(transaction)
                db.commit()
            dialog.open = False
            await page.show_snack("Transaction updated!", "green")
            if refresh_all:
                await refresh_all()
        except Exception:
            await page.show_snack("Invalid input", "red")

    amount_field = ft.TextField(value=str(abs(transaction.amount)), label="Amount")
    category = ft.Dropdown(
        label="Category",
        value=transaction.category,
        options=[ft.dropdown.Option(c) for c in [
            "Salary", "Freelance", "Groceries", "Transport",
            "Rent", "Entertainment", "Savings", "Investment"
        ]]
    )
    switch = ft.Switch(label="Income / Expense", value=transaction.amount > 0)
    notes = ft.TextField(value=transaction.description or "", label="Notes")

    dialog = ft.AlertDialog(
        title=ft.Text("Edit Transaction"),
        content=ft.Column([amount_field, category, ft.Row([switch, ft.Text("Income      Expense")]), notes], tight=True),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, "open", False) or page.update()),
            ft.TextButton("Save", on_click=lambda e: page.run_task(save_changes, e)),
        ],
        modal=True,
    )
    page.dialog = dialog
    dialog.open = True
    page.update()

async def delete_transaction(page: ft.Page, transaction: Transaction, refresh_all):
    async def confirm(e):
        with SessionLocal() as db:
            db.delete(transaction)
            db.commit()
        await page.show_snack("Deleted!", "orange")
        if refresh_all:
            await refresh_all()

    dialog = ft.AlertDialog(
        title=ft.Text("Delete Transaction?"),
        content=ft.Text("This cannot be undone."),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close_dialog()),
            ft.TextButton("Delete", on_click=lambda e: page.run_task(confirm, e), style=ft.ButtonStyle(color="red")),
        ],
        modal=True,
    )
    page.dialog = dialog
    dialog.open = True
    page.update()

# Investment dialogs
async def edit_investment_dialog(page: ft.Page, inv: Investment, refresh_all):
    name_field = ft.TextField(value=inv.name, label="Name")
    current = ft.TextField(value=str(inv.current_value), label="Current Value")
    monthly = ft.TextField(value=str(inv.monthly_contribution), label="Monthly")
    rate = ft.TextField(value=str(inv.expected_annual_return), label="Return %")
    year = ft.TextField(value=str(inv.target_year), label="Target Year")

    async def save(e):
        try:
            add_or_update(
                name=name_field.value or "Unnamed",
                current_value=float(current.value or 0),
                monthly=float(monthly.value or 0),
                return_rate=float(rate.value or 11),
                target_year=int(year.value or 2050),
            )
            dialog.open = False
            await page.show_snack("Investment updated!", "green")
            if refresh_all:
                await refresh_all()
        except Exception:
            await page.show_snack("Invalid input", "red")

    dialog = ft.AlertDialog(
        title=ft.Text("Edit Investment"),
        content=ft.Column([name_field, current, monthly, rate, year]),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, "open", False) or page.update()),
            ft.TextButton("Save", on_click=lambda e: page.run_task(save, e)),
        ],
        modal=True,
    )
    page.dialog = dialog
    dialog.open = True
    page.update()

async def delete_investment(page: ft.Page, inv: Investment, refresh_all):
    async def confirm(e):
        with SessionLocal() as db:
            db.delete(inv)
            db.commit()
        await page.show_snack("Deleted!", "orange")
        if refresh_all:
            await refresh_all()

    dialog = ft.AlertDialog(
        title=ft.Text("Delete Investment?"),
        content=ft.Text(f"Permanently delete {inv.name}?"),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close_dialog()),
            ft.TextButton("Delete", on_click=lambda e: page.run_task(confirm, e), style=ft.ButtonStyle(color="red")),
        ],
        modal=True,
    )
    page.dialog = dialog
    dialog.open = True
    page.update()
