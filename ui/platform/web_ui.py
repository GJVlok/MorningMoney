# ui/platform/web_ui.py
import flet as ft
from ui.blocks.daily_fire.daily_fire_web import daily_fire_web
from ui.sections.web.new_tab_web import NewEntryTabWeb
from ui.sections.web.diary_tab_web import DiaryTabWeb
from src.services.core import svc_get_balance

def build_web_ui(page: ft.Page):
    new_tab = NewEntryTabWeb(page, refresh_all=lambda: page.run_async(page.refresh_all if hasattr(page, "refresh_all") else None))
    diary_tab = DiaryTabWeb(page, refresh_all=lambda: page.run_async(page.refresh_all if hasattr(page, "refresh_all") else None))
    investments_tab = ft.Column([ft.Text("Investments (web)")], expand=True)
    settings_tab = ft.Column([ft.Text("Settings (web)")], expand=True)

    balance_text = ft.Text(size=32, weight="bold")
    def update_balance():
        bal = svc_get_balance()
        balance_text.value = f"R{bal:,.2f}"
        balance_text.color = "green" if bal >= 0 else "red"
        page.update()
    page.balance_updater = update_balance

    header = ft.Row([ft.Text("MorningMoney", size=40, weight="bold"), ft.Container(expand=True), balance_text], alignment="spaceBetween")

    tabs = ft.Tabs(
        selected_index=1,
        expand=True,
        animation_duration=300,
        tabs=[
            ft.Tab(text="New", icon=ft.Icons.ADD_CIRCLE, content=new_tab),
            ft.Tab(text="Diary", icon=ft.Icons.RECEIPT_LONG, content=diary_tab),
            ft.Tab(text="Investments", icon=ft.Icons.TRENDING_UP, content=investments_tab),
            ft.Tab(text="Settings", icon=ft.Icons.SETTINGS, content=settings_tab),
        ],
    )

    page.add(
        ft.Column([
            daily_fire_web(page),
            header,
            ft.Divider(height=2),
            tabs,
        ], expand=True, spacing=0)
    )

    update_balance()
