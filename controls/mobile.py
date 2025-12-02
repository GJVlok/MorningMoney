# controls/mobile.py
import flet as ft
from src.services.transactions import get_balance
from controls.common import money_text, daily_fire_container

def build_mobile_ui(page: ft.Page, new_entry_tab, diary_tab, investments_tab, settings_tab):
    balance_text = ft.Text(size=36, weight="bold", text_align="center")

    def update_balance():
        bal = get_balance()
        balance_text.value = f"R{bal:,.2f}"
        balance_text.color = "green" if bal >= 0 else "red"
        page.update()

    page.balance_updater = update_balance

    bottom_nav = ft.BottomAppBar(
        bgcolor="#111122",
        height=70,
        content=ft.Row([
            ft.IconButton(ft.Icons.ADD, tooltip="New", on_click=lambda _: page.go("/new")),
            ft.IconButton(ft.Icons.RECEIPT_LONG, tooltip="Diary", on_click=lambda _: page.go("/diary")),
            ft.IconButton(ft.Icons.TRENDING_UP, tooltip="Investments", on_click=lambda _: page.go("/investments")),
            ft.IconButton(ft.Icons.SETTINGS, tooltip="Settings", on_click=lambda _: page.go("/settings")),
        ], alignment="spaceAround")
    )

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        bgcolor="#1e1e2e",
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.ADD, selected_icon=ft.Icons.ADD_CIRCLE, label="New"),
            ft.NavigationRailDestination(icon=ft.Icons.RECEIPT_LONG, selected_icon=ft.Icons.RECEIPT, label="Diary"),
            ft.NavigationRailDestination(icon=ft.Icons.TRENDING_UP, selected_icon=ft.Icons.SSID_CHART, label="Investments"),
            ft.NavigationRailDestination(icon=ft.Icons.SETTINGS, selected_icon=ft.Icons.SETTINGS, label="Settings"),
        ],
        on_change=lambda e: page.go(["/new", "/diary", "/investments", "/settings"][e.control.selected_index]),
    )

    content_stack = ft.Stack(expand=True)

    def route_change(route):
        content_stack.controls.clear()
        route_to_index = {"/new": 0, "/diary": 1, "/investments": 2, "/settings": 3}
        rail.selected_index = route_to_index.get(page.route, 1)
        if page.route == "/new":
            content_stack.controls.append(new_entry_tab)
        elif page.route == "/diary":
            content_stack.controls.append(diary_tab)
        elif page.route == "/investments":
            content_stack.controls.append(investments_tab)
        elif page.route == "/settings":
            content_stack.controls.append(settings_tab)
        page.update()

    page.on_route_change = route_change

    page.add(
        ft.Column([
            daily_fire_container(),
            ft.Container(balance_text, padding=20),
            ft.Row([
                rail,
                ft.VerticalDivider(width=1),
                ft.Container(content_stack, expand=True),
            ], expand=True),
        ], expand=True)
    )

    page.bottom_appbar = bottom_nav
    update_balance()
