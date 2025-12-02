# controls/common.py
import flet as ft
import asyncio
from src.services.investments import get_total_projected_wealth
from src.services.transactions import get_balance
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
            page.update()

    async def show_snack(message: str, bgcolor: str = "green", duration_ms: int = 4000):
        page.snack_bar = ft.SnackBar(ft.Text(message, color="white"), bgcolor=bgcolor, open=True, duration=duration_ms)
        page.snack_bar.open = True
        page.update()
        # give event loop a tick
        await asyncio.sleep(0)

    page.safe_update = safe_update
    page.show_snack = show_snack

def is_currently_desktop(page: ft.Page) -> bool:
    force_desktop = page.session.get("force_desktop") or False
    force_mobile = page.session.get("force_mobile") or False
    if force_desktop:
        return True
    if force_mobile:
        return False
    return (
        page.platform in ("windows", "macos", "linux") or
        (getattr(page, "window", None) and getattr(page.window, "width", 0) > 800) or
        (getattr(page, "window", None) and getattr(page.window, "height", 0) > 900)
    )

def money_text(value, size=20, weight="bold"):
    try:
        value = float(value or 0)
        color = "green" if value >= 0 else "red"
        return ft.Text(f"R{value:,.2f}", size=size, weight=weight, color=color)
    except (TypeError, ValueError):
        return ft.Text("R0.00", color="orange", italic=True)

def daily_fire_container():
    return ft.Container(
        padding=20,
        bgcolor="#ff0066",
        border_radius=12,
        content=ft.Column([
            ft.Text("Daily Fire", size=18, weight="bold", color="white"),
            ft.Text(daily_message(get_balance(), get_total_projected_wealth()),
                    size=16, color="white", italic=True),
        ])
    )
