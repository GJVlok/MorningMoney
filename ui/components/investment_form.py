# ui/components/investment_form.py
import flet as ft
import asyncio

from src.models import add_or_update_investment


def investment_form(page: ft.Page, refresh_all) -> ft.Column:
    """Add/Edit Investment form – used by InvestmentsTab"""
    name = ft.TextField(label="Fund Name (e.g. RA – Discovery)", expand=True)
    current = ft.TextField(label="Current Value", keyboard_type="number", expand=True)
    monthly = ft.TextField(label="Monthly Contribution", value="0", expand=True)
    rate = ft.TextField(label="Expected Return %", value="11", expand=True)
    year = ft.TextField(label="Target Year", value="2050", expand=True)

    async def save(e):
        try:
            add_or_update_investment(
                name=name.value or "Unnamed",
                current_value=float(current.value or 0),
                monthly=float(monthly.value or 0),
                return_rate=float(rate.value or 11),
                target_year=int(year.value or 2050),
            )
            page.show_snack("Investment saved!", bgcolor="green")
            await refresh_all()
        except ValueError:
            page.show_snack("Invalid input", bgcolor="red")

    return ft.Column([
        ft.Divider(height=30, color="transparent"),
        ft.Text("Add / Update Investment", weight="bold", size=20),
        name, current, monthly, rate, year,
        ft.ElevatedButton("Save Investment", on_click=save),
    ])