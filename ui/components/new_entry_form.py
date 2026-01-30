# ui/components/new_entry_form.py
import flet as ft
from datetime import date
from src.services.core import svc_add_transaction


def new_entry_form(page: ft.Page, refresh_all) -> ft.Control:
    amount = ft.TextField(
        label="Amount (R)",
        keyboard_type=ft.KeyboardType.NUMBER,
        autofocus=True,
        expand=True,
    )

    category = ft.Dropdown(
        label="Category",
        value="Groceries",
        options=[
            ft.dropdown.Option(c)
            for c in [
                "Salary",
                "Freelance",
                "Other Income",
                "Groceries",
                "Transport",
                "Entertainment",
                "Rent",
                "Subscriptions",
                "Savings",
                "Investment",
            ]
        ],
        expand=True,
    )

    is_income = ft.Switch(label="Income", value=False)

    notes = ft.TextField(
        label="Notes (optional)",
        multiline=True,
        min_lines=1,
        max_lines=3,
    )

    feedback = ft.Text(size=14)

    async def submit():
        try:
            value = float(amount.value or 0)
            if not is_income.value:
                value = -abs(value)
            svc_add_transaction(date=date.today(), category=category.value or "Uncategorized", amount=value, description=notes.value or "")
            # ... reset form ...
            await page.show_snack("Transaction saved.", "green")
        except ValueError as ve:
            await page.show_snack(f"Invalid amount: {str(ve)}", "red") # Teach: Specific feedback builds user trust
        except Exception as ex:
            await page.show_snack("Unexpected error-try again!", "orange") # Positivity: Frame errors as temporary
            return

        svc_add_transaction(
            date=date.today(),
            category=category.value or "Uncategorized",
            amount=value,
            description=notes.value or "",
        )

        # reset form
        amount.value = ""
        notes.value = ""
        is_income.value = False

        feedback.value = "Transaction saved."
        feedback.color = "green"

        await page.safe_update()

        if refresh_all:
            await refresh_all()

    return ft.Column(
        [
            ft.Text("Add Transaction", size=28, weight="bold"),
            amount,
            category,
            ft.Row(
                [
                    is_income,
                    ft.Text("Income / Expense", color="grey"),
                ]
            ),
            notes,
            ft.ElevatedButton(
                "Save Transaction",
                icon=ft.Icons.SAVE,
                on_click=lambda _: page.run_task(submit),
            ),
            feedback,
        ],
        scroll="auto",
        spacing=12,
    )
