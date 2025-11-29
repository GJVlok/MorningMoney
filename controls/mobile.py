# controls/mobile.py
import flet as ft
from .common import money_text, daily_fire_container
from src.models import get_balance

def build_mobile_ui(page: ft.Page, new_entry_tab, diary_tab, investments_tab):
    balance_text = ft.Text(size=28, weight="bold", text_align="center")

    def update_balance():
        bal = get_balance()
        balance_text.value = f"R{bal:,.2f}"
        balance_text.color = "green" if bal >= 0 else "red"
        page.update()

    page.balance_updater = update_balance

    page.add(daily_fire_container())

    page.appbar = ft.AppBar(
        title=ft.Text("MorningMoney", size=24),
        center_title=True,
        bgcolor="#ff0066",
        actions=[ft.IconButton("Refresh", on_click=lambda _: update_balance())]
    )

    page.bottom_appbar = ft.BottomAppBar(
        bgcolor="#111122",
        content=ft.Row([
            ft.IconButton(ft.Icons.ADD, tooltip="New", on_click=lambda _: page.go("/new")),
            ft.IconButton(ft.Icons.RECEIPT_LONG, tooltip="Diary"),
            ft.IconButton(ft.Icons.TRENDING_UP, tooltip="Investments"),
        ], alignment="spaceAround")
    )

    # We'll use navigation rail or simple tabs — here using simple tabs for now
    tabs = ft.Tabs(...)  # same as desktop for simplicity, or use NavigationRail

    page.add(ft.Column([balance_text, tabs], expand=True))
    update_balance()