# ui/components/new_entry_form.py
import flet as ft
from datetime import date as dt_date
from decimal import Decimal, InvalidOperation

from src.services.core import svc_add_transaction
from controls.common import money_text


def new_entry_form(page: ft.Page, refresh_all) -> ft.Control:
    today = dt_date.today()

    # ---------------- DATE PICKER ---------------- #

    date_display = ft.Text(
        value=today.strftime("%d %b %Y"),
        color=ft.Colors.PRIMARY,
        weight=ft.FontWeight.BOLD,
    )

    date_picker = ft.DatePicker(
        first_date=dt_date(today.year - 2, 1, 1),
        last_date=dt_date(today.year + 1, 12, 31),
        value=today,
    )

    def open_date_picker(e):
        page.open(date_picker)

    def on_date_changed(e):
        if date_picker.value:
            date_display.value = date_picker.value.strftime("%d %b %Y")
            page.shared_preferences.set(
                "last_used_date",
                date_picker.value.isoformat(),
            )
            page.update()

    date_picker.on_change = on_date_changed

    date_row = ft.Row(
            [
                ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CALENDAR_MONTH),
                            ft.Text("Choose Date"),
                        ],
                        spacing=8,
                    ),
                    on_click=open_date_picker,
                ),
                date_display,
            ],
            spacing=16,
        )

        # Load last date ASYNC
    async def load_last_date():
        last_date_str = await page.shared_preferences.get("last_used_date")
        if last_date_str:
            try:
                last_date = dt_date.fromisoformat(last_date_str)
                date_picker.value = last_date
                date_display.value = last_date.strftime("%d %b %Y")
                page.update()  # ensure UI refreshes
            except ValueError:
                pass  # invalid date string, ignore

    # Fire the async load immediately (non-blocking)
    page.run_task(load_last_date)

    # ---------------- TYPE ---------------- #

    def get_is_expense():
        return "expense" in type_selector.selected

    type_selector = ft.SegmentedButton(
        selected=["expense"],
        show_selected_icon=False,
        segments=[
            ft.Segment(value="income", label=ft.Text("Income")),
            ft.Segment(value="expense", label=ft.Text("Expense")),
        ],
    )

    # ---------------- CATEGORY ---------------- #

    INCOME_CATEGORIES = [
        "Salary", "Freelance", "Side Hustle",
        "Investment Return", "Gift", "Refund", "Other Income"
    ]

    EXPENSE_CATEGORIES = [
        "Groceries", "Meat", "Toiletries", "Clothes", "Transport",
        "Fuel", "Eating Out", "Entertainment", "Subscriptions",
        "Rent / Bond", "Electricity / Water", "Phone / Internet",
        "Medical", "Insurance", "Savings Transfer", "Debt Repayment",
        "Education", "Gifts Given", "Hobbies", "Travel",
        "Other Expense",
    ]

    category_dropdown = ft.Dropdown(expand=True)

    def update_category_dropdown():
        if get_is_expense():
            category_dropdown.options = [
                ft.dropdown.Option(c)
                for c in EXPENSE_CATEGORIES
            ]
            category_dropdown.value = EXPENSE_CATEGORIES[0]
            category_dropdown.border_color = ft.Colors.RED_400
        else:
            category_dropdown.options = [
                ft.dropdown.Option(c)
                for c in INCOME_CATEGORIES
            ]
            category_dropdown.value = INCOME_CATEGORIES[0]
            category_dropdown.border_color = ft.Colors.GREEN_400

        # page.update()

    type_selector.on_change = lambda e: (
        update_category_dropdown(),
        update_discount_fields(),
    )

    # ---------------- AMOUNT ---------------- #

    def clean_decimal(val: str | None) -> Decimal:

        if not val or not val.strip():
            return Decimal("0.00")

        clean = (
            val.replace("R", "")
            .replace("$", "")
            .replace(",", "")
            .strip()
        )

        try:
            return Decimal(clean)
        except InvalidOperation:
            raise ValueError("Invalid number")

    amount = ft.TextField(
        label="Amount",
        prefix=ft.Text("R"),
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
    )

    amount_preview = ft.Text(
        "",
        size=12,
        color=ft.Colors.GREY_400,
        italic=True,
    )

    def update_amount_preview(e=None):
        try:
            val = clean_decimal(amount.value)

            if val == 0:
                amount_preview.value = ""
            elif val < 0:
                amount_preview.value = (
                    f"Expense of {money_text(-val).value}"
                )
            else:
                amount_preview.value = (
                    f"Income of {money_text(val).value}"
                )

        except Exception:
            amount_preview.value = "Invalid amount"

        if e is not None:
            amount_preview.update()

    amount.on_change = update_amount_preview

    # ---------------- DISCOUNT ---------------- #

    discount_type = ft.Dropdown(
        label="Discount Type",
        value="none",
        options=[
            ft.dropdown.Option("none", "None"),
            ft.dropdown.Option("fixed", "Fixed Prices"),
            ft.dropdown.Option("percent", "Percentage"),
        ],
    )

    fixed_row = ft.Row(
        visible=False,
        controls=[
            ft.TextField(label="Original Price", prefix=ft.Text("R"), expand=True),
            ft.TextField(label="Paid Price", prefix=ft.Text("R"), expand=True),
        ],
    )

    percent_row = ft.Row(
        visible=False,
        controls=[
            ft.TextField(label="Original Price", prefix=ft.Text("R"), expand=True),
            ft.TextField(label="Discount %", expand=True),
        ],
    )

    saved_preview = ft.Text(
        "",
        size=14,
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
    )

    discount_container = ft.Container(
        visible=False,
        content=ft.Column(
            [
                ft.Text(
                    "Track Your Deal!",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.AMBER,
                ),
                discount_type,
                fixed_row,
                percent_row,
                saved_preview,
            ],
            spacing=12,
        ),
        padding=16,
        border=ft.border.all(1, ft.Colors.AMBER_200),
        border_radius=12,
    )

    def update_saved_preview(do_update=True):
        saved = Decimal("0.00")
        msg = ""
        color = ft.Colors.GREEN_300

        try:
            if not get_is_expense() or discount_type.value == "none":
                saved_preview.value = ""
                if do_update:
                    saved_preview.update()
                return

            if discount_type.value == "fixed":

                orig = clean_decimal(
                    fixed_row.controls[0].value
                )
                paid = clean_decimal(
                    fixed_row.controls[1].value
                )

                if orig <= paid:
                    msg = "Original must be > Paid"
                    color = ft.Colors.RED_400
                else:
                    saved = orig - paid
                    msg = f"Saved R{saved:,.2f}"

            elif discount_type.value == "percent":

                orig = clean_decimal(
                    percent_row.controls[0].value
                )

                perc = clean_decimal(
                    percent_row.controls[1].value or "0"
                )

                if perc < 0 or perc > 100:
                    msg = "Discount % must be 0-100"
                    color = ft.Colors.RED_400
                else:
                    saved = orig * (perc / Decimal("100"))
                    msg = f"Saved R{saved:,.2f} ({perc}%)"

        except Exception:
            msg = "Check numbers"
            color = ft.Colors.RED_400

        saved_preview.value = msg
        saved_preview.color = color
        if do_update:
            saved_preview.update()

    def update_discount_fields(e=None):
        is_exp = get_is_expense()

        discount_container.visible = is_exp
        discount_type.visible = is_exp

        fixed_row.visible = is_exp and discount_type.value == "fixed"
        percent_row.visible = is_exp and discount_type.value == "percent"

        update_saved_preview(do_update=(e is not None)) # pass False at init

        if e is not None:
            page.update()

    discount_type.on_change = update_discount_fields

    # ---------------- OTHER FIELDS ---------------- #

    tags = ft.TextField(label="Tags", expand=True)
    notes = ft.TextField(
        label="Notes",
        multiline=True,
        max_length=256,
        expand=True,
    )

    # ---------------- SUBMIT ---------------- #

    async def submit(e):
        try:
            amt_clean = clean_decimal(amount.value)

            if amt_clean == 0:
                await page.show_snack(
                    "Enter amount > 0",
                    bgcolor="orange",
                )
                return

            is_expense = get_is_expense()

            final_amt = (
                abs(amt_clean)
                if not is_expense
                else -abs(amt_clean)
            )

            saved_amt = Decimal("0.00")

            entry_date = date_picker.value or today

            svc_add_transaction(
                date=entry_date,
                category=category_dropdown.value,
                amount=final_amt,
                description=notes.value.strip(),
                tags=tags.value.strip(),
                saved_amount=saved_amt,
            )

            await page.show_snack(
                "Transaction saved!",
                bgcolor="#2e7d32",
            )

            amount.value = ""
            notes.value = ""
            tags.value = ""

            page.update()

            if refresh_all:
                await refresh_all()

        except Exception as ex:

            print("Submit error:", ex)

            await page.show_snack(
                "Something went wrong",
                bgcolor="red",
            )

    # Initial state
    update_category_dropdown()
    update_discount_fields()

    return ft.Column(
        [
            date_row,
            amount,
            amount_preview,
            type_selector,
            category_dropdown,
            tags,
            notes,
            discount_container,
            ft.ElevatedButton(
                content=ft.Text("Save Transaction"),
                on_click=lambda _: page.run_task(submit),
            ),
        ],
        spacing=12,
    )
