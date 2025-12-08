# ui/platform/desktop_ui.py
import flet as ft
from ui.blocks.daily_fire.daily_fire_desktop import daily_fire_desktop
from ui.sections.desktop.new_tab_desktop import NewEntryTabDesktop
from ui.sections.desktop.diary_tab_desktop import DiaryTabDesktop
from ui.sections.desktop.investments_tab_desktop import InvestmentsTabDesktop
from src.services.core import svc_get_balance

def build_desktop_ui(page: ft.Page):
    # build platform tabs (desktop-specific)
    new_tab = NewEntryTabDesktop(page, refresh_all=lambda: page.run_async(page.refresh_all if hasattr(page, "refresh_all") else None))
    diary_tab = DiaryTabDesktop(page, refresh_all=lambda: page.run_async(page.refresh_all if hasattr(page, "refresh_all") else None))
    investments_tab = InvestmentsTabDesktop(page, refresh_all=lambda: page.run_async(page.refresh_all if hasattr(page, "refresh_all") else None))
    settings_tab = ft.Column([ft.Text("Settings (desktop)")], expand=True)  # placeholder

    balance_text = ft.Text(size=32, weight="bold")
    def update_balance():
        bal = svc_get_balance()
        balance_text.value = f"R{bal:,.2f}"
        balance_text.color = "#07ff07" if bal >= 0 else "red"
        page.update()
    page.balance_updater = update_balance

    header = ft.Row([
        ft.Text("MorningMoney", size=40, weight="bold"),
        ft.Container(expand=True),
        balance_text,
    ], alignment="spaceBetween")

    tabs = ft.Tabs(
        selected_index=1,  # default Diary
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
            daily_fire_desktop(page),
            header,
            ft.Divider(height=2),
            tabs,
        ], expand=True, spacing=0)
    )

    update_balance()
