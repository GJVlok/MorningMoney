# ui/sections/desktop/investments_desktop.py
import flet as ft
from src.services.core import svc_get_investments
from ui.components.investment_card import investment_card
from ui.components.investment_form import investment_form

class InvestmentsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self._page = page
        self.refresh_all = refresh_all
        self.container = ft.Column(scroll="auto")
        self._build()

    def _build(self):
        self.controls = [
            ft.Text("Investments & Retirement", size=28, weight="bold"),
            self.container,
        ]

    async def refresh(self):
        self.container.controls.clear()

        investments = svc_get_investments()
        if not investments:
            self.container.controls.append(
                ft.Text("No investments yet!", italic=True, color="grey")
            )

        for inv in investments:
            self.container.controls.append(
                investment_card(inv, self.page, self.refresh_all)
            )

        await self._page.safe_update()
