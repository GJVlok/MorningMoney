# ui/components/investment_form.py
import flet as ft
from datetime import date as dt_date
from decimal import Decimal, InvalidOperation
from src.services.core import svc_add_or_update_investment


def investment_form(page: ft.Page, refresh_all=None, existing_inv=None) -> ft.Column:
    """
    Reusable form for adding OR editing investments.
    - existing_inv: if provided, pre-fills fields for edit mode.
    """
    is_edit = existing_inv is not None

    def clean_decimal(val: str | None, default: str = "0.00") -> Decimal:
        if not val or not val.strip():
            return Decimal(default)
        clean = val.replace("R", "").replace("$", "").replace(",", "").strip()
        try:
            return Decimal(clean)
        except InvalidOperation:
            raise ValueError("Invalid number format")

    # ── Fields ───────────────────────────────────────────────────
    name_field = ft.TextField(
        label="Investment Name (e.g. RA Discovery, Satrix MSCI World)",
        value=existing_inv.name if is_edit else "",
        autofocus=not is_edit,  # focus on name when adding new
        expand=True,
    )

    current_field = ft.TextField(
        label="Current Value",
        prefix_text="R ",
        value=f"{existing_inv.current_value:.2f}" if is_edit else "",
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d{0,2}$"),
        expand=True,
    )

    monthly_field = ft.TextField(
        label="Monthly Contribution",
        prefix_text="R ",
        value=f"{existing_inv.monthly_contribution:.2f}" if is_edit else "0.00",
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d{0,2}$"),
        expand=True,
    )

    rate_field = ft.TextField(
        label="Expected Annual Return",
        suffix_text="%",
        value=f"{existing_inv.expected_annual_return:.2f}" if is_edit else "11.00",
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d{0,2}$"),
        expand=True,
    )

    year_field = ft.TextField(
        label="Target / FIRE Year",
        value=str(existing_inv.target_year if is_edit else 2050),
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^\d{0,4}$"),
        expand=True,
    )

    # Simple projected preview (teaches compound interest!)
    preview_text = ft.Text(
        "... calculating ...",
        size=13,
        color=ft.Colors.GREEN_300,
        italic=True,
        text_align=ft.TextAlign.CENTER,
    )

    def update_preview(e=None):
        try:
            curr = clean_decimal(current_field.value)
            monthly = clean_decimal(monthly_field.value)
            rate = clean_decimal(rate_field.value, "0") / Decimal("100")  # % → decimal
            years = int(year_field.value or "2050") - dt_date.today().year

            if years <= 0 or rate <= 0:
                preview_text.value = ""
                return

            # Simple compound interest approximation
            future = curr * (1 + rate) ** years + monthly * (((1 + rate) ** years - 1) / rate)
            preview_text.value = f"≈ R{future:,.0f} by {year_field.value}"
            preview_text.color = ft.Colors.GREEN_300
        except:
            preview_text.value = "Check inputs for preview"
            preview_text.color = ft.Colors.GREY_500
        page.update()

    # Wire live preview
    for field in [current_field, monthly_field, rate_field, year_field]:
        field.on_change = update_preview

    # Initial preview
    update_preview()

    # ── Save Logic ───────────────────────────────────────────────
    async def save_investment(e):
        try:
            name_val = name_field.value.strip() or "Unnamed Investment"
            curr_val = clean_decimal(current_field.value)
            mon_val = clean_decimal(monthly_field.value)
            rate_val = clean_decimal(rate_field.value, "11.00")
            year_val = int(year_field.value.strip() or "2050")

            if rate_val <= 0:
                raise ValueError("Return rate should be positive")
            if year_val < dt_date.today().year + 1:
                raise ValueError("Target year must be in the future")

            svc_add_or_update_investment(
                name=name_val,
                current_value=curr_val,
                monthly=mon_val,
                return_rate=rate_val,
                target_year=year_val,
                # notes=... (add field later if wanted)
            )

            await page.show_snack(
                f"{'Updated' if is_edit else 'Added'} {name_val} — on track for FIRE!",
                bgcolor="#94d494"
            )

            if not is_edit:
                # Clear for next entry (add mode)
                name_field.value = ""
                current_field.value = ""
                monthly_field.value = "0.00"
                rate_field.value = "11.00"
                year_field.value = "2050"
                update_preview()

            if refresh_all:
                await refresh_all()

            page.update()

        except ValueError as ve:
            await page.show_snack(f"Oops: {str(ve)}", bgcolor="orange")
        except Exception as ex:
            await page.show_snack(f"Save failed: {str(ex)}", bgcolor="red")

    # ── Build UI ─────────────────────────────────────────────────
    return ft.Column(
        spacing=16,
        controls=[
            ft.Text(
                "Edit Investment" if is_edit else "Add New Investment",
                size=22,
                weight=ft.FontWeight.BOLD,
            ),
            name_field,
            ft.Row([current_field, monthly_field], spacing=12),
            ft.Row([rate_field, year_field], spacing=12),
            preview_text,
            ft.ElevatedButton(
                "Update Investment" if is_edit else "Save Investment",
                icon=ft.Icons.SAVE,
                bgcolor="#94d494",
                color=ft.Colors.BLACK,
                expand=True,
                on_click=lambda e: page.run_task(save_investment, e),
            ),
        ],
    )