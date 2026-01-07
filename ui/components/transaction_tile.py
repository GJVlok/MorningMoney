# ui/components/transaction_tile.py
import flet as ft
from src.database import Transaction
from controls.dialogs import edit_transaction_dialog, delete_transaction
from controls.common import money_text

def transaction_tile(
    transaction: Transaction,
    page: ft.Page,
    refresh_all,
    running_balance: float | None = None,
) -> ft.Control:
    """Desktop/Web transaction tile (no mobile UX)."""

    trailing_content = ft.Column(
        [
            money_text(transaction.amount, size=18, weight="bold"),
            ft.Text(
                f"Balance: R{running_balance:,.2f}"
                if running_balance is not None
                else "",
                size=12,
                color="grey",
                italic=True,
            ),
        ],
        spacing=2,
        horizontal_alignment="end",
    )

    title_area = ft.Column(
        [
            ft.Text(transaction.category, weight="bold", no_wrap=False),
            ft.Text(
                transaction.description
                or transaction.date.strftime("%d %b %Y"),
                color="grey",
                no_wrap=False,
            ),
        ],
        spacing=2,
        expand=1,
    )

    base_tile = ft.ListTile(
        leading=ft.Icon(ft.Icons.RECEIPT, color="#ff0066"),
        title=title_area,
        trailing=ft.Container(trailing_content, width=120),
        dense=False,
    )

    return ft.Container(
        content=ft.Row(
            [
                ft.Container(base_tile, expand=True),
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.EDIT,
                            icon_color="blue400",
                            tooltip="Edit",
                            on_click=lambda _: page.run_task(
                                edit_transaction_dialog,
                                page,
                                transaction,
                                refresh_all,
                            ),
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE,
                            icon_color="red400",
                            tooltip="Delete",
                            on_click=lambda _: page.run_task(
                                delete_transaction,
                                page,
                                transaction,
                                refresh_all,
                            ),
                        ),
                    ],
                    spacing=4,
                ),
            ],
            alignment="spaceBetween",
            vertical_alignment="center",
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        border_radius=12,
        on_hover=lambda e: (
            setattr(
                e.control,
                "bgcolor",
                "#2d2d3d" if e.data == "true" else None,
            ),
            e.control.update(),
        ),
    )
