# ui/components/transaction_tile.py
import flet as ft
from src.database import Transaction
from ui.dialogs import edit_transaction_dialog, delete_transaction
from controls.common import is_currently_desktop, money_text

def _mobile_transaction_menu(t: Transaction, page: ft.Page, refresh_all):
    def handler(e):
        bs = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.EDIT, color="blue"),
                            title=ft.Text("Edit"),
                            on_click=lambda _: (page.run_task(edit_transaction_dialog, page, t, refresh_all), setattr(bs, "open", False), page.update()),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DELETE, color="red"),
                            title=ft.Text("Delete", color="red"),
                            on_click=lambda _: (page.run_task(delete_transaction, page, t, refresh_all), setattr(bs, "open", False), page.update()),
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
        page.bottom_sheet = bs
        page.update()
    return handler

def transaction_tile(transaction: Transaction, page: ft.Page, refresh_all, running_balance: float = None) -> ft.Control:
    # Build the trailing: amount + running balance below
    trailing_content = ft.Column(
        [
            money_text(transaction.amount, size=18, weight="bold"),
            ft.Text(
                f"Balance: R{running_balance:,.2f}" if running_balance is not None else "",
                size=12,
                color="grey",
                italic=True,
            )
        ],
        spacing=2,
        horizontal_alignment="end",
    )

    base = ft.ListTile(
        leading=ft.Icon(ft.Icons.RECEIPT, color="#ff0066"),
        title=ft.Text(transaction.category, weight="bold", no_wrap=False),
        subtitle=ft.Text(transaction.description or transaction.date.strftime("%d %b %Y"), color="grey", no_wrap=False),
        trailing=trailing_content,  # ← Now shows amount + balance
        dense=False,
    )

    if is_currently_desktop(page):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(base, expand=True),
                    ft.Row(
                        [
                            ft.IconButton(ft.Icons.EDIT, icon_color="blue400", tooltip="Edit", on_click=lambda _: page.run_task(edit_transaction_dialog, page, transaction, refresh_all)),
                            ft.IconButton(ft.Icons.DELETE, icon_color="red400", tooltip="Delete", on_click=lambda _: page.run_task(delete_transaction, page, transaction, refresh_all)),
                        ],
                        spacing=4,
                    ),
                ],
                alignment="spaceBetween",
                expand=True,
                vertical_alignment="center",
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=12,
            on_hover=lambda e: setattr(e.control, "bgcolor", "#2d2d3d" if e.data == "true" else None) or e.control.update(),
        )

    return ft.Dismissible(
        content=ft.Card(
            elevation=4,
            content=ft.Container(content=base, padding=12, border_radius=10, expand=True, on_click=_mobile_transaction_menu(transaction, page, refresh_all)),
            margin=8,
            color="#1e1e2e",
        ),
        background=ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.DELETE_FOREVER, size=40, color="white")], alignment="end", expand=True),
            padding=30,
            bgcolor="red",
        ),
        dismiss_direction=ft.DismissDirection.START_TO_END,
        on_dismiss=lambda _: page.run_task(page, transaction, refresh_all),
    )
