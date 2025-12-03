# ui/tabs.py
import flet as ft
from src.services.transactions import get_all_transactions
from src.services.investments import get_investments
from ui.components.transaction_tile import transaction_tile
from ui.components.investment_card import investment_card
from ui.components.new_entry_form import new_entry_form
from ui.components.investment_form import investment_form
from ui.components.settings_dev_tools import settings_dev_tools

class NewEntryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True)
        self.page = page
        self.refresh_all = refresh_all
        self.controls = []
        self._initialize_form()

    def _initialize_form(self):
        self.controls.append(new_entry_form(self.page, self.refresh_all))

    async def refresh(self):
        self.controls.clear()
        self._initialize_form()
        await self.page.safe_update()

class DiaryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(scroll="auto", expand=True)
        self.page = page
        self.refresh_all = refresh_all
        self.list = ft.Column(scroll="auto", expand=True)
        self.controls = [
            ft.Text("Recent Transactions", size=28, weight="bold"),
            ft.Divider(),
            self.list,
        ]

    async def refresh(self):
        transactions = get_all_transactions()[:100]
        self.list.controls.clear()
        for t in transactions:
            self.list.controls.append(transaction_tile(t, self.page, self.refresh_all))
        await self.page.safe_update()

class InvestmentsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(scroll="auto", expand=True)
        self.page = page
        self.refresh_all = refresh_all
        self.container = ft.Column(scroll="auto")
        self.controls = [
            ft.Text("Investments & Retirement", size=28, weight="bold"),
            self.container,
        ]

    async def refresh(self):
        self.container.controls.clear()
        investments = get_investments()
        if not investments:
            self.container.controls.append(ft.Text("No investments yet!", italic=True, color="grey"))
        for inv in investments:
            self.container.controls.append(investment_card(inv, self.page, self.refresh_all))
        self.container.controls.append(investment_form(self.page, self.refresh_all))
        await self.page.safe_update()

class SettingsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self.page = page
        self.refresh_all = refresh_all
        self.controls = [
            ft.Text("Settings", size=32, weight="bold"),
            ft.Divider(height=20, color="transparent"),
            settings_dev_tools(page, refresh_all),
        ]

    async def refresh(self):
        await self.page.safe_update()
