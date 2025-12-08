import flet as ft
from src.services.core import svc_get_transactions_with_running_balance
from ui.components.transaction_tile import transaction_tile

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
        data = svc_get_transactions_with_running_balance()
        self.list.controls.clear()
        for item in data[:100]:
            t = item["transaction"]
            running_balance = item["running_balance"]
            tile = transaction_tile(t, self.page, self.refresh_all, running_balance, variant="desktop")
            self.list.controls.append(tile)
        await self.page.safe_update()
