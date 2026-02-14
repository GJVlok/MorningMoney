# ui/sections/desktop/investments_desktop.py
import flet as ft
from decimal import Decimal
from src.services.core import svc_get_investments, svc_get_total_projected_wealth
from ui.components.investment_card import investment_card
from ui.components.investment_form import investment_form


class InvestmentsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
        )
        self.page = page
        self.refresh_all = refresh_all

        # Header + summary row
        self.header = ft.Text("Investments & Retirement", size=28, weight=ft.FontWeight.BOLD)
        self.total_projected = ft.Text("", size=18, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_300)
        self.add_button = ft.ElevatedButton(
            "Add New Investment",
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            bgcolor="#94d494",
            color=ft.Colors.BLACK,
            on_click=self._open_add_form,
        )

        self.summary_row = ft.Row(
            [self.total_projected, ft.Container(expand=True), self.add_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Scrollable list of cards
        self.cards_container = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)

        self.controls = [
            self.header,
            self.summary_row,
            ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
            self.cards_container,
        ]

        # Initial load
        self.page.run_task(self.refresh)

    async def refresh(self):
        """Reload investments + update summary"""
        self.cards_container.controls.clear()

        investments = svc_get_investments()

        if not investments:
            self.cards_container.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.SAVINGS_OUTLINED, size=64, color=ft.Colors.GREY_500),
                            ft.Text("No investments tracked yet", size=18, color=ft.Colors.GREY_400),
                            ft.Text("Add your first one to start seeing projections!", italic=True, color=ft.Colors.GREY_600),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                )
            )
        else:
            for inv in investments:
                self.cards_container.controls.append(
                    investment_card(inv, self.page, self.refresh_all)
                )

        # Update total projected wealth
        total = svc_get_total_projected_wealth()
        self.total_projected.value = (
            f"Total Projected Wealth: R{total:,.0f}"
            if total > 0
            else "Start adding investments to see your future wealth grow!"
        )
        self.total_projected.color = ft.Colors.GREEN_300 if total >= Decimal("1000000") else ft.Colors.GREY_300

        await self.page.safe_update()

    def _open_add_form(self, e):
        """Open the investment form in a dialog (using the improved version)"""
        form = investment_form(self.page, self.refresh_all)  # no existing_inv = add mode

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add New Investment"),
            content=form,
            actions=[
                ft.TextButton("Close", on_click=lambda _: self.page.close(dialog)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12),
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()