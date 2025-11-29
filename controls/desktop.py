# controls/desktop.py
import flet as ft
from .common import money_text, daily_fire_container
from src.models import get_balance

def build_desktop_ui(page: ft.Page, new_entry_tab, diary_tab, investments_tab):
    # Live balance in header
    balance_text = ft.Text(size=32, weight="bold")

    def update_balance():
        bal = get_balance()
        balance_text.value = f"R{bal:,.2f}"
        balance_text.color = "green" if bal >= 0 else "red"
        page.update()

    page.balance_updater = update_balance  # we'll call this from tabs

    header = ft.Row([
        ft.Text("MorningMoney", size=40, weight="bold"),
        ft.Text("", expand=True),
        balance_text,
    ], alignment="spaceBetween")

    tabs = ft.Tabs(
        selected_index=0,
        expand=True,
        tabs=[
            ft.Tab(text="New", icon=ft.Icons.ADD_CIRCLE, content=new_entry_tab),
            ft.Tab(text="Diary", icon=ft.Icons.RECEIPT_LONG, content=diary_tab),
            ft.Tab(text="Investments", icon=ft.Icons.TRENDING_UP, content=investments_tab),
        ]
    )

    page.add(
        ft.Column([
            daily_fire_container(),
            header,
            ft.Divider(height=2),
            tabs
        ], expand=True)
    )

    update_balance()  # initial