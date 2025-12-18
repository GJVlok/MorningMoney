# ui/sections/mobile/diary.py
import flet as ft
from src.services.core import svc_get_transactions_with_running_balance
from ui.components.transaction_tile import transaction_tile

class DiaryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self.page = page
        self.refresh_all = refresh_all
        self.list = ft.Column(expand=True, scroll="auto")

        self.controls = [
            ft.Text("Recent Transactions", size=24, weight="bold"),
            ft.Divider(),
            self.list,
        ]

    async def refresh(self):
        self.list.controls.clear()
        for item in svc_get_transactions_with_running_balance()[:100]:
            self.list.controls.append(
                transaction_tile(
                    item["transaction"],
                    self.page,
                    self.refresh_all,
                    item["running_balance"],
                    variant="mobile",
                )
            )
        await self.page.safe_update()