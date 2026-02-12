# ui/components/new_entry_form.py
import flet as ft
from datetime import date as dt_date
from decimal import Decimal, InvalidOperation
from src.services.core import svc_add_transaction
from controls.common import money_text


def new_entry_form(page: ft.Page, refresh_all) -> ft.Control:
    today = dt_date.today()
    selected_date_ref = ft.Ref[ft.Text]()
    date_hidden = ft.Ref[ft.DatePicker]()

    def on_date_change(e):
        selected_date_ref.current.value = e.control.value.strftime("%d %b %Y")
        page.session.set("last_used_date", e.control.value)
        page.update()

    date_picker = ft.DatePicker(
        ref=date_hidden,
        first_date=dt_date(today.year - 2, 1, 1),
        last_date=dt_date(today.year + 1, 12, 31),
        value=today,
        on_change=on_date_change,
    )

    date_row = ft.Row(
        [
            ft.ElevatedButton(
                text="Choose Date",
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=lambda _: page.open(date_picker),
            ),
            ft.Text(
                ref=selected_date_ref,
                value=today.strftime("%d %b %Y"),
                color=ft.Colors.PRIMARY,
                weight=ft.FontWeight.BOLD,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=16,
    )

    def get_is_expense():
        return "expense" in type_selector.selected

    def update_discount_fields(e=None):
        is_expense = get_is_expense()

        # Toggle main discount UI
        discount_container.visible = is_expense
        discount_type.visible = is_expense

        # Toggle specific discount modes
        fixed_fields.visible = is_expense and discount_type.value == "Fixed Prices"
        percent_fields.visible = is_expense and discount_type.value == "Percentage"

        # Attach preview updates
        for field in [
            fixed_fields.controls[0],
            fixed_fields.controls[1],
            percent_fields.controls[0],
            percent_fields.controls[1],
        ]:
            field.on_change = lambda e: update_saved_preview()

        # Focus AFTER visibility is set
        if fixed_fields.visible:
            page.focus(fixed_fields.controls[0])
        elif percent_fields.visible:
            page.focus(percent_fields.controls[0])

        update_saved_preview()
        page.update()

    def on_type_change(e):
        update_category_dropdown(e)
        update_discount_fields(e)

    type_selector = ft.SegmentedButton(
        selected={"expense"},
        show_selected_icon=False,
        segments=[
            ft.Segment(value="income", label=ft.Text("Income")),
            ft.Segment(value="expense", label=ft.Text("Expense")),
        ],
        on_change=on_type_change,
    )

    discount_type = ft.Dropdown(
        label="Discount Type",
        options=[
            ft.dropdown.Option("None"),
            ft.dropdown.Option("Fixed Prices"),
            ft.dropdown.Option("Percentage"),
        ],
        value="None",
        on_change=lambda e: update_discount_fields(),
    )

    tags_field = ft.TextField(
        label="Tags (comma-seperated, e.g., milk,shop:Checkers)",
        expand=True,
    )

    fixed_fields = ft.Row(visible=False, controls=[
        ft.TextField(label="Original Price (R)", keyboard_type=ft.KeyboardType.NUMBER, expand=True),
        ft.TextField(label="Discounted Price (R)", keyboard_type=ft.KeyboardType.NUMBER, expand=True),
    ])

    percent_fields = ft.Row(visible=False, controls=[
        ft.TextField(label="Original Price (R)", keyboard_type=ft.KeyboardType.NUMBER, expand=True),
        ft.TextField(label="Discount % (e.g., 20)", keyboard_type=ft.KeyboardType.NUMBER, expand=True),
    ])

    def get_clean_amount(val: str) -> Decimal:
        if not val or not val.strip():
            return Decimal("0.00")
        clean = val.replace("R", "").replace("$", "").replace(",", "").strip()
        return Decimal(clean)
    
    amount = ft.TextField(
        label="Amount",
        prefix_text="R ",
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d{0,2}$"),
        on_change=lambda e: update_amount_preview(),
        expand=True,
    )
    amount_preview = ft.Text(
        "...",
        size=12,
        color=ft.Colors.GREY_400,
        italic=True,
    )

    saved_preview = ft.Text(
        "",
        size=14,
        weight=ft.FontWeight.W_500,
        color=ft.Colors.GREEN_300,
        text_align=ft.TextAlign.CENTER,
    )

    discount_container = ft.Container(
        visible=False,  # We'll control this based on transaction type
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text("Discount / Deal Tracking",
                        size=16,
                        weight="bold",
                        color=ft.Colors.AMBER),
                discount_type,  # your existing Dropdown: None / Fixed Prices / Percentage
                fixed_fields,
                percent_fields,
                saved_preview,
            ],
        ),
        padding=16,
        border=ft.border.all(1, ft.Colors.AMBER_200),
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.AMBER),
    )

    def update_saved_preview():
        saved = Decimal('0.00')
        message = ""
        error = ""

        try:
            is_expense = get_is_expense()
            if not is_expense or discount_type.value == "None":
                saved_preview.value = ""
                saved_preview.update()
                return

            if discount_type.value == "Fixed Prices":
                orig_str = fixed_fields.controls[0].value.strip()
                disc_str = fixed_fields.controls[1].value.strip()
                if not orig_str or not disc_str:
                    return

                orig = Decimal(orig_str)
                disc = Decimal(disc_str)

                if orig <= disc:
                    error = "Original price must be higher than discounted price"
                else:
                    saved = orig - disc
                    message = f"You save R{saved:,.2f} — great deal!"

            elif discount_type.value == "Percentage":
                orig_str = percent_fields.controls[0].value.strip()
                perc_str = percent_fields.controls[1].value.strip()
                if not orig_str or not perc_str:
                    return

                orig = Decimal(orig_str)
                perc = Decimal(perc_str)

                if perc < 0 or perc > 100:
                    error = "Discount % should be between 0 and 100"
                else:
                    saved = orig * (perc / Decimal('100'))
                    paid = orig - saved
                    message = f"You save R{saved:,.2f} ({perc}%) — smart shopping!"

            if error:
                saved_preview.value = error
                saved_preview.color = ft.Colors.RED_400
            else:
                saved_preview.value = message
                saved_preview.color = ft.Colors.GREEN_300

        except Exception:
            saved_preview.value = "Check the numbers — something doesn't add up"
            saved_preview.color = ft.Colors.RED_400

        saved_preview.update()


    def update_amount_preview():
        try:
            val = Decimal(amount.value or "0")
            if val < 0:
                amount_preview.value = f"Expense of {money_text(-val).value}"
            else:
                amount_preview.value = f"Income of {money_text(val).value}"
            amount_preview.update()
        except:
            amount_preview.value = ""
            amount_preview.update()

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

    category_dropdown = ft.Dropdown(
        label="Category",
        value=EXPENSE_CATEGORIES[0],
        options=[ft.dropdown.Option(c) for c in EXPENSE_CATEGORIES],
        expand=True,
        icon=ft.Icons.CATEGORY,
        border_color=ft.Colors.RED_400,
    )
    def update_category_dropdown(e):
        selected_type = "income" if "income" in type_selector.selected else "expense"

        if selected_type == "income":
            category_dropdown.options = [ft.dropdown.Option(c) for c in INCOME_CATEGORIES]
            category_dropdown.value = INCOME_CATEGORIES[0]
            category_dropdown.border_color = "#94d494"  # Green for income
        else:
            category_dropdown.options = [ft.dropdown.Option(c) for c in EXPENSE_CATEGORIES]
            category_dropdown.value = EXPENSE_CATEGORIES[0]
            category_dropdown.border_color = "#c21717"  # Red-ish for expense
        
        page.update()

    notes = ft.TextField(
        label="Notes (optional)",
        multiline=True,
        max_length=256,
        expand=True,
    )

    async def submit():
        try:
            raw_value = get_clean_amount(amount.value)
            if raw_value == 0:
                await page.show_snack("Please enter an amount greater than zero.", "orange")
                return
            
            try:
                entry_date = date_picker.value if isinstance(date_picker.value, dt_date) else dt_date.fromisoformat(date_picker.value)
            except (ValueError, AttributeError):
                entry_date = dt_date.today()
            tags_str = tags_field.value.strip() if tags_field.value else ""

            selected_type = next(iter(type_selector.selected)) if type_selector.selected else "expense"
            if selected_type == "income":
                final_amount = abs(raw_value)
            else:
                final_amount = -abs(raw_value)

            saved = Decimal('0.00')
            if selected_type == "expense" and discount_type.value != "None":
                if discount_type.value == "Fixed Prices":
                    orig = get_clean_amount(fixed_fields.controls[0].value)
                    disc = get_clean_amount(fixed_fields.controls[1].value)
                    if orig <= disc:
                        raise ValueError("Original must be > discounted!")
                    if orig <= 0:
                        raise ValueError("Original price must be greater than 0.")
                    saved = orig - disc
                    final_amount = -disc
                else:
                    orig = get_clean_amount(percent_fields.controls[0].value)
                    perc_raw = percent_fields.controls[1].value or '0'
                    perc = Decimal(''.join(filter(lambda c: c.isdigit() or c=='.', perc_raw)))
                    if perc < 0 or perc > 100:
                        raise ValueError("Percent 0-100!")
                    if orig <= 0:
                        raise ValueError("Original price must be greater than 0.")
                    saved = orig * (perc / Decimal('100'))
                    paid = orig - saved
                    final_amount = -paid

            svc_add_transaction(
                date=entry_date,
                category=category_dropdown.value or "Uncategorized",
                amount=final_amount,
                description=notes.value or "",
                tags=tags_str,
                saved_amount=saved
            )

            if saved > 0:
                success_msg = f"Deal nailed! Saved R{saved:,.2f} today — you're building real wealth!"
            else:
                success_msg = "Transaction saved!"

            await page.show_snack(success_msg, bgcolor="#2e7d32", duration_ms=4000)

            amount.value = ""
            notes.value = ""
            date_picker.value = dt_date.today()
            tags_field.value = ""

            discount_type.value = "None"
            fixed_fields.controls[0].value = ""
            fixed_fields.controls[1].value = ""
            percent_fields.controls[0].value = ""
            percent_fields.controls[1].value = ""
            update_discount_fields()

            if refresh_all:
                await refresh_all()

            await page.safe_update()

        except (InvalidOperation, ValueError):
            await page.show_snack("Invalid number! Use digits and '.' only.", "red")
        except Exception as e:
            print(f"From Error: {e}")
            await page.show_snack("Something went wrong.", "red")

    update_discount_fields()

    return ft.Column(
        controls=[
            ft.Text("New Transaction", size=24, weight="bold"),
            date_row,
            date_picker,
            ft.Divider(height=12, color="transparent"),
            ft.Container(
                content=ft.Column([amount, amount_preview]),
                padding=12,
                border_radius=8,
                bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.PRIMARY),
            ),
            type_selector,
            category_dropdown,
            tags_field,
            notes,
            discount_container,
            ft.ElevatedButton(
                "Save Transaction",
                icon=ft.Icons.SAVE,
                bgcolor="#94d494",
                color="black",
                on_click=lambda _: page.run_task(submit),
            ),
        ],
        scroll="auto",
        spacing=12,
    )
