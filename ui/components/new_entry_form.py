# ui/components/new_entry_form.py
import flet as ft
from datetime import date
from decimal import Decimal, InvalidOperation
from src.services.core import svc_add_transaction


def new_entry_form(page: ft.Page, refresh_all) -> ft.Control:

    # Helper to clean currency strings (reusing logic from dialogs)
    def get_clean_amount(val: str) -> Decimal:
        if not val or not val.strip():
            return Decimal("0.00")
        # Strip R, $, and commas
        clean = val.replace("R", "").replace("$", "").replace(",", "").strip()
        return Decimal(clean)
    
    amount = ft.TextField(
        label="Amount (R)",
        keyboard_type=ft.KeyboardType.NUMBER,
        autofocus=True,
        expand=True,
        border_color="#afdaaf",
        focused_border_color="white",
        hint_text="0.00"
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
        border_color="#ffd2d2", # Start red for expense
    )

    # Handler to update dropdown when type changes
    def update_category_dropdown(e):
        # Safely extrac selection
        selected_type = next(iter(type_selector.selected)) if type_selector.selected else "expense"  # Get "income" or "expense"

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

    async def submit():
        try:
            # 1. Clean and convert to Decimal
            raw_value = get_clean_amount(amount.value)

            if raw_value == 0:
                await page.show_snack("Please enter an amount greater than zero.", "orange")
                return

            # 2. Ensure correct sign logic
            # Use abs() first to prevent user-entered negatives from flipping back to positive
            selected_type = next(iter(type_selector.selected)) if type_selector.selected else "expense"
            if selected_type == "income":
                final_amount = abs(raw_value)
            else:
                final_amount = -abs(raw_value)

            # 3. Save to DB via service
            # SINGLE write
            svc_add_transaction(
                date=date.today(),
                category=category_dropdown.value or "Uncategorized",
                amount=final_amount,
                description=notes.value or "",
            )

            # 4. Success UI Flow
            # Reset form AFTER success
            amount.value = ""
            notes.value = ""
            # Feedback
            await page.show_snack(f"Saved: R{abs(final_amount):,.2f}", "green")

            # 5. Refresh logic
            if refresh_all:
                await refresh_all() # Note the () - executing the callback

            await page.safe_update()

        except (InvalidOperation, ValueError):
            await page.show_snack("Invalid number! Use digits and '.' only.", "red")
        except Exception as e:
            print(f"From Error: {e}")
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
        ],
        scroll="auto",
        spacing=12,
    )
