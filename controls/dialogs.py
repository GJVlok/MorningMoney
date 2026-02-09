# controls/dialogs.py
import flet as ft
from typing import TYPE_CHECKING
from decimal import Decimal, InvalidOperation

from src.services.core import (
    svc_add_or_update_investment,
    svc_delete_transaction,
    svc_delete_investment,
    svc_update_transaction,
)

if TYPE_CHECKING:
    from src.database import Transaction, Investment

def clean_decimal_input(value: str) -> Decimal:
    """Helper to strip common currency characters and return a Decimal."""
    if not value or not value.strip():
        return Decimal("0.00")
    # Remove currency symbols and commas to prevent Decimal constructor errors
    clean_val = value.replace("R", "").replace("$", "").replace(",", "").strip()
    try:
        return Decimal(clean_val)
    except InvalidOperation:
        raise ValueError("Invalid number format")

# -------------------------
# Transactions
# -------------------------

async def edit_transaction_dialog(page: ft.Page, transaction, refresh_all):
    async def save_changes(e):
        try:
            # Clean and parse the decimal
            new_amount = clean_decimal_input(amount_field.value)

            if new_amount == 0:
                await page.show_snack("Amount cannot be zero", "red")
                return
            
            # Apply sign logic based on switch (Income vs Expense)
            # If switch is True (Income), ensure amount is positive.
            # If False (Expense), ensure amount is negative.
            if switch.value:
                new_amount = abs(new_amount)
            else:
                new_amount = -abs(new_amount)

            svc_update_transaction(
                transaction.id,
                category=category.value,
                amount=new_amount,
                description=notes.value or "",
            )

            dialog.open = False
            page.update() # Close dialog immediately
            await page.show_snack("Transaction updated!", "green")
            if refresh_all:
                await refresh_all()

        except (ValueError, InvalidOperation):
            await page.show_snack("Invalid input", "red")
        except Exception as ex:
            await page.show_snack(f"Error: {str(ex)}", "red")

    # Display current absolute value in the field
    current_amt = Decimal(str(transaction.amount or '0'))
    amount_field = ft.TextField(value=f"{abs(current_amt):.2f}", label="Amount")

############################################################################
        # Change the catecories #
    category = ft.Dropdown(
        label="Category",
        value=transaction.category,
        options=[ft.dropdown.Option(c) for c in [
            "Salary", "Freelance", "Groceries", "Transport",
            "Rent", "Entertainment", "Savings", "Investment"
        ]],
    )

    # transaction.amount > 0 means it's Income (Switch = True)
    switch = ft.Switch(label="Is this Income?", value=transaction.amount > 0)
    notes = ft.TextField(value=transaction.description or "", label="Notes")

    dialog = ft.AlertDialog(
        title=ft.Text("Edit Transaction"),
        content=ft.Column([
            amount_field,
            category,
            ft.Row([switch, ft.Text(" Income if checked")]), notes
            ],
            tight=True,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close_dialog()),
            ft.TextButton("Save", on_click=lambda e: page.run_task(save_changes, e)),
        ],
        modal=True,
    )

##############################################################################################

    page.dialog = dialog
    dialog.open = True
    page.update()


async def delete_transaction(page: ft.Page, transaction, refresh_all):
    async def confirm(e):
        svc_delete_transaction(transaction.id)
        await page.show_snack("Deleted!", "orange")
        if refresh_all:
            await refresh_all()

    dialog = ft.AlertDialog(
        title=ft.Text("Delete Transaction?"),
        content=ft.Text("This cannot be undone."),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close_dialog()),
            ft.TextButton(
                "Delete",
                on_click=lambda e: page.run_task(confirm, e),
                style=ft.ButtonStyle(color="red"),
            ),
        ],
        modal=True,
    )

    page.dialog = dialog
    dialog.open = True
    page.update()


# -------------------------
# Investments
# -------------------------

async def edit_investment_dialog(page: ft.Page, inv, refresh_all):
    # Ensure current values are treated as decimals for the display string
    name_field = ft.TextField(value=inv.name, label="Name")
    current = ft.TextField(value=f"{Decimal(str(inv.current_value)):.2f}", label="Current Value", keyboard_type=ft.KeyboardType.NUMBER)
    monthly = ft.TextField(value=f"{Decimal(str(inv.monthly_contribution)):.2f}", label="Monthly", keyboard_type=ft.KeyboardType.NUMBER)
    rate = ft.TextField(value=f"{Decimal(str(inv.expected_annual_return)):.2f}", label="Return %", keyboard_type=ft.KeyboardType.NUMBER)
    year = ft.TextField(value=str(inv.target_year), label="Target Year", keyboard_type=ft.KeyboardType.NUMBER)

    async def save(e):
        try:
            svc_add_or_update_investment(
                name=name_field.value or "Unnamed",
                current_value=clean_decimal_input(current.value),
                monthly=clean_decimal_input(monthly.value),
                return_rate=clean_decimal_input(rate.value),
                target_year=int(year.value or 2050),
            )

            dialog.open = False
            page.update()
            await page.show_snack("Investment updated!", "green")
            if refresh_all:
                await refresh_all()
        except (ValueError, InvalidOperation):
            await page.show_snack("Invalid number in fields", "red")
        except Exception:
            await page.show_snack("Save failed", "red")

    dialog = ft.AlertDialog(
        title=ft.Text("Edit Investment"),
        content=ft.Column([name_field, current, monthly, rate, year], tight=True),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close_dialog()),
            ft.TextButton("Save", on_click=lambda e: page.run_task(save, e)),
        ],
        modal=True,
    )

    page.dialog = dialog
    dialog.open = True
    page.update()


async def delete_investment(page: ft.Page, inv, refresh_all):
    async def confirm(e):
        svc_delete_investment(inv.id)
        await page.show_snack("Deleted!", "orange")
        if refresh_all:
            await refresh_all()

    dialog = ft.AlertDialog(
        title=ft.Text("Delete Investment?"),
        content=ft.Text(f"Permanently delete {inv.name}?"),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close_dialog()),
            ft.TextButton(
                "Delete",
                on_click=lambda e: page.run_task(confirm, e),
                style=ft.ButtonStyle(color="red"),
            ),
        ],
        modal=True,
    )

    page.dialog = dialog
    dialog.open = True
    page.update()
