# controls/desktop.py
import flet as ft
import logging
from src.services.core import svc_get_balance

def build_desktop_ui(
    page: ft.Page,
    new_entry_tab: ft.Container,
    diary_tab: ft.Container,
    monthly_tab: ft.Container,
    investments_tab: ft.Container,
    tags_insights_tab: ft.Container,
    savings_brag_tab: ft.Container,
    graphs_tab: ft.Container,
    settings_tab: ft.Container,
) -> None:

    # ---------------- BALANCE ---------------- #

    balance_text = ft.Text(size=32, weight=ft.FontWeight.BOLD)

    def update_balance():
        try:
            bal = svc_get_balance()

            balance_text.value = f"R{bal:,.2f}"
            balance_text.color = "#94d494" if bal >= 0 else "red"

            logging.info("Balance updated")

        except Exception as e:
            logging.error(f"Balance error: {e}")

    page.balance_updater = update_balance

    # ---------------- HEADER ---------------- #

    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("MorningMoney", size=40, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                balance_text,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=40, vertical=10),
        bgcolor=ft.Colors.GREY_50,
    )

    # ---------------- TABS ---------------- #

    # Headers only (no selected_index here)
    tab_bar = ft.TabBar(
        tabs=[
            ft.Tab(
                label="New",
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            ),
            ft.Tab(
                label="Diary",
                icon=ft.Icons.BOOK,
            ),
            ft.Tab(
                label="Monthly",
                icon=ft.Icons.CALENDAR_MONTH,
            ),
            ft.Tab(
                label="Investments",
                icon=ft.Icons.SHOW_CHART,
            ),
            ft.Tab(
                label="Insights",
                icon=ft.Icons.INSIGHTS,
            ),
            ft.Tab(
                label="Savings",
                icon=ft.Icons.SAVINGS,
            ),
            ft.Tab(
                label="Graphs",
                icon=ft.Icons.BAR_CHART,
            ),
            ft.Tab(
                label="Settings",
                icon=ft.Icons.SETTINGS,
            ),
        ],
    )

    # Contents (must match order and count of tabs above)
    tab_contents = ft.TabBarView(
        expand=True,
        controls=[
            new_entry_tab,
            diary_tab,
            monthly_tab,
            investments_tab,
            tags_insights_tab,
            savings_brag_tab,
            graphs_tab,
            settings_tab,
        ],
    )

    # Wrap in Tabs – this manages selection and syncing
    tabs_section = ft.Tabs(
        length=8,  # must equal len(tab_bar.tabs) and len(tab_contents.controls)
        selected_index=0,
        animation_duration=300,
        content=ft.Column(
            expand=True,
            controls=[
                tab_bar,
                tab_contents,
            ],
            spacing=0,
        ),
    )

    # ---------------- TAB CHANGE EVENT ---------------- #

    def on_tab_change(e: ft.ControlEvent):
        tabs_section.selected_index = tabs_section.selected_index
        tabs_section.update()

    tabs_section.on_change = on_tab_change

    # ---------------- MAIN LAYOUT ---------------- #

    layout = ft.Column(
        controls=[
            header,
            tabs_section,
        ],
        expand=True,
        spacing=0,
    )

    page.add(layout)

    # Initial balance
    update_balance()
