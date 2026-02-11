# ui/components/transaction_tile_mobile.py
import flet as ft
from decimal import Decimal
from src.database import Transaction
from controls.dialogs import edit_transaction_dialog, delete_transaction
from ui.components.transaction_tile import transaction_tile  # Reuse base

def _mobile_transaction_menu(
    transaction: Transaction,
    page: ft.Page,
    refresh_all,
):
    full_desc = transaction.description or transaction.date.strftime("%d %b %Y")

    def show_full_notes(_):
        sheet = ft.BottomSheet(
            content=ft.Container(
                ft.Column(
                    [
                        ft.Text("Full Notes", size=18, weight="bold"),
                        ft.Text(full_desc, size=14),
                    ],
                    spacing=10,
                ),
                padding=20,
                bgcolor=ft.Colors.with_opacity(0.98, "#1e1e2e"),
                border_radius=12,
            ),
            open=True,
            enable_drag=True,
        )
        page.bottom_sheet = sheet
        page.update()

    def handler(_):
        sheet = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.EDIT, color="blue"),
                            title=ft.Text("Edit"),
                            on_click=lambda _: (
                                page.run_task(
                                    edit_transaction_dialog,
                                    page,
                                    transaction,
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
                                    delete_transaction,
                                    page,
                                    transaction,
                                    refresh_all,
                                ),
                                setattr(sheet, "open", False),
                                page.update(),
                            ),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.NOTES, color="green"),
                            title=ft.Text("View Full Notes"),
                            on_click=lambda _: (
                                show_full_notes(_),
                                setattr(sheet, "open", False),
                                page.update(),
                            ),
                        ),
                    ],
                ),
                padding=20,
                bgcolor=ft.Colors.with_opacity(0.98, "#1e1e2e"),
                border_radius=12,
            ),
            open=True,
            enable_drag=True,
        )
        page.bottom_sheet = sheet
        page.update()

    return handler

def transaction_tile_mobile(
    transaction: Transaction,
    page: ft.Page,
    refresh_all,
    running_balance: Decimal | None = None,
) -> ft.Control:
    """Mobile-specific transaction tile with gestures."""

    base_tile = transaction_tile(
        transaction,
        page,
        refresh_all,
        running_balance,
    )

    return ft.Dismissible(
        content=ft.Card(
            elevation=4,
            margin=8,
            color="#1e1e2e",
            content=ft.Container(
                content=base_tile,
                padding=12,
                border_radius=10,
                on_click=_mobile_transaction_menu(
                    transaction,
                    page,
                    refresh_all,
                ),
            ),
        ),
        background=ft.Container(
            content=ft.Row(
                [ft.Icon(ft.Icons.DELETE_FOREVER, size=40, color="white")],
                alignment="end",
                expand=True,
            ),
            padding=30,
            bgcolor="red",
        ),
        dismiss_direction=ft.DismissDirection.START_TO_END,
        on_dismiss=lambda _: page.run_task(
            delete_transaction,
            page,
            transaction,
            refresh_all,
        ),
    )