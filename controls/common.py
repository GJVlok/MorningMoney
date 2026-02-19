# controls/common.py
import flet as ft
import asyncio
from decimal import Decimal, InvalidOperation

from src.services.core import svc_get_balance, svc_get_total_projected_wealth
from src.motivation import daily_message

def init_page_extensions(page: ft.Page):
    """
    Attach standardized helpers to `page`:
      - page.show_snack(message, bgcolor)
      - page.safe_update() -> async wrapper around page.update()
    """
    page.snack_bar = None
    page.bottom_sheet = None
    page.balance_updater = getattr(page, "balance_updater", None)

    async def safe_update():
        try:
            page.update()
        except Exception:
            # give event loop a tick and retry
            await asyncio.sleep(0)
            try:
                page.update()
            except:
                pass

    async def show_snack(message: str, bgcolor: str = "green", duration_ms: int = 4000):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=bgcolor,
            duration=duration_ms
        )
        page.snack_bar.open = True
        page.update()
        # give event loop a tick
        await asyncio.sleep(0)

    page.safe_update = safe_update
    page.show_snack = show_snack

def money_text(value, size=20, weight="bold", color: str | None=None):
    """
    Standardized currency display.
    Ensures any input (float, int, str, None) is treated as a Decimal.
    """
    try:
        # Convert to string first to avoid float 'noise'
        clean_value = Decimal(str(value or '0.00'))

        # Color coding: Green for positive/zero, Red for negative
        if color is None:
            color = "#07ff07" if clean_value >= 0 else "#ff4444"

        # Formatting: R1,234.56
        # :,.2f works perfectly with Decimals for commas and 2 decimal places
        formatted_value = f"R{clean_value:,.2f}"

        return ft.Text(formatted_value, size=size, weight=weight, color=color)
    
    except (TypeError, ValueError, InvalidOperation):
        return ft.Text("R0.00", size=size, color="orange", italic=True)