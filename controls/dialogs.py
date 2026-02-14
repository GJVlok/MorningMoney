# controls/dialogs.py
import flet as ft
from typing import TYPE_CHECKING
from datetime import date
from decimal import Decimal, InvalidOperation

from src.services.core import (
    svc_add_or_update_investment,
    svc_delete_transaction,
    svc_delete_investment,
    svc_update_transaction,
)

print("===== CORRECT dialogs.py LOADED – TYPE_CHECKING is present =====")

if TYPE_CHECKING:
    from src.database import Transaction, Investment


def clean_decimal_input(value: str | None) -> Decimal:
    """Helper to strip common currency characters and return a Decimal."""
    if not value or not value.strip():
        return Decimal("0.00")
    # Remove currency symbols and commas
    clean_val = value.replace("R", "").replace("$", "").replace(",", "").strip()
    try:
        return Decimal(clean_val)
    except InvalidOperation:
        raise ValueError("Invalid number format")


# ────────────────────────────────────────────────
# Helper to close any dialog safely
# ────────────────────────────────────────────────
def close_dialog(page: ft.Page):
    if page.dialog:
        page.dialog.open = False
        page.update()


# ────────────────────────────────────────────────
# TRANSACTION – Edit
# ────────────────────────────────────────────────
async def edit_transaction_dialog(page: ft.Page, transaction: Transaction, refresh_all):
    """
    Modern dialog using page.dialog + explicit open/close.
    Shows absolute amount + switch for income/expense.
    Basic date validation on save.
    """

    def on_cancel(e):
        close_dialog(page)

    async def save_changes(e):
        try:
            # ── Amount ───────────────────────────────────────
            raw_amount = clean_decimal_input(amount_field.value)
            if raw_amount == 0:
                await page.show_snack("Amount cannot be zero", bgcolor="red")
                return

            amount = abs(raw_amount) if income_switch.value else -abs(raw_amount)

            # ── Date validation ──────────────────────────────
            try:
                dt = date.fromisoformat(date_field.value.strip())
            except ValueError:
                await page.show_snack("Invalid date format — use YYYY-MM-DD", bgcolor="red")
                return

            # ── Save ─────────────────────────────────────────
            svc_update_transaction(
                transaction_id=transaction.id,
                category=category_dropdown.value,
                amount=amount,
                description=notes_field.value.strip() or "",
                date=dt,
                tags=tags_field.value.strip() or None,
            )

            close_dialog(page)
            await page.show_snack("Transaction updated successfully", bgcolor="#94d494")
            if refresh_all:
                await refresh_all()

        except ValueError as ve:
            await page.show_snack(f"Invalid input: {ve}", bgcolor="red")
        except Exception as ex:
            await page.show_snack(f"Save failed: {str(ex)}", bgcolor="red")

    # ── Controls ────────────────────────────────────────
    amount_field = ft.TextField(
        label="Amount",
        value=f"{abs(Decimal(str(transaction.amount or '0'))):.2f}",
        keyboard_type=ft.KeyboardType.NUMBER,
        autofocus=True,
        prefix_text="R ",
    )

    category_dropdown = ft.Dropdown(
        label="Category",
        value=transaction.category,
        options=[ft.dropdown.Option(c) for c in [
            "Salary", "Freelance", "Groceries", "Transport",
            "Rent", "Entertainment", "Savings", "Investment"
        ]],
    )

    income_switch = ft.Switch(
        label="This is Income",
        value=transaction.amount >= 0
    )

    notes_field = ft.TextField(
        value=transaction.description or "",
        label="Notes (optional)",
        multiline=True,
        min_lines=2,
        max_lines=5,
    )

    date_field = ft.TextField(
        value=transaction.date.isoformat() if transaction.date else date.today().isoformat(),
        label="Date (YYYY-MM-DD)",
    )

    tags_field = ft.TextField(
        value=transaction.tags or "",
        label="Tags (comma separated)",
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Transaction"),
        content=ft.Column(
            controls=[
                amount_field,
                category_dropdown,
                income_switch,
                notes_field,
                date_field,
                tags_field,
            ],
            tight=True,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=on_cancel),
            ft.TextButton(
                "Save",
                on_click=lambda e: page.run_task(save_changes, e),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Open dialog — modern Flet style
    page.dialog = dialog
    dialog.open = True
    page.update()


# ────────────────────────────────────────────────
# TRANSACTION – Delete
# ────────────────────────────────────────────────
async def delete_transaction(page: ft.Page, transaction: Transaction, refresh_all):
    async def confirm_delete(e):
        svc_delete_transaction(transaction.id)
        close_dialog(page)
        await page.show_snack("Transaction deleted", bgcolor="orange")
        if refresh_all:
            await refresh_all()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Delete Transaction?"),
        content=ft.Text("This action cannot be undone."),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: close_dialog(page)),
            ft.TextButton(
                "Delete",
                on_click=lambda e: page.run_task(confirm_delete, e),
                style=ft.ButtonStyle(color=ft.colors.RED),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = dialog
    dialog.open = True
    page.update()


# ────────────────────────────────────────────────
# INVESTMENT – Edit
# ────────────────────────────────────────────────
async def edit_investment_dialog(page: ft.Page, inv: Investment, refresh_all):
    async def save_changes(e):
        try:
            svc_add_or_update_investment(
                name=name_field.value.strip() or "Unnamed Investment",
                current_value=clean_decimal_input(current_field.value),
                monthly=clean_decimal_input(monthly_field.value),
                return_rate=clean_decimal_input(rate_field.value),
                target_year=int(year_field.value.strip() or "2050"),
                notes="",  # add notes field later if needed
            )
            close_dialog(page)
            await page.show_snack("Investment updated", bgcolor="#94d494")
            if refresh_all:
                await refresh_all()
        except ValueError as ve:
            await page.show_snack(f"Invalid number: {ve}", bgcolor="red")
        except Exception as ex:
            await page.show_snack(f"Save failed: {str(ex)}", bgcolor="red")

    name_field = ft.TextField(
        label="Investment / Fund Name",
        value=inv.name or "",
    )

    current_field = ft.TextField(
        label="Current Value",
        value=f"{Decimal(str(inv.current_value)):.2f}",
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_text="R ",
    )

    monthly_field = ft.TextField(
        label="Monthly Contribution",
        value=f"{Decimal(str(inv.monthly_contribution)):.2f}",
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_text="R ",
    )

    rate_field = ft.TextField(
        label="Expected Annual Return %",
        value=f"{Decimal(str(inv.expected_annual_return)):.2f}",
        keyboard_type=ft.KeyboardType.NUMBER,
        suffix_text="%",
    )

    year_field = ft.TextField(
        label="Target Year",
        value=str(inv.target_year or 2050),
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Investment"),
        content=ft.Column(
            [
                name_field,
                current_field,
                monthly_field,
                rate_field,
                year_field,
            ],
            tight=True,
            spacing=16,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: close_dialog(page)),
            ft.TextButton(
                "Save",
                on_click=lambda e: page.run_task(save_changes, e),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = dialog
    dialog.open = True
    page.update()


# ────────────────────────────────────────────────
# INVESTMENT – Delete
# ────────────────────────────────────────────────
async def delete_investment(page: ft.Page, inv: Investment, refresh_all):
    async def confirm_delete(e):
        svc_delete_investment(inv.id)
        close_dialog(page)
        await page.show_snack("Investment deleted", bgcolor="orange")
        if refresh_all:
            await refresh_all()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Delete Investment?"),
        content=ft.Text(f"Permanently delete {inv.name or 'this investment'}?"),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: close_dialog(page)),
            ft.TextButton(
                "Delete",
                on_click=lambda e: page.run_task(confirm_delete, e),
                style=ft.ButtonStyle(color=ft.colors.RED),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = dialog
    dialog.open = True
    page.update()