# controls/desktop.py
import flet as ft
from src.services import svc_get_balance
from controls.common import money_text, daily_fire_container

def build_desktop_ui(page: ft.Page, new_entry_tab, diary_tab, investments_tab, settings_tab):
    balance_text = ft.Text(size=32, weight="bold")

    def update_balance():
        bal = svc_get_balance()
        balance_text.value = f"R{bal:,.2f}"
        balance_text.color = "green" if bal >= 0 else "red"
        page.update()

    page.balance_updater = update_balance

    header = ft.Row([
        ft.Text("MorningMoney", size=40, weight="bold"),
        ft.Container(expand=True),
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
            daily_fire_container(),
            header,
            ft.Divider(height=2),
            tabs,
        ], expand=True, spacing=0)
    )

    update_balance()
