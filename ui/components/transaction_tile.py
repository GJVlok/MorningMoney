# ui/components/transaction_tile.py
import flet as ft
from decimal import Decimal
from src.database import Transaction
from controls.dialogs import edit_transaction_dialog, delete_transaction
from controls.common import money_text

def transaction_tile(
    transaction: Transaction,
    page: ft.Page,
    refresh_all,
    running_balance: Decimal | None = None,
) -> ft.Control:
    """Desktop/Web transaction tile (responsive, with notes preview)."""

    # Preview logic: Shorten desc if long
    full_desc = transaction.description or transaction.date.strftime("%d %b %Y")
    preview_desc = full_desc[:50] + "..." if len(full_desc) > 50 else full_desc

    tags_list = (transaction.tags or "").split(",") if transaction.tags else []
    tag_chips = ft.Row(
        [ft.Chip(label=ft.Text(tag.strip(), size=10), bgcolor="blue200") for tag in tags_list[:3]],
        wrap=True,
        spacing=5,
    )
    # Add "+X more" indicator if there are many tags
    if len(tags_list) > 3:
        tag_chips.controls.append(ft.Text(f"+{len(tags_list)-3} more", size=10, color="grey"))

    # Title area (category + desc preview + future tags)
    title_area = ft.Column(
        [   
            ft.Text(
                transaction.date.strftime("%d %b %Y"),
                size=12,
                color="grey",
            ),
            ft.Text(
                transaction.category,
                weight="bold",
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            ft.Text(
                preview_desc,
                color="grey",
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
                tooltip=full_desc,  # Hover for full (desktop/web)
            ),
            tag_chips,
        ],
        spacing=2,
        expand=True,
    )

    # Amount/Balance (restored, flexible)
    amount_balance = ft.Column(
        [
            money_text(transaction.amount, size=18, weight="bold"),
            ft.Text(
                f"Balance: R{running_balance:,.2f}" if running_balance is not None else "",
                size=12,
                color="grey",
                italic=True,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
        ],
        spacing=2,
        horizontal_alignment="end",
    )

    # Buttons
    buttons = ft.Row(
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
        alignment="end",
    )

    # Main layout: ResponsiveRow for adaptive sizing
    return ft.Container(
        content=ft.ResponsiveRow(
            [
                ft.Container(ft.Icon(ft.Icons.RECEIPT, color="#ff0066"), col=1),  # Icon fixed small
                ft.Container(title_area, col={"xs": 12, "sm": 6, "md": 7}),  # Title expands most
                ft.Container(amount_balance, col={"xs": 12, "sm": 3}),  # Amount/balance next
                ft.Container(buttons, col={"xs": 12, "sm": 2}),  # Buttons stack on narrow
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
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