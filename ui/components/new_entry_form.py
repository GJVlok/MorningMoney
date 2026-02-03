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
        border_color="#afdaaf",
        focused_border_color="white",
    )

    # Seperate category lists - easy to expand later!
    # Coding tip: Use lists for flexibility; you could even load these from a config file someday for user-custom categories.
    INCOME_CATEGORIES = [
        "Salary", "Freelance", "Side Hustle", "Investment Return",
        "Gift", "Refund", "Other Income"
    ]

    EXPENSE_CATEGORIES = [
        "Groceries", "Meat", "Toiletries", "Clothes", "Transport",
        "Fuel", "Eating Out", "Entertainment", "Subscriptions",
        "Rent / Bond", "Electricity / Water", "Phone / Internet",
        "Medical", "Insurance", "Savings Transfer", "Debt Repayment",
        "Education", "Gifts Given", "Hobbies", "Travel", "Other Expense"
    ]

    # Segmented button for type toggle — starts with "Expense" selected
    type_selector = ft.SegmentedButton(
        selected={"expense"},  # Default to expense
        show_selected_icon=False,  # Clean look
        segments=[
            ft.Segment(
                value="income",
                label=ft.Text("Income"),
            ),
            ft.Segment(
                value="expense",
                label=ft.Text("Expense"),
            ),
        ],
        on_change=lambda e: update_category_dropdown(e),  # We'll define this next
    )

    # Single dropdown — options update based on type
    category_dropdown = ft.Dropdown(
        label="Category",
        value=EXPENSE_CATEGORIES[0],  # Default to first expense
        options=[ft.dropdown.Option(c) for c in EXPENSE_CATEGORIES],  # Starts with expenses
        expand=True,
        icon=ft.Icons.CATEGORY,
        border_color="#afdaaf",
    )

    # Handler to update dropdown when type changes
    def update_category_dropdown(e):
        selected_type = next(iter(e.control.selected)) if e.control.selected else "expense"  # Get "income" or "expense"

        if selected_type == "income":
            category_dropdown.options = [ft.dropdown.Option(c) for c in INCOME_CATEGORIES]
            category_dropdown.value = INCOME_CATEGORIES[0]
            category_dropdown.border_color = "#afdaaf"  # Green for income
        else:
            category_dropdown.options = [ft.dropdown.Option(c) for c in EXPENSE_CATEGORIES]
            category_dropdown.value = EXPENSE_CATEGORIES[0]
            category_dropdown.border_color = "#ffd2d2"  # Red-ish for expense
        
        page.update()

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

            if "expense" in type_selector.selected:
                value = -abs(value)

            category = category_dropdown.value or "Uncategorized"

            # SINGLE write
            svc_add_transaction(
                date=date.today(),
                category=category,
                amount=value,
                description=notes.value or "",
            )

            # Reset form AFTER success
            amount.value = ""
            notes.value = ""
            type_selector.selected = {"expense"}
            update_category_dropdown(None) # Reset to expense options

            await page.show_snack("Transaction saved.", "green")

            await page.safe_update()

            if refresh_all:
                await refresh_all
            
        except ValueError:
            await page.show_snack("Invalid input!", "red")

        except Exception as e:
            await page.show_snack("Something went wrong.", "red")

    return ft.Column(
        controls=[
            type_selector,
            amount,
            category_dropdown,
            notes,
            ft.ElevatedButton(
                "Save Transaction",
                icon=ft.Icons.SAVE,
                bgcolor="#afdaaf",
                color="black",
                on_click=lambda _: page.run_task(submit),
            ),
            ft.Container(
                content=feedback,
                alignment=ft.alignment.center,
                padding=8,
                opacity=0 if not feedback.value else 1,
            ),
        ],
        scroll="auto",
        spacing=12,
    )
