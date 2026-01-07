# ui/components/investment_form.py
import flet as ft
from src.services.core import svc_add_or_update_investment


def investment_form(page: ft.Page, refresh_all=None) -> ft.Column:
    name = ft.TextField(
        label="Fund Name (e.g. RA - Discovery)",
        expand=True,
    )

    current = ft.TextField(
        label="Current Value",
        keyboard_type="number",
        expand=True,
    )

    monthly = ft.TextField(
        label="Monthly Contribution",
        keyboard_type="number",
        value="0",
        expand=True,
    )

    rate = ft.TextField(
        label="Expected Return %",
        keyboard_type="number",
        value="11",
        expand=True,
    )

    year = ft.TextField(
        label="Target Year",
        keyboard_type="number",
        value="2050",
        expand=True,
    )

    async def on_save(e):
        try:
            svc_add_or_update_investment(
                name=name.value or "Unnamed",
                current_value=float(current.value or 0),
                monthly=float(monthly.value or 0),
                return_rate=float(rate.value or 11),
                target_year=int(year.value or 2050),
            )
            await page.show_snack("Investment saved!", "green")

            if refresh_all:
                await refresh_all()

        except ValueError:
            await page.show_snack("Invalid input", "red")

    return ft.Column(
        controls=[
            ft.Divider(height=30, color="transparent"),
            ft.Text("Add / Update Investment", size=20, weight="bold"),
            name,
            current,
            monthly,
            rate,
            year,
            ft.ElevatedButton(
                "Save Investment",
                on_click=lambda e: page.run_task(on_save, e),
            ),
        ]
    )
