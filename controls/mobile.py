# controls/mobile.py
import flet as ft
from src.models import get_balance
from .common import money_text, daily_fire_container


def build_mobile_ui(page: ft.Page, new_entry_tab, diary_tab, investments_tab):
    # Balance at top
    balance_text = ft.Text(size=36, weight="bold", text_align="center")

    def update_balance():
        bal = get_balance()
        balance_text.value = f"R{bal:,.2f}"
        balance_text.color = "green" if bal >= 0 else "red"
        page.update()

    page.balance_updater = update_balance

    # Bottom navigation
    bottom_nav = ft.BottomAppBar(
        bgcolor="#111122",
        height=70,
        content=ft.Row([
            ft.IconButton(ft.Icons.ADD, tooltip="New", on_click=lambda _: page.go("/new")),
            ft.IconButton(ft.Icons.RECEIPT_LONG, tooltip="Diary", on_click=lambda _: page.go("/diary")),
            ft.IconButton(ft.Icons.TRENDING_UP, tooltip="Investments", on_click=lambda _: page.go("/investments")),
        ], alignment="spaceAround")
    )

    # NavigationRail for side menu (optional — looks great on tablets)
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        bgcolor="#1e1e2e",
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.ADD, selected_icon=ft.Icons.ADD_CIRCLE, label="New"),
            ft.NavigationRailDestination(icon=ft.Icons.RECEIPT_LONG, selected_icon=ft.Icons.RECEIPT, label="Diary"),
            ft.NavigationRailDestination(icon=ft.Icons.TRENDING_UP, selected_icon=ft.Icons.SSID_CHART, label="Investments"),
        ],
        on_change=lambda e: page.go(["/new", "/diary", "/investments"][e.control.selected_index]),
    )

    page.add(
        ft.Column([
            daily_fire_container(),
            ft.Container(balance_text, padding=20),
            ft.Row([
                rail,
                ft.VerticalDivider(width=1),
                ft.Container(
                    ft.Stack([
                        new_entry_tab if page.route == "/new" else ft.Container(),
                        diary_tab if page.route == "/diary" else ft.Container(),
                        investments_tab if page.route == "/investments" else ft.Container(),
                    ], expand=True),
                    expand=True,
                )
            ], expand=True),
        ], expand=True)
    )

    page.bottom_appbar = bottom_nav
    update_balance()