# controls/common.py
import flet as ft
import asyncio
import os
from src.models import get_balance, get_total_projected_wealth
from src.motivation import daily_message

# +++++++++ Added Stable Page Helpers +++++++++++++ #

def init_page_extensions(page: ft.Page):
    """
    Ensure the Page object always has the attributes dialogs/tokens expect.
    Call once, early in main() before building any UI or calling tabs/dialogs.
    """
    # initialize expected attributes
    page.snack_bar = None
    page.bottom_sheet = None
    page.balance_updater = getattr(page, "balance_updater", None)

    # convenience helper: uniform snack usage across modules
    def show_snack(message: str, bgcolor: str = "green", duration_ms: int = 4000):
        page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=bgcolor, open=True)
        # Flet SnackBar has an 'open' property; use page.update() to show
        page.update()

    # attach helper
    page.show_snack = show_snack

# ++++++++++++++++++++++++++++++++++++++++++++++++++ #

def money_text(value: float, size=20, weight="bold"):
    color = "green" if value >= 0 else "red"
    return ft.Text(f"R{value:,.2f}", size=size, weight=weight, color=color)

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

async def splash(page: ft.Page):
    logo = ft.Image(src="assets/logo.png", width=200, opacity=0.0) \
        if os.path.exists("assets/logo.png") else ft.Text("Money", size=120, opacity=0.0)
    splash_text = ft.Text("MorningMoney", size=32, weight="bold", opacity=0.0)
    loading_text = ft.Text("Loading your wealth engine...", opacity=0.0)

    page.add(ft.Column([logo, splash_text, loading_text],
                      alignment="center", horizontal_alignment="center", spacing=20))
    page.update()

    for i in range(11):
        opacity = i / 10
        logo.opacity = splash_text.opacity = loading_text.opacity = opacity
        page.update()
        await asyncio.sleep(0.04)

    for i in reversed(range(11)):
        opacity = i / 10
        logo.opacity = splash_text.opacity = loading_text.opacity = opacity
        page.update()
        await asyncio.sleep(0.03)

    page.clean()