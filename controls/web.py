# controls/web.py
import flet as ft
from src.services.core import svc_get_balance

def build_web_ui(page: ft.Page,
                 new_entry_tab,
                 diary_tab,
                 monthly_tab,
                 investments_tab,
                 tags_insights_tab,
                 savings_brag_tab,
                 graphs_tab,
                 settings_tab):
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
        selected_index=0,
        expand=True,
        animation_duration=300,
        tabs=[
            ft.Tab(label="New", icon=ft.Icons.ADD_CIRCLE, content=new_entry_tab),
            ft.Tab(label="Diary", icon=ft.Icons.RECEIPT_LONG, content=diary_tab),
            ft.Tab(label="Monthly", icon=ft.Icons.CALENDAR_MONTH, content=monthly_tab),
            ft.Tab(label="Investments", icon=ft.Icons.TRENDING_UP, content=investments_tab),
            ft.Tab(label="Tag Insights", icon=ft.Icons.TAG, content=tags_insights_tab),
            ft.Tab(label="Savings Brag", icon=ft.Icons.SAVINGS, content=savings_brag_tab),
            ft.Tab(label="Graphs", icon=ft.Icons.BAR_CHART, content=graphs_tab),
            ft.Tab(label="Settings", icon=ft.Icons.SETTINGS, content=settings_tab),
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
