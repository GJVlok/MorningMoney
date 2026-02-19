# controls/desktop.py
import flet as ft
import logging
from src.services.core import svc_get_balance
# from src.services.settings import get_username

def build_desktop_ui(
    page: ft.Page,
    new_entry_tab: ft.Control,
    diary_tab: ft.Control,
    monthly_tab: ft.Control,
    investments_tab: ft.Control,
    tags_insights_tab: ft.Control,
    savings_brag_tab: ft.Control,
    graphs_tab: ft.Control,
    settings_tab: ft.Control
) -> None:

    # ---- Balance display ----
    balance_text = ft.Text(size=32, weight="bold")

    def update_balance():
        try:
            bal = svc_get_balance()
            balance_text.value = f"R{bal:,.2f}"
            balance_text.color = "#94d494" if bal >= 0 else "red"
            page.update()
            logging.info("Balance updated successfully.")
        except Exception as e:
            logging.error(f"Error fetching balance: {e}")
        
    page.balance_updater = update_balance

    # ---- Header ----
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text("MorningMoney", size=40, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                balance_text,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=40, vertical=10),
        bgcolor=ft.Colors.GREY_50,   # or "#f5f5f5"
    )

    # ---- Real tab contents (already wrapped) ----
    wrapped_tabs = ft.TabBarView(
        controls=[
        ft.Container(new_entry_tab, alignment=ft.Alignment.CENTER),
        ft.Container(diary_tab, alignment=ft.Alignment.CENTER),
        ft.Container(monthly_tab, alignment=ft.Alignment.CENTER),
        ft.Container(investments_tab, alignment=ft.Alignment.CENTER),
        ft.Container(tags_insights_tab, alignment=ft.Alignment.CENTER),
        ft.Container(savings_brag_tab, alignment=ft.Alignment.CENTER),
        ft.Container(graphs_tab, alignment=ft.Alignment.CENTER),
        ft.Container(settings_tab, alignment=ft.Alignment.CENTER),
        ],
        expand=True,
    )

    # ---- Tabs ----
    tab_bar = ft.Tabs(
        length=8,
        selected_index=0,
        animation_duration=300,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="New", icon=ft.Icons.ADD_CIRCLE_OUTLINE),
                        ft.Tab(label="Diary", icon=ft.Icons.BOOK),
                        ft.Tab(label="Monthly", icon=ft.Icons.CALENDAR_MONTH),
                        ft.Tab(label="Investments", icon=ft.Icons.SHOW_CHART),
                        ft.Tab(label="Insights", icon=ft.Icons.INSIGHTS),
                        ft.Tab(label="Savings", icon=ft.Icons.SAVINGS),
                        ft.Tab(label="Graphs", icon=ft.Icons.BAR_CHART),
                        ft.Tab(label="Settings", icon=ft.Icons.SETTINGS),
                    ],
                )
            ]
        )
    )

    # ---- Main layout ----
    main_column = ft.Column(
        [
            header,
            tab_bar,
            wrapped_tabs,
        ],
        expand=True,
        spacing=0,
    )

    # ---- Add everything ----
    page.add(main_column)

    # Initial update
    update_balance()

    # Optional: call when coming back to "New" tab (example)
    def on_tab_changed(e):
        if tab_bar.selected_index == 0:
            update_balance()
            # you can also refresh other tabs here if needed

    tab_bar.on_change = on_tab_changed