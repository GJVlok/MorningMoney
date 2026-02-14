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
    """
    Responsive transaction tile for desktop/web.
    Shows date, category, description preview, tags, amount + balance,
    with edit/delete buttons and hover effect.
    """
    # ── Description preview ──────────────────────────────────────
    full_desc = transaction.description or transaction.date.strftime("%d %b %Y")
    preview_desc = full_desc[:60] + "..." if len(full_desc) > 60 else full_desc

    # ── Tags as small chips ──────────────────────────────────────
    tags_list = [t.strip() for t in (transaction.tags or "").split(",") if t.strip()]
    tag_chips = ft.Row(
        controls=[
            ft.Chip(
                label=ft.Text(tag, size=11, color=ft.Colors.WHITE70),
                bgcolor=ft.Colors.BLUE_GREY_800,
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
            )
            for tag in tags_list[:4]
        ],
        wrap=True,
        spacing=6,
        run_spacing=4,
    )
    if len(tags_list) > 4:
        tag_chips.controls.append(
            ft.Text(f"+{len(tags_list)-4}", size=11, color=ft.Colors.GREY_500)
        )

    # ── Title / info column ──────────────────────────────────────
    title_area = ft.Column(
        spacing=4,
        controls=[
            ft.Row(
                [
                    ft.Text(
                        transaction.date.strftime("%d %b %Y"),
                        size=13,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Container(expand=True),
                    ft.Text(
                        f"Balance: {money_text(running_balance).value}" if running_balance is not None else "",
                        size=13,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Text(
                transaction.category,
                size=16,
                weight=ft.FontWeight.W_600,
                color=ft.Colors.WHITE,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            ft.Text(
                preview_desc,
                size=14,
                color=ft.Colors.GREY_400,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
                tooltip=full_desc if full_desc != preview_desc else None,
            ),
            tag_chips,
        ],
        expand=True,
    )

    # ── Amount display with sign-based coloring ──────────────────
    amount_color = ft.Colors.GREEN_300 if transaction.amount >= 0 else ft.Colors.RED_300
    amount_text = money_text(
        transaction.amount,
        size=20,
        weight=ft.FontWeight.BOLD,
        color=amount_color,
    )

    amount_area = ft.Column(
        [
            amount_text,
            ft.Text(
                f"Balance: {money_text(running_balance).value}" if running_balance is not None else "",
                size=12,
                color=ft.Colors.GREY_600,
                text_align=ft.TextAlign.END,
            ),
        ],
        spacing=2,
        horizontal_alignment=ft.CrossAxisAlignment.END,
    )

    # ── Action buttons ───────────────────────────────────────────
    actions = ft.Column(
        spacing=0,
        controls=[
            ft.IconButton(
                ft.Icons.EDIT_OUTLINED,
                icon_color=ft.Colors.BLUE_300,
                tooltip="Edit transaction",
                on_click=lambda e: page.run_task(
                    edit_transaction_dialog, page, transaction, refresh_all
                ),
            ),
            ft.IconButton(
                ft.Icons.DELETE_OUTLINE,
                icon_color=ft.Colors.RED_400,
                tooltip="Delete transaction",
                on_click=lambda e: page.run_task(
                    delete_transaction, page, transaction, refresh_all
                ),
            ),
        ],
    )

    # ── Main responsive layout ───────────────────────────────────
    tile = ft.Container(
        content=ft.ResponsiveRow(
            columns=12,
            controls=[
                # Icon column (fixed small)
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.RECEIPT_LONG,
                        color="#ff0066",
                        size=28,
                    ),
                    col={"xs": 1, "sm": 1},
                    alignment=ft.Alignment(0, 0),
                ),
                # Main content (title + desc + tags)
                ft.Container(
                    content=title_area,
                    col={"xs": 11, "sm": 7, "md": 6},
                    padding=ft.padding.only(left=12),
                ),
                # Amount + balance (right-aligned)
                ft.Container(
                    content=amount_area,
                    col={"xs": 12, "sm": 3, "md": 3},
                    alignment=ft.Alignment(1, 0),
                ),
                # Edit/Delete buttons
                ft.Container(
                    content=actions,
                    col={"xs": 12, "sm": 1, "md": 2},
                    alignment=ft.Alignment(1, -0.5),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            run_spacing=8,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.PRIMARY),
        on_hover=lambda e: (
            setattr(e.control, "bgcolor", ft.Colors.with_opacity(0.12, ft.Colors.PRIMARY)),
            e.control.update()
        ),
        on_blur=lambda e: (
            setattr(e.control, "bgcolor", ft.Colors.with_opacity(0.06, ft.Colors.PRIMARY)),
            e.control.update()
        ),
    )

    return tile