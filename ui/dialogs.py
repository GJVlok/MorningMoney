# ui/dialogs.py
import flet as ft
from src.database import Transaction, Investment, SessionLocal
from src.models import add_or_update_investment


def money_text(value: float, size=20, weight="bold"):
    color = "green" if value >= 0 else "red"
    return ft.Text(f"R{value:,.2f}", size=size, weight=weight, color=color)


def edit_transaction_dialog(page: ft.Page, transaction: Transaction, refresh_all):
    def save_changes(e):
        try:
            new_amount = float(amount_field.value)
            if not switch.value:  # expense
                new_amount = -abs(new_amount)
            transaction.category = category.value
            transaction.amount = new_amount
            transaction.description = notes.value or ""

            with SessionLocal() as db:
                db.merge(transaction)
                db.commit()

            dlg.open = False
            page.snack_bar("Transaction updated!", bgcolor="green")
            page.update()
            refresh_all()
        except Exception:
            page.snack_bar("Invalid input", bgcolor="red")

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

    dlg = ft.AlertDialog(
        title=ft.Text("Edit Transaction"),
        content=ft.Column([
            amount_field, category,
            ft.Row([switch, ft.Text("Income      Expense")]),
            notes
        ], tight=True),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
            ft.TextButton("Save", on_click=save_changes),
        ],
        modal=True,
    )
    page.dialog = dlg
    dlg.open = True
    page.update()


def delete_transaction(page: ft.Page, transaction: Transaction, refresh_all):
    def confirm(e):
        with SessionLocal() as db:
            db.delete(transaction)
            db.commit()
        page.snack_bar("Deleted!", bgcolor="orange")
        page.update()
        refresh_all()

    dlg = ft.AlertDialog(
        title=ft.Text("Delete Transaction?"),
        content=ft.Text("This cannot be undone."),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close_dialog()),
            ft.TextButton("Delete", on_click=confirm, style=ft.ButtonStyle(color="red")),
        ],
        modal=True,
    )
    page.dialog = dlg
    dlg.open = True
    page.update()


def edit_investment_dialog(page: ft.Page, inv: Investment, refresh_all):
    name_field = ft.TextField(value=inv.name, label="Name")
    current = ft.TextField(value=str(inv.current_value), label="Current Value")
    monthly = ft.TextField(value=str(inv.monthly_contribution), label="Monthly")
    rate = ft.TextField(value=str(inv.expected_annual_return), label="Return %")
    year = ft.TextField(value=str(inv.target_year), label="Target Year")

    def save(e):
        try:
            add_or_update_investment(
                name=name_field.value or "Unnamed",
                current_value=float(current.value or 0),
                monthly=float(monthly.value or 0),
                return_rate=float(rate.value or 11),
                target_year=int(year.value or 2050),
            )
            dlg.open = False
            page.snack_bar("Investment updated!", bgcolor="green")
            page.update()
            refresh_all()
        except:
            page.snack_bar("Invalid input", bgcolor="red")
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Edit Investment"),
        content=ft.Column([name_field, current, monthly, rate, year]),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
            ft.TextButton("Save", on_click=save),
        ],
        modal=True,
    )
    page.dialog = dlg
    dlg.open = True
    page.update()


def delete_investment(page: ft.Page, inv: Investment, refresh_all):
    def confirm(e):
        with SessionLocal() as db:
            db.delete(inv)
            db.commit()
        page.snack_bar("Deleted!", bgcolor="orange")
        page.update()
        refresh_all()

    dlg = ft.AlertDialog(
        title=ft.Text("Delete Investment?"),
        content=ft.Text(f"Permanently delete {inv.name}?"),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close_dialog()),
            ft.TextButton("Delete", on_click=confirm, style=ft.ButtonStyle(color="red")),
        ],
        modal=True,
    )
    page.dialog = dlg
    dlg.open = True
    page.update()