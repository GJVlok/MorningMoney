# controls/desktop.py
import flet as ft
from src.services.core import svc_get_balance

def build_desktop_ui(page: ft.Page, new_entry_tab, diary_tab, investments_tab, settings_tab):
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
        ft.Text(f"Hi, {page.session.get('username') or 'friend'}!", size=18, color="grey"),
        balance_text,
    ], alignment="spaceBetween")

    tabs = ft.Tabs(
        selected_index=0,
        expand=True,
        animation_duration=300,
        tabs=[
            ft.Tab(text="New", icon=ft.Icons.ADD_CIRCLE, content=new_entry_tab),
            ft.Tab(text="Diary", icon=ft.Icons.RECEIPT_LONG, content=diary_tab),
            ft.Tab(text="Investments", icon=ft.Icons.TRENDING_UP, content=investments_tab),
            ft.Tab(text="Settings", icon=ft.Icons.SETTINGS, content=settings_tab),
        ],
    )

    page.add(
        ft.Column([
            header,
            ft.Divider(height=2),
            tabs,
        ], expand=True, spacing=0)
    )

    update_balance()
