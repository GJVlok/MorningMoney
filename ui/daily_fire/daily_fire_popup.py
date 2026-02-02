# ui/daily_fire/daily_fire_popup.py
import flet as ft
from src.motivation import daily_message
from src.services.core import (
    svc_get_balance,
    svc_get_total_projected_wealth,
)


def _get_daily_fire_text() -> str:
    return daily_message(
        svc_get_balance(),
        svc_get_total_projected_wealth(),
    )


def daily_fire(page: ft.Page):
    message = _get_daily_fire_text()

    return ft.Container(
        padding=20,
        bgcolor="#061035",
        border_radius=12,
        content=ft.Row(
            alignment="spaceBetween",
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Daily Fire", size=18, weight="bold", color="#07ff07"),
                        ft.Text(message, size=16, color="white", italic=True),
                    ]
                ),
                ft.Container(expand=True),
                ft.Column(
                    controls=[
                        ft.Text("Projected Wealth (desktop)", color="grey", size=12)
                    ]
                ),
            ],
        ),
    )