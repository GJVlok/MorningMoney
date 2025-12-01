# ui/components/transaction_tile.py
import flet as ft
from src.database import Transaction
from ui.dialogs import edit_transaction_dialog, delete_transaction, money_text


def _mobile_transaction_menu(t: Transaction, page: ft.Page, refresh_all):
    """Mobile-only long-press bottom sheet"""
    def handler(e):
        bs = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.EDIT, color="blue"),
                            title=ft.Text("Edit"),
                            on_click=lambda _: (
                                edit_transaction_dialog(page, t, refresh_all),
                                setattr(bs, "open", False),
                                page.update(),
                            ),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DELETE, color="red"),
                            title=ft.Text("Delete", color="red"),
                            on_click=lambda _: (
                                delete_transaction(page, t, refresh_all),
                                setattr(bs, "open", False),
                                page.update(),
                            ),
                        ),
                    ],
                    tight=True,
                ),
                padding=20,
                bgcolor=ft.Colors.ON_SURFACE_VARIANT,
                border_radius=10,
            ),
            open=True,
            enable_drag=True,
            is_scroll_controlled=True,
        )
        page.bottom_sheet = bs
        page.update()

    return handler


def transaction_tile(transaction: Transaction, page: ft.Page, refresh_all) -> ft.Control:
    """Platform-aware transaction row/card. Pure widget — no business logic."""
    base = ft.ListTile(
        leading=ft.Icon(ft.Icons.RECEIPT, color="#ff0066"),
        title=ft.Text(transaction.category, weight="bold"),
        subtitle=ft.Text(
            transaction.description or transaction.date.strftime("%d %b %Y"),
            color="grey",
        ),
        trailing=money_text(transaction.amount, size=18),
    )

    # ── Desktop: hover + edit/delete icons ─────────────────────────────
    if page.platform in ("windows", "macos", "linux"):
        return ft.Container(
            content=ft.Row(
                [
                    base,
                    ft.Row(
                        [
                            ft.IconButton(
                                ft.Icons.EDIT,
                                icon_color="blue400",
                                tooltip="Edit",
                                on_click=lambda _: edit_transaction_dialog(page, transaction, refresh_all),
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                icon_color="red400",
                                tooltip="Delete",
                                on_click=lambda _: delete_transaction(page, transaction, refresh_all),
                            ),
                        ],
                        spacing=4,
                    ),
                ],
                alignment="spaceBetween",
                expand=True,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=8,
            on_hover=lambda e: setattr(
                e.control, "bgcolor", "#2d2d3d" if e.data == "true" else None
            )
            or e.control.update(),
        )

    # ── Mobile: long-press menu ───────────────────────────────────────
    base.on_long_press = _mobile_transaction_menu(transaction, page, refresh_all)
    return base