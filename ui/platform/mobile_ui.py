# ui/platform/mobile_ui.py
import flet as ft
from ui.blocks.daily_fire.daily_fire_mobile import daily_fire_mobile
from ui.sections.mobile.new_tab_mobile import NewEntryTabMobile
from ui.sections.mobile.diary_tab_mobile import DiaryTabMobile
from src.services.core import svc_get_balance

def build_mobile_ui(page: ft.Page):
    # platform-specific tabs
    new_tab = NewEntryTabMobile(page, refresh_all=lambda: page.run_async(page.refresh_all if hasattr(page, "refresh_all") else None))
    diary_tab = DiaryTabMobile(page, refresh_all=lambda: page.run_async(page.refresh_all if hasattr(page, "refresh_all") else None))
    investments_tab = ft.Column([ft.Text("Investments (mobile)")], expand=True)
    settings_tab = ft.Column([ft.Text("Settings (mobile)")], expand=True)

    balance_text = ft.Text(size=28, weight="bold", text_align="center")
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
            ft.IconButton(ft.Icons.TRENDING_UP, tooltip="Investments", on_click=lambda _: page.go("/investments")),
            ft.IconButton(ft.Icons.SETTINGS, tooltip="Settings", on_click=lambda _: page.go("/settings")),
        ], alignment="spaceAround")
    )

    # content stack is a single column in mobile
    content_stack = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    def route_change(route):
        content_stack.controls.clear()
        if page.route == "/new":
            content_stack.controls.append(new_tab)
        elif page.route == "/diary":
            content_stack.controls.append(diary_tab)
        elif page.route == "/investments":
            content_stack.controls.append(investments_tab)
        else:
            content_stack.controls.append(settings_tab)
        page.update()

    page.on_route_change = route_change

    page.add(
        ft.Column([
            daily_fire_mobile(page),
            ft.Container(balance_text, padding=12),
            content_stack
        ], expand=True)
    )

    page.bottom_appbar = bottom_nav
    update_balance()
