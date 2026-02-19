# ui/components/investment_card.py
import flet as ft
from datetime import date as dt_date
from decimal import Decimal
from src.database import Investment
from src.services.core import svc_calculate_future_value
from controls.dialogs import edit_investment_dialog, delete_investment
from ui.components.investment_form import investment_form  # ← new connection


# Constants – easy to tweak later (e.g. adjust FIRE goal per user)
FIRE_THRESHOLD = Decimal("10000000")  # R10M
FIRE_COLOR = "#00ff88"                # bright green
ON_TRACK_COLOR = "#ffaa00"            # warm orange
CARD_BG = "#1e1e2e"


def _build_card_content(inv: Investment) -> ft.Column:
    """Core content – reusable & testable"""
    try:
        fv = svc_calculate_future_value(inv)
        years_to_target = inv.target_year - dt_date.today().year
        status_color = FIRE_COLOR if fv >= FIRE_THRESHOLD else ON_TRACK_COLOR
        status_label = "FIRE Achieved!" if fv >= FIRE_THRESHOLD else f"On Track (~{years_to_target} yrs)"
        
        return ft.Column(
            spacing=10,
            controls=[
                ft.Text(inv.name or "Unnamed Investment", size=22, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(
                    f"Current: R{inv.current_value:,.0f}  •  "
                    f"+R{inv.monthly_contribution:,.0f}/mo @ {inv.expected_annual_return}%",
                    size=14,
                    color=ft.Colors.GREY_400,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_700),
                ft.Row(
                    [
                        ft.Text("Projected Value", size=16, color=status_color),
                        ft.Text(f"R{fv:,.0f}", size=32, weight=ft.FontWeight.BOLD, color=status_color),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    f"≈ R{fv / Decimal('1000000'):.1f}M – {status_label}",
                    size=14,
                    color=status_color,
                    italic=True,
                ),
            ],
        )
    except Exception as e:
        return ft.Column([
            ft.Text("Error calculating projection", color=ft.Colors.RED_400),
            ft.Text(str(e), size=12, color=ft.Colors.GREY_500),
        ])


def investment_card(
    investment: Investment,
    page: ft.Page,
    refresh_all,
) -> ft.Card:
    """Investment summary card – desktop/web style"""

    content = _build_card_content(investment)

    def on_edit(e):
        # Option A: Use modern form directly (recommended)
        # page.dialog = ft.AlertDialog(
        #     modal=True,
        #     content=investment_form(page, refresh_all, existing_inv=investment),
        #     actions=[ft.TextButton("Close", on_click=lambda _: page.close_dialog())],
        # )
        # page.dialog.open = True
        # page.update()

        # Option B: Keep using your dialog function (if you prefer popup style)
        page.run_task(edit_investment_dialog, page, investment, refresh_all)

    def on_delete(e):
        page.run_task(delete_investment, page, investment, refresh_all)

    card = ft.Card(
        elevation=6,
        bgcolor=CARD_BG,
        margin=ft.margin.all(8),
        content=ft.Container(
            border_radius=16,
            padding=16,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(content=content, expand=True),
                    ft.Column(
                        spacing=8,
                        controls=[
                            ft.IconButton(
                                ft.Icons.EDIT_OUTLINED,
                                icon_color=ft.Colors.BLUE_300,
                                tooltip="Edit investment",
                                on_click=on_edit,
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.RED_400,
                                tooltip="Delete investment",
                                on_click=on_delete,
                            ),
                        ],
                    ),
                ],
            ),
            on_hover=lambda e: setattr(card, "elevation", 12 if e.data == "true" else 6) or card.update(),
        ),
    )

    return card