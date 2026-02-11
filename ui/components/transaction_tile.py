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
    """Desktop/Web transaction tile (no mobile UX)."""

    trailing_content = ft.Column(
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

    title_area = ft.Column(
        [
            ft.Text(
                transaction.category,
                weight="bold",
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            ft.Text(
                transaction.description
                or transaction.date.strftime("%d %b %Y"),
                color="grey",
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            # Future tags: Add a Row here for chips (e.g., ft.Chip for each tag).
            # Placeholder: When you implement, fetch tags from Transaction model (add a 'tags' field as list[str]).
            # Example: ft.Row([ft.Chip(label=ft.Text(tag), bgcolor="blue200") for tag in transaction.tags or []], wrap=True),
        ],
        spacing=2,
        expand=True,
    )

    base_tile = ft.ListTile(
        leading=ft.Icon(ft.Icons.RECEIPT, color="#ff0066"),
        title=title_area,
        trailing=trailing_content,
    )

    # Outer container: Use ResponsiveRow for better resizing.
    # Teach: ResponsiveRow adapts columns based on breakpoints (e.g., col=12 full width on small screens).
    # This prevents cutoff by stacking if window is too narrow.
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(base_tile, col={"xs": 12, "sm": 9}), # Main content takes most space
                ft.Container( # Buttons stack vertically on small, horizontal on large.
                    content=ft.Row(
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
                        alignment="end", # Align right
                    ),
                    col={"xs": 12, "sm": 3}, #Buttons take less space, stack on mobile-like narrow.
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
