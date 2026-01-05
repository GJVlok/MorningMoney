# ui/blocks/daily_fire/daily_fire.py
import flet as ft
from src.motivation import daily_message
from src.services.core import svc_get_balance, svc_get_total_projected_wealth

def daily_fire_desktop(page: ft.Page):
    return ft.Container(
        padding=20,
        bgcolor="#061035",
        border_radius=12,
        content=ft.Row([
            ft.Column([
                ft.Text("Daily Fire", size=18, weight="bold", color="#07ff07"),
                ft.Text(daily_message(svc_get_balance(), svc_get_total_projected_wealth()), size=16, color="white", italic=True),
            ]),
            ft.Container(expand=True),
            # extra desktop info — projected wealth snippet
            ft.Column([
                ft.Text("Projected Wealth (desktop)", color="grey", size=12)
            ])
        ], alignment="spaceBetween"),
    )


def daily_fire_mobile(page: ft.Page):
    return ft.Container(
        padding=14,
        bgcolor="#061035",
        border_radius=12,
        content=ft.Column([
            ft.Text("Daily Fire", size=16, weight="bold", color="#07ff07"),
            ft.Text(daily_message(svc_get_balance(), svc_get_total_projected_wealth()), size=14, color="white", italic=True),
        ])
    )


def daily_fire_web(page: ft.Page):
    return ft.Container(
        padding=18,
        bgcolor="#061035",
        border_radius=12,
        content=ft.Row([
            ft.Column([
                ft.Text("Daily Fire", size=18, weight="bold", color="#07ff07"),
                ft.Text(daily_message(svc_get_balance(), svc_get_total_projected_wealth()), size=16, color="white", italic=True),
            ]),
        ]),
    )
