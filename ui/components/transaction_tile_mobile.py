# ui/components/transaction_tile_mobile.py
import flet as ft
from src.database import Transaction
from controls.dialogs import edit_transaction_dialog, delete_transaction
from ui.components.transaction_tile import transaction_tile


def _mobile_transaction_menu(
    transaction: Transaction,
    page: ft.Page,
    refresh_all,
):
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
                    ],
                    tight=True,
                    spacing=10,
                ),
                padding=20,
                bgcolor=ft.Colors.with_opacity(0.98, "#1e1e2e"),
                border_radius=12,
            ),
            open=True,
            enable_drag=True,
            is_scroll_controlled=True,
        )
        page.bottom_sheet = sheet
        page.update()

    return handler


def transaction_tile_mobile(
    transaction: Transaction,
    page: ft.Page,
    refresh_all,
    running_balance: float | None = None,
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