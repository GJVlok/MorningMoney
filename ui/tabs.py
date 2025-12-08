# ui/tabs.py
import flet as ft
from src.services.core import (
    svc_get_all_transactions,
    svc_get_investments,
    svc_get_transactions_with_running_balance
)
from ui.components.transaction_tile import transaction_tile
from ui.components.investment_card import investment_card
from ui.components.new_entry_form import new_entry_form
from ui.components.investment_form import investment_form
from ui.components.settings_dev_tools import settings_dev_tools
from controls.common import is_currently_desktop


class BaseTab(ft.Column):
    """Base class to provide platform variant detection."""
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True)
        self.page = page
        self.refresh_all = refresh_all
        self.variant = self._detect_variant()

    def _detect_variant(self):
        if is_currently_desktop(self.page):
            return "desktop"
        elif self.page.platform == "web":
            return "web"
        else:
            return "mobile"


class NewEntryTab(BaseTab):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(page, refresh_all)
        self.controls = []
        self._initialize_form()

    def _initialize_form(self):
        self.controls.append(new_entry_form(self.page, self.refresh_all))

    async def refresh(self):
        self.controls.clear()
        self._initialize_form()
        await self.page.safe_update()


class DiaryTab(BaseTab):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(page, refresh_all)
        self.list = ft.Column(scroll="auto", expand=True)
        self.controls = [
            ft.Text("Recent Transactions", size=28, weight="bold"),
            ft.Divider(),
            self.list
        ]

    async def refresh(self):
        data = svc_get_transactions_with_running_balance()
        self.list.controls.clear()

        for item in data[:100]:
            t = item["transaction"]
            running_balance = item["running_balance"]
            tile = transaction_tile(
                t,
                self.page,
                self.refresh_all,
                running_balance,
                variant=self.variant
            )
            self.list.controls.append(tile)

        await self.page.safe_update()


class InvestmentsTab(BaseTab):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(page, refresh_all)
        self.container = ft.Column(scroll="auto")
        self.controls = [
            ft.Text("Investments & Retirement", size=28, weight="bold"),
            self.container
        ]

    async def refresh(self):
        self.container.controls.clear()
        investments = svc_get_investments()
        if not investments:
            self.container.controls.append(ft.Text("No investments yet!", italic=True, color="grey"))
        for inv in investments:
            self.container.controls.append(
                investment_card(inv, self.page, self.refresh_all, variant=self.variant)
            )
        self.container.controls.append(investment_form(self.page, self.refresh_all))
        await self.page.safe_update()


class SettingsTab(BaseTab):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(page, refresh_all)
        self.controls = [
            ft.Text("Settings", size=32, weight="bold"),
            ft.Divider(height=20, color="transparent"),
            settings_dev_tools(page, refresh_all)
        ]

    async def refresh(self):
        await self.page.safe_update()
