# controls/mobile.py
import flet as ft
from src.services.core import svc_get_balance

def build_mobile_ui(page: ft.Page,
                    new_entry_tab,
                    diary_tab,
                    monthly_tab,
                    investments_tab,
                    graphs_tab,
                    settings_tab):
    balance_text = ft.Text(size=36, weight="bold", text_align="center")

    def update_balance():
        bal = svc_get_balance()
        balance_text.value = f"R{bal:,.2f}"
        balance_text.color = "#07ff07" if bal >= 0 else "red"
        page.update()

    page.balance_updater = update_balance

    bottom_nav = ft.BottomAppBar(
        bgcolor="#111122",
        height=70,
        content=ft.Row([
            ft.IconButton(ft.Icons.ADD, tooltip="New", on_click=lambda _: page.go("/new")),
            ft.IconButton(ft.Icons.RECEIPT_LONG, tooltip="Diary", on_click=lambda _: page.go("/diary")),
            ft.IconButton(ft.Icons.CALENDAR_MONTH, tooltip="Monthly", on_click=lambda _: page.go("/monthly")),
            ft.IconButton(ft.Icons.TRENDING_UP, tooltip="Investments", on_click=lambda _: page.go("/investments")),
            ft.IconButton(ft.Icons.TRENDING_UP_SHARP, tooltip="Graphs", on_click=lambda _: page.go("/graphs")),
            ft.IconButton(ft.Icons.SETTINGS, tooltip="Settings", on_click=lambda _: page.go("/settings")),
        ], alignment="spaceAround")
    )

    main_row = ft.Row(expand=True)
    content_stack = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    rail = None

    main_row.controls = [ft.Container(content_stack, expand=True)]

    def route_change(e):
        route = e.route
        content_stack.controls.clear()
        if route == "/new":
            content_stack.controls.append(new_entry_tab)
        elif route == "/diary":
            content_stack.controls.append(diary_tab)
        elif route == "/monthly":
            content_stack.controls.append(monthly_tab)
        elif route == "/investments":
            content_stack.controls.append(investments_tab)
        elif route == "/graphs":
            content_stack.controls.append(graphs_tab)
        elif route == "/settings":
            content_stack.controls.append(settings_tab)
        page.update()

    page.on_route_change = route_change

    page.add(
        ft.Column([
            ft.Container(balance_text, padding=20),
            main_row
        ], expand=True)
    )

    page.bottom_appbar = bottom_nav
    page.go(page.route or "/new")
    update_balance()
