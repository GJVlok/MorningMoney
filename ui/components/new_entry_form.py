# ui/components/new_entry_form.py
import flet as ft
from datetime import date as dt_date, datetime, timezone
from decimal import Decimal, InvalidOperation
import asyncio

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
        confirm_text="Select",
        cancel_text="Cancel",
    )
    page.overlay.append(date_picker)

    async def set_date_to(date_obj: dt_date, do_update=True):
        utc_midnight = datetime(
            date_obj.year,
            date_obj.month,
            date_obj.day,
            tzinfo=timezone.utc,
        )

        date_picker.value = utc_midnight
        date_display.value = date_obj.strftime("%d %b %Y")

        await page.shared_preferences.set(
            "last_used_date",
            date_obj.isoformat(),
        )

        if do_update and date_display.page is not None:
            date_display.update()

    async def on_date_changed(do_update=True):
        if not date_picker.value:
            return
        utc_dt = date_picker.value
        local_offset = datetime.now(timezone.utc).astimezone().utcoffset()
        corrected_date = (utc_dt + local_offset).date()
        await set_date_to(corrected_date, do_update=do_update)

    def open_date_picker(e=None):
        page.show_dialog(date_picker)

    date_picker.on_change = lambda e: page.run_task(on_date_changed, do_update=True)

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

    async def load_last_date():
        last_date_str = await page.shared_preferences.get("last_used_date")
        if last_date_str:
            try:
                last_date = dt_date.fromisoformat(last_date_str)
            except ValueError:
                last_date = today
        else:
            last_date = today

        # Only set value, do NOT call update here
        date_picker.value = datetime(
            last_date.year,
            last_date.month,
            last_date.day,
            tzinfo=timezone.utc
        )
        date_display.value = last_date.strftime("%d %b %Y")

    # ---------------- TYPE ---------------- #

    type_selector = ft.SegmentedButton(
        segments=[
            ft.Segment(value="income", label=ft.Text("Income")),
            ft.Segment(value="expense", label=ft.Text("Expense")),
        ],
        selected=["expense"],
        allow_multiple_selection=False,
        allow_empty_selection=False,
        show_selected_icon=False,
    )

    def get_is_expense():
        return "expense" in type_selector.selected

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

    def update_category_dropdown(do_update=True):
        if get_is_expense():
            category_dropdown.options = [ft.dropdown.Option(c) for c in EXPENSE_CATEGORIES]
            category_dropdown.value = EXPENSE_CATEGORIES[0]
            category_dropdown.border_color = ft.Colors.RED_400
        else:
            category_dropdown.options = [ft.dropdown.Option(c) for c in INCOME_CATEGORIES]
            category_dropdown.value = INCOME_CATEGORIES[0]
            category_dropdown.border_color = ft.Colors.GREEN_400
        if do_update and category_dropdown.page is not None:
            category_dropdown.update()

    type_selector.on_change = lambda e: (
        update_category_dropdown(),
        update_discount_fields(),
    )

    # ---------------- AMOUNT ---------------- #

    def clean_decimal(val: str | None) -> Decimal:
        if not val or not val.strip():
            return Decimal("0.00")
        clean = val.replace("R", "").replace("$", "").replace(",", "").strip()
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
                amount_preview.value = f"Expense of {money_text(-val).value}"
            else:
                amount_preview.value = f"Income of {money_text(val).value}"
        except Exception:
            amount_preview.value = "Invalid amount"
        if e is not None and amount_preview.page is not None:
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
        # visible=False,
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
        try:
            if not get_is_expense() or discount_type.value == "none":
                saved_preview.value = ""
                saved_preview.color = ft.Colors.GREY_400
                if do_update and saved_preview.page is not None:
                    saved_preview.update()
                return

            if discount_type.value == "fixed":
                orig = clean_decimal(fixed_row.controls[0].value)
                paid = clean_decimal(fixed_row.controls[1].value)
                if orig <= paid:
                    saved_preview.value = "Original must be > Paid"
                    saved_preview.color = ft.Colors.RED_400
                else:
                    saved_amt = orig - paid
                    saved_preview.value = f"Saved R{saved_amt:,.2f}"
                    saved_preview.color = ft.Colors.GREEN_300

            elif discount_type.value == "percent":
                orig = clean_decimal(percent_row.controls[0].value)
                perc = clean_decimal(percent_row.controls[1].value or "0")
                if perc < 0 or perc > 100:
                    saved_preview.value = "Discount % must be 0-100"
                    saved_preview.color = ft.Colors.RED_400
                else:
                    saved_amt = orig * (perc / Decimal("100"))
                    saved_preview.value = f"Saved R{saved_amt:,.2f} ({perc}%)"
                    saved_preview.color = ft.Colors.GREEN_300

            if do_update and saved_preview.page is not None:
                saved_preview.update()

        except Exception:
            saved_preview.value = "Check numbers"
            saved_preview.color = ft.Colors.RED_400
            if do_update and saved_preview.page is not None:
                saved_preview.update()

    def update_discount_fields(e=None):
        # No more visibility changes here — always show the container
        fixed_row.visible = discount_type.value == "fixed"
        percent_row.visible = discount_type.value == "percent"
        update_saved_preview(do_update=False)

        # Still update children (safe even if redundant)
        for ctrl in (fixed_row, percent_row):
            if ctrl.page is not None:
                ctrl.update()
        # Optional: discount_container.update() if you ever hide it again

        # ← THIS IS THE FIX: explicitly update every control whose visibility changed
        for ctrl in (discount_container, discount_type, fixed_row, percent_row):
            if ctrl.page is not None:
                ctrl.update()

    # Hook input changes
    for tf in fixed_row.controls + percent_row.controls:
        tf.on_change = lambda e: update_saved_preview()

    discount_type.on_change = lambda e: update_discount_fields()

    # ---------------- OTHER FIELDS ---------------- #

    tags = ft.TextField(label="Tags", expand=True)
    notes = ft.TextField(label="Notes", multiline=True, max_length=256, expand=True)

    # ---------------- SUBMIT ---------------- #

    async def submit(e=None):
        try:
            amt_clean = clean_decimal(amount.value)
            if amt_clean == 0:
                await page.show_snack("Enter amount > 0", bgcolor="orange")
                return

            is_expense = get_is_expense()
            final_amt = abs(amt_clean) if not is_expense else -abs(amt_clean)

            entry_value = date_picker.value
            if isinstance(entry_value, datetime):
                entry_date = entry_value.date()
            elif isinstance(entry_value, dt_date):
                entry_date = entry_value
            else:
                entry_date = dt_date.today()

            saved_amount = Decimal("0.00")
            if is_expense and discount_type.value != "none":
                try:
                    if discount_type.value == "fixed":
                        orig = clean_decimal(fixed_row.controls[0].value)
                        paid = clean_decimal(fixed_row.controls[1].value)
                        if orig > paid:
                            saved_amount = orig - paid
                    elif discount_type.value == "percent":
                        orig = clean_decimal(percent_row.controls[0].value)
                        perc = clean_decimal(percent_row.controls[1].value or "0")
                        if 0 <= perc <= 100:
                            saved_amount = orig * (perc / Decimal("100"))
                except Exception:
                    saved_amount = Decimal("0.00")

            await asyncio.to_thread(
                svc_add_transaction,
                date=entry_date,
                category=category_dropdown.value,
                amount=final_amt,
                description=notes.value.strip(),
                tags=tags.value.strip(),
                saved_amount=saved_amount,
            )

            await page.show_snack("Transaction saved!", bgcolor="#2e7d32")
            amount.value = ""
            notes.value = ""
            tags.value = ""
            await set_date_to(dt_date.today(), do_update=True)
            if refresh_all:
                await refresh_all()
            page.update()

        except Exception as ex:
            print("Submit error:", ex)
            await page.show_snack("Something went wrong", bgcolor="red")

    # ---------------- MAIN COLUMN ---------------- #

    col = ft.Column(
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
                on_click=lambda e: page.run_task(submit),
            ),
        ],
        spacing=12,
    )

    def on_mount():
        page.run_task(load_last_date)
        update_category_dropdown()
        update_discount_fields()
        update_amount_preview()

    col.did_mount = on_mount

    return col