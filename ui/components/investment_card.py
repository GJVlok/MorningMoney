# ui/components/investment_card.py
import flet as ft
from src.database import Investment
from ui.dialogs import edit_investment_dialog, delete_investment
from src.services.core import svc_calculate_future_value

def _mobile_investment_menu(inv: Investment, page: ft.Page, refresh_all):
    def handler(e):
        bs = ft.BottomSheet(
            ft.Container(
                ft.Column([
                    ft.ListTile(leading=ft.Icon(ft.Icons.EDIT, color="blue"), title=ft.Text("Edit"), on_click=lambda _: (page.run_task(edit_investment_dialog, page, inv, refresh_all), setattr(bs, "open", False), page.update())),
                    ft.ListTile(leading=ft.Icon(ft.Icons.DELETE, color="red"), title=ft.Text("Delete", color="red"), on_click=lambda _: (page.run_task(delete_investment, page, inv, refresh_all), setattr(bs, "open", False), page.update())),
                ], tight=True, spacing=10),
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


def investment_card(investment: Investment, page: ft.Page, refresh_all, variant="desktop") -> ft.Control:
    fv = svc_calculate_future_value(investment)

    content = ft.Column([
        ft.Text(investment.name, size=22, weight="bold", color="white"),
        ft.Text(f"Current: R{investment.current_value:,.0f}  •  +R{investment.monthly_contribution:,.0f}/mo @ {investment.expected_annual_return}%", color="grey"),
        ft.Divider(color="grey"),
        ft.Text("Projected", color="#00ff88"),
        ft.Text(f"R{fv:,.0f}", size=34, weight="bold", color="#00ff88"),
        ft.Text(f"R{fv/1_000_000:.2f} million {'FIRE!' if fv >= 10_000_000 else 'on track'}", color="#00ff88" if fv >= 10_000_000 else "orange", italic=True)
    ], spacing=8)

    if variant == "desktop" or variant == "web":
        return ft.Card(
            elevation=8,
            content=ft.Container(
                content=ft.Row([
                    ft.Container(content, padding=20, expand=True),
                    ft.Column([
                        ft.IconButton(ft.Icons.EDIT, tooltip="Edit", on_click=lambda e: page.run_task(edit_investment_dialog, page, investment, refresh_all)),
                        ft.IconButton(ft.Icons.DELETE, tooltip="Delete", on_click=lambda e: page.run_task(delete_investment, page, investment, refresh_all)),
                    ], spacing=4),
                ], alignment="spaceBetween"),
                bgcolor="#1e1e2e",
                border_radius=12,
                padding=10
            )
        )

    # mobile
    return ft.Card(
        elevation=6,
        content=ft.Container(content=content, padding=20, bgcolor="#1e1e2e", border_radius=12, on_click=_mobile_investment_menu(investment, page, refresh_all)),
        margin=8
    )
