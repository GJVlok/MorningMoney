# ui/components/investment_form.py

import flet as ft
from datetime import date as dt_date
from decimal import Decimal, InvalidOperation

from src.services.core import svc_add_or_update_investment


def investment_form(page: ft.Page, refresh_all=None, existing_inv=None):
    is_edit = existing_inv is not None

    # ---------------- DECIMAL CLEAN ---------------- #

    def clean_decimal(val: str | None, default="0.00"):

        if not val or not val.strip():
            return Decimal(default)

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

    # ---------------- FIELDS ---------------- #

    name_field = ft.TextField(
        label="Investment Name",
        value=existing_inv.name if is_edit else "",
        autofocus=not is_edit,
        expand=True,
    )

    current_field = ft.TextField(
        label="Current Value",
        prefix=ft.Text("R"),
        value=f"{existing_inv.current_value:.2f}" if is_edit else "",
        expand=True,
    )

    monthly_field = ft.TextField(
        label="Monthly Contribution",
        prefix=ft.Text("R"),
        value=f"{existing_inv.monthly_contribution:.2f}" if is_edit else "0.00",
        expand=True,
    )

    rate_field = ft.TextField(
        label="Expected Annual Return %",
        value=f"{existing_inv.expected_annual_return:.2f}" if is_edit else "11.00",
        suffix=ft.Text("%", size=16, color=ft.Colors.GREY_700),
        expand=True,
    )

    year_field = ft.TextField(
        label="Target Year",
        value=str(existing_inv.target_year if is_edit else 2050),
        expand=True,
    )

    preview_text = ft.Text(
        "",
        size=13,
        color=ft.Colors.GREEN_300,
        italic=True,
        text_align=ft.TextAlign.CENTER,
    )

    # ---------------- PREVIEW ---------------- #

    def update_preview(e=None, do_update=True):

        try:
            curr = float(clean_decimal(current_field.value))
            monthly = float(clean_decimal(monthly_field.value))
            rate = float(clean_decimal(rate_field.value, "0")) / 100

            target_year = int(year_field.value or "2050")
            years = target_year - dt_date.today().year

            if years <= 0 or rate <= 0:
                preview_text.value = ""
                if do_update:
                    preview_text.update()
                return

            future = (
                curr * (1 + rate) ** years
                + monthly * (((1 + rate) ** years - 1) / rate)
            )

            preview_text.value = f"≈ R{future:,.0f} by {target_year}"
            preview_text.color = ft.Colors.GREEN_300

        except Exception:

            preview_text.value = "Check inputs"
            preview_text.color = ft.Colors.GREY_500
        if do_update:
            preview_text.update()

    for f in [current_field, monthly_field, rate_field, year_field]:
        f.on_change = lambda _: update_preview(_, do_update=True)

    # Initial set (no update)
    update_preview(None, do_update=False)

    # ---------------- SAVE ---------------- #

    async def save_investment(e=None):

        try:

            name_val = name_field.value.strip() or "Unnamed Investment"

            curr_val = clean_decimal(current_field.value)
            mon_val = clean_decimal(monthly_field.value)
            rate_val = clean_decimal(rate_field.value, "11.00")
            year_val = int(year_field.value.strip() or "2050")

            if rate_val <= 0:
                raise ValueError("Return must be positive")

            if year_val < dt_date.today().year + 1:
                raise ValueError("Target year must be future")

            svc_add_or_update_investment(
                name=name_val,
                current_value=curr_val,
                monthly=mon_val,
                return_rate=rate_val,
                target_year=year_val,
            )

            await page.show_snack(
                f"{'Updated' if is_edit else 'Added'} {name_val}",
                bgcolor="#94d494",
            )

            if not is_edit:

                name_field.value = ""
                current_field.value = ""
                monthly_field.value = "0.00"
                rate_field.value = "11.00"
                year_field.value = "2050"

                update_preview()

            page.update()

            if refresh_all:
                await refresh_all()

        except ValueError as ve:

            await page.show_snack(
                str(ve),
                bgcolor="orange",
            )

        except Exception as ex:

            await page.show_snack(
                f"Save failed: {str(ex)}",
                bgcolor="red",
            )

    # ---------------- UI ---------------- #

    return ft.Column(
        spacing=16,
        controls=[
            ft.Text(
                "Edit Investment" if is_edit else "Add Investment",
                size=22,
                weight=ft.FontWeight.BOLD,
            ),
            name_field,
            ft.Row([current_field, monthly_field]),
            ft.Row([rate_field, year_field]),
            preview_text,
            ft.ElevatedButton(
                content=ft.Text("Update Investment" if is_edit else "Save Investment"),
                icon=ft.Icons.SAVE,
                bgcolor="#94d494",
                color=ft.Colors.BLACK,
                expand=True,
                on_click=lambda e: page.run_task(save_investment),
            ),
        ],
    )
