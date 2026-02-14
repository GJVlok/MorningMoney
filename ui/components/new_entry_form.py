# ui/components/new_entry_form.py
import flet as ft
from datetime import date as dt_date
from decimal import Decimal, InvalidOperation
from src.services.core import svc_add_transaction
from controls.common import money_text


def new_entry_form(page: ft.Page, refresh_all) -> ft.Control:
    today = dt_date.today()

    # ── Date Picker Setup ────────────────────────────────────────
    date_display = ft.Text(
        value=today.strftime("%d %b %Y"),
        color=ft.colors.PRIMARY,
        weight=ft.FontWeight.BOLD,
    )

    date_picker = ft.DatePicker(
        first_date=dt_date(today.year - 2, 1, 1),
        last_date=dt_date(today.year + 1, 12, 31),
        value=today,
    )

    def open_date_picker(e):
        # Modern way — use show_dialog (cleaner, no overlay management)
        page.show_dialog(date_picker)

    def on_date_changed(e):
        if date_picker.value:
            date_display.value = date_picker.value.strftime("%d %b %Y")
            # Persist last used date (ISO format is safest)
            page.client_storage.set("last_used_date", date_picker.value.isoformat())
            page.update()

    date_picker.on_change = on_date_changed

    # Try to load last used date
    last_date_str = page.client_storage.get("last_used_date")
    if last_date_str:
        try:
            last_date = dt_date.fromisoformat(last_date_str)
            date_picker.value = last_date
            date_display.value = last_date.strftime("%d %b %Y")
        except ValueError:
            pass  # invalid → keep today

    date_row = ft.Row(
        [
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.icons.CALENDAR_MONTH), ft.Text("Choose Date")], spacing=8),
                on_click=open_date_picker,
            ),
            date_display,
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=16,
    )

    # ── Type & Category ──────────────────────────────────────────
    def get_is_expense():
        return type_selector.selected and "expense" in type_selector.selected

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
        options=[ft.dropdown.Option(c) for c in EXPENSE_CATEGORIES],
        value=EXPENSE_CATEGORIES[0],
        expand=True,
    )

    def update_category_dropdown():
        if get_is_expense():
            category_dropdown.options = [ft.dropdown.Option(c) for c in EXPENSE_CATEGORIES]
            category_dropdown.value = EXPENSE_CATEGORIES[0]
            category_dropdown.border_color = ft.colors.RED_400
        else:
            category_dropdown.options = [ft.dropdown.Option(c) for c in INCOME_CATEGORIES]
            category_dropdown.value = INCOME_CATEGORIES[0]
            category_dropdown.border_color = ft.colors.GREEN_400
        page.update()

    type_selector = ft.SegmentedButton(
        selected=["expense"],
        show_selected_icon=False,
        segments=[
            ft.Segment(value="income", label=ft.Text("Income")),
            ft.Segment(value="expense", label=ft.Text("Expense")),
        ],
        on_change=lambda e: (update_category_dropdown(), update_discount_fields()),
    )

    # ── Amount & Preview ─────────────────────────────────────────
    def clean_decimal(val: str | None) -> Decimal:
        if not val or not val.strip():
            return Decimal("0.00")
        clean = val.replace("R", "").replace("$", "").replace(",", "").strip()
        try:
            return Decimal(clean)
        except InvalidOperation:
            raise ValueError("Invalid number format")

    amount = ft.TextField(
        label="Amount",
        prefix_text="R ",
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d{0,2}$"),
        expand=True,
    )

    amount_preview = ft.Text("", size=12, color=ft.colors.GREY_400, italic=True)

    def update_amount_preview(e=None):
        try:
            val = clean_decimal(amount.value)
            if val == 0:
                amount_preview.value = ""
            elif val < 0:
                amount_preview.value = f"Expense of {money_text(-val).value}"
            else:
                amount_preview.value = f"Income of {money_text(val).value}"
        except:
            amount_preview.value = "Invalid amount"
        page.update()

    amount.on_change = update_amount_preview

    # ── Discount / Savings Tracking ──────────────────────────────
    discount_type = ft.Dropdown(
        label="Discount Type",
        value="none",
        options=[
            ft.dropdown.Option("none", "None"),
            ft.dropdown.Option("fixed", "Fixed Prices"),
            ft.dropdown.Option("percent", "Percentage"),
        ],
    )

    fixed_row = ft.Row(visible=False, controls=[
        ft.TextField(label="Original Price", prefix_text="R ", keyboard_type=ft.KeyboardType.NUMBER, expand=True),
        ft.TextField(label="Paid Price", prefix_text="R ", keyboard_type=ft.KeyboardType.NUMBER, expand=True),
    ])

    percent_row = ft.Row(visible=False, controls=[
        ft.TextField(label="Original Price", prefix_text="R ", keyboard_type=ft.KeyboardType.NUMBER, expand=True),
        ft.TextField(label="Discount %", keyboard_type=ft.KeyboardType.NUMBER, expand=True),
    ])

    saved_preview = ft.Text("", size=14, weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER)

    discount_container = ft.Container(
        visible=False,
        content=ft.Column([
            ft.Text("Track Your Deal!", size=16, weight="bold", color=ft.colors.AMBER),
            discount_type,
            fixed_row,
            percent_row,
            saved_preview,
        ], spacing=12),
        padding=16,
        border=ft.border.all(1, ft.colors.AMBER_200),
        border_radius=12,
        bgcolor=ft.colors.with_opacity(0.08, ft.colors.AMBER),
    )

    def update_discount_fields(e=None):
        is_exp = get_is_expense()
        discount_container.visible = is_exp
        discount_type.visible = is_exp

        fixed_row.visible = is_exp and discount_type.value == "fixed"
        percent_row.visible = is_exp and discount_type.value == "percent"

        # Re-attach preview update
        for fld in [*fixed_row.controls, *percent_row.controls]:
            fld.on_change = lambda _: update_saved_preview()

        update_saved_preview()
        page.update()

    def update_saved_preview():
        saved = Decimal("0.00")
        msg = ""
        color = ft.colors.GREEN_300

        try:
            if not get_is_expense() or discount_type.value == "none":
                saved_preview.value = ""
                return

            if discount_type.value == "fixed":
                orig = clean_decimal(fixed_row.controls[0].value)
                paid = clean_decimal(fixed_row.controls[1].value)
                if orig <= paid:
                    msg = "Original must be > Paid"
                    color = ft.colors.RED_400
                else:
                    saved = orig - paid
                    msg = f"Saved R{saved:,.2f} — nice one!"

            elif discount_type.value == "percent":
                orig = clean_decimal(percent_row.controls[0].value)
                perc_str = percent_row.controls[1].value.strip()
                perc = clean_decimal(perc_str) if perc_str else Decimal("0")
                if perc < 0 or perc > 100:
                    msg = "Discount % must be 0–100"
                    color = ft.colors.RED_400
                else:
                    saved = orig * (perc / Decimal("100"))
                    msg = f"Saved R{saved:,.2f} ({perc}%) — smart!"

        except Exception:
            msg = "Check numbers"
            color = ft.colors.RED_400

        saved_preview.value = msg
        saved_preview.color = color
        page.update()

    discount_type.on_change = update_discount_fields

    # ── Other Fields ─────────────────────────────────────────────
    tags = ft.TextField(label="Tags (comma separated)", expand=True)
    notes = ft.TextField(label="Notes (optional)", multiline=True, max_length=256, expand=True)

    # ── Submit ───────────────────────────────────────────────────
    async def submit(e):
        try:
            amt_clean = clean_decimal(amount.value)
            if amt_clean == 0:
                await page.show_snack("Enter amount > 0", bgcolor="orange")
                return

            is_expense = get_is_expense()
            final_amt = abs(amt_clean) if not is_expense else -abs(amt_clean)
            saved_amt = Decimal("0.00")

            if is_expense and discount_type.value != "none":
                if discount_type.value == "fixed":
                    orig = clean_decimal(fixed_row.controls[0].value)
                    paid = clean_decimal(fixed_row.controls[1].value)
                    if orig <= paid or orig <= 0:
                        raise ValueError("Invalid fixed prices")
                    saved_amt = orig - paid
                    final_amt = -paid
                else:  # percent
                    orig = clean_decimal(percent_row.controls[0].value)
                    perc = clean_decimal(percent_row.controls[1].value or "0")
                    if perc < 0 or perc > 100 or orig <= 0:
                        raise ValueError("Invalid percentage discount")
                    saved_amt = orig * (perc / Decimal("100"))
                    final_amt = -(orig - saved_amt)

            entry_date = date_picker.value or today

            svc_add_transaction(
                date=entry_date,
                category=category_dropdown.value or "Uncategorized",
                amount=final_amt,
                description=notes.value.strip() or "",
                tags=tags.value.strip(),
                saved_amount=saved_amt,
            )

            msg = f"Deal nailed! Saved R{saved_amt:,.2f} — wealth building!" if saved_amt > 0 else "Transaction saved!"
            await page.show_snack(msg, bgcolor="#2e7d32", duration=4000)

            # Reset form
            amount.value = ""
            notes.value = ""
            tags.value = ""
            discount_type.value = "none"
            fixed_row.controls[0].value = ""
            fixed_row.controls[1].value = ""
            percent_row.controls[0].value = ""
            percent_row.controls[1].value = ""
            update_discount_fields()
            update_amount_preview()

            if refresh_all:
                await refresh_all()

        except ValueError as ve:
            await page.show_snack(str(ve), bgcolor="red")
        except Exception as ex:
            print(f"Submit error: {ex}")
            await page.show_snack("Something went wrong — check inputs", bgcolor="red")

    update_category_dropdown()   # Initial state
    update_discount_fields()     # Initial visibility

    return ft.Column([
        ft.Text("New Transaction", size=24, weight="bold"),
        date_row,
        ft.Divider(height=12, color="transparent"),
        ft.Container(
            content=ft.Column([amount, amount_preview]),
            padding=12,
            border_radius=8,
            bgcolor=ft.colors.with_opacity(0.04, ft.colors.PRIMARY),
        ),
        type_selector,
        category_dropdown,
        tags,
        notes,
        discount_container,
        ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.icons.SAVE), ft.Text("Save Transaction")], spacing=8),
            bgcolor="#94d494",
            color="black",
            on_click=lambda _: page.run_task(submit),
        ),
    ])