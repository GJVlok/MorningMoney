# ui/components/investment_card.py
import flet as ft
from src.database import Investment
from src.services.core import svc_calculate_future_value
from controls.dialogs import edit_investment_dialog, delete_investment


def _investment_card_content(investment: Investment) -> ft.Column:
    fv = svc_calculate_future_value(investment)

    status_color = "#00ff88" if fv >= 10_000_000 else "orange"
    status_text = "FIRE!" if fv >= 10_000_000 else "on track"

    return ft.Column(
        spacing=8,
        controls=[
            ft.Text(investment.name, size=22, weight="bold", color="white"),
            ft.Text(
                f"Current: R{investment.current_value:,.0f}  •  "
                f"+R{investment.monthly_contribution:,.0f}/mo @ "
                f"{investment.expected_annual_return}%",
                color="grey",
            ),
            ft.Divider(color="grey"),
            ft.Text("Projected", color=status_color),
            ft.Text(f"R{fv:,.0f}", size=34, weight="bold", color=status_color),
            ft.Text(
                f"R{fv / 1_000_000:.2f} million {status_text}",
                color=status_color,
                italic=True,
            ),
        ],
    )


def investment_card(
    investment: Investment,
    page: ft.Page,
    refresh_all,
) -> ft.Card:
    """Desktop / Web investment card"""

    content = _investment_card_content(investment)

    return ft.Card(
        elevation=8,
        content=ft.Container(
            bgcolor="#1e1e2e",
            border_radius=12,
            padding=10,
            content=ft.Row(
                alignment="spaceBetween",
                controls=[
                    ft.Container(content=content, padding=20, expand=True),
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.IconButton(
                                ft.Icons.EDIT,
                                tooltip="Edit",
                                on_click=lambda e: page.run_task(
                                    edit_investment_dialog,
                                    page,
                                    investment,
                                    refresh_all,
                                ),
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                tooltip="Delete",
                                on_click=lambda e: page.run_task(
                                    delete_investment,
                                    page,
                                    investment,
                                    refresh_all,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ),
    )
