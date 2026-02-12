import flet as ft
from decimal import Decimal, InvalidOperation
from src.services.core import svc_add_or_update_investment

def investment_form(page: ft.Page, refresh_all=None) -> ft.Column:
    
    # Re-using the same cleanup logic for consistency
    def get_clean_decimal(val: str, default: str = "0.00") -> Decimal:
        if not val or not val.strip():
            return Decimal(default)
        # Strip R, $, and commas
        clean = val.replace("R", "").replace("$", "").replace(",", "").strip()
        try:
            return Decimal(clean)
        except InvalidOperation:
            raise ValueError("Invalid number format")

    name = ft.TextField(
        label="Fund Name (e.g. RA - Discovery)",
        expand=True,
    )

    current = ft.TextField(
        label="Current Value",
        keyboard_type=ft.KeyboardType.NUMBER,
        hint_text="0.00",
        expand=True,
    )

    monthly = ft.TextField(
        label="Monthly Contribution",
        keyboard_type=ft.KeyboardType.NUMBER,
        value="0",
        expand=True,
    )

    rate = ft.TextField(
        label="Expected Return %",
        keyboard_type=ft.KeyboardType.NUMBER,
        value="11",
        expand=True,
    )

    year = ft.TextField(
        label="Target Year",
        keyboard_type=ft.KeyboardType.NUMBER,
        value="2050",
        expand=True,
    )

    async def on_save(e):
        try:
            # 1. Convert everything safely
            c_val = get_clean_decimal(current.value)
            m_val = get_clean_decimal(monthly.value)
            r_val = get_clean_decimal(rate.value, default="11.00")
            t_year = int(year.value or 2050)

            # 2. Pass to service
            svc_add_or_update_investment(
                name=name.value or "Unnamed",
                current_value=c_val,
                monthly=m_val,
                return_rate=r_val,
                target_year=t_year,
            )
            
            # 3. Success UI
            await page.show_snack(f"Saved {name.value or 'Investment'}!", "green")

            # 4. Clear fields (optional, but good for adding multiple)
            name.value = ""
            current.value = ""
            
            if refresh_all:
                await refresh_all()
            
            page.update()

        except (ValueError, InvalidOperation):
            await page.show_snack("Please enter valid numbers", "red")
        except Exception as ex:
            await page.show_snack(f"Error: {str(ex)}", "red")

    return ft.Column(
        controls=[
            ft.Divider(height=10, color="transparent"),
            ft.Text("Add / Update Investment", size=20, weight="bold"),
            name,
            ft.Row([current, monthly], spacing=10), # Grouping for better UI
            ft.Row([rate, year], spacing=10),
            ft.ElevatedButton(
                "Save Investment",
                icon=ft.Icons.SAVE,
                bgcolor="#94d494",
                color="black",
                on_click=lambda e: page.run_task(on_save, e),
            ),
        ],
        spacing=15
    )