# ui/sections/desktop/diary.py
import flet as ft
import asyncio
from src.services.core import svc_get_transactions_with_running_balance
from ui.components.transaction_tile import transaction_tile
from ui.components.monthly_summary import monthly_summary_table

class DiaryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self.page = page
        self.refresh_all = refresh_all
        self.list = ft.Column(expand=True, scroll="auto")
        self.summary_table = monthly_summary_table()

        self.controls = [
            ft.Text("Recent Transactions", size=28, weight="bold"),
            ft.Divider(),
            self.list,
            ft.Text("Monthly Summaries", size=28, weight="bold"),
            self.summary_table,
        ]

    async def refresh(self):
        # 1 Show spinner and clear old items
        self.list.controls = [
            ft.Container(
                content=ft.ProgressRing(),
                alignment=ft.alignment.center,
                padding=20
            )
        ]
        await self.page.safe_update()
        # 2. Fetch data (offloaded to a thread to keep the spinner moving)
        # This prevents the UI from freezing during the database/API call
        data = await asyncio.to_thread(svc_get_transactions_with_running_balance)
        data = data[:100]
        # 3 Build the new List
        if not data:
            new_controls = [ft.Text("No transactions found.", size=16, italic=True)]
        else:
            new_controls = [
                transaction_tile(
                    item["transaction"],
                    self.page,
                    self.refresh_all,
                    item["running_balance"]
                ) for item in data
            ]
        # 4 Update both the list and the summary table
        self.list.controls = new_controls
        # Clear the old rows and replace the summary table component
        self.summary_table.rows.clear()
        self.controls[-1] = monthly_summary_table()
        # Final single update to push all changes to the UI
        await self.page.safe_update()