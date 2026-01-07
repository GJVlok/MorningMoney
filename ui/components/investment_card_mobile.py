# ui/components/investment_card_mobile.py
import flet as ft
from src.database import Investment
from controls.dialogs import edit_investment_dialog, delete_investment
from ui.components.investment_card import _investment_card_content


def investment_card_mobile(
    investment: Investment,
    page: ft.Page,
    refresh_all,
) -> ft.Card:
    def open_menu(e):
        sheet = ft.BottomSheet(
            content=ft.Container(
                padding=20,
                bgcolor=ft.Colors.with_opacity(0.98, "#1e1e2e"),
                border_radius=12,
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.EDIT, color="blue"),
                            title=ft.Text("Edit"),
                            on_click=lambda _: (
                                page.run_task(
                                    edit_investment_dialog,
                                    page,
                                    investment,
                                    refresh_all,
                                ),
                                setattr(sheet, "open", False),
                                page.update(),
                            ),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DELETE, color="red"),
                            title=ft.Text("Delete", color="red"),
                            on_click=lambda _: (
                                page.run_task(
                                    delete_investment,
                                    page,
                                    investment,
                                    refresh_all,
                                ),
                                setattr(sheet, "open", False),
                                page.update(),
                            ),
                        ),
                    ],
                ),
            ),
            open=True,
            enable_drag=True,
            is_scroll_controlled=True,
        )

        page.bottom_sheet = sheet
        page.update()

    return ft.Card(
        elevation=6,
        margin=8,
        content=ft.Container(
            padding=20,
            bgcolor="#1e1e2e",
            border_radius=12,
            content=_investment_card_content(investment),
            on_click=open_menu,
        ),
    )
