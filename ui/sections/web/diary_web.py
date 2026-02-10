# ui/sections/web/diary_web.py
import flet as ft
import asyncio
from datetime import date
from src.services.core import (
    svc_get_transactions_with_running_balance,
    svc_get_transactions_with_running_balance_date_to_date
)
from ui.components.transaction_tile import transaction_tile
from ui.components.monthly_summary import monthly_summary_table

class DiaryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self.page = page
        self.refresh_all = refresh_all
        self.list = ft.Column(expand=True, scroll="auto")
        self.summary_table = monthly_summary_table()
        self.from_date = ft.TextField(label="From Date (YYYY-MM-DD)", value="")
        self.to_date = ft.TextField(label="To Date (YYYY-MM-DD)", value="")
        self.filter_btn = ft.ElevatedButton("Filter", on_click=lambda _: self.page.run_task(self.refresh))

        self.controls = [
            ft.Text("Recent Transactions", size=28, weight="bold"),
            ft.Divider(),
            ft.Row([self.from_date, self.to_date, self.filter_btn]),
            self.list,
            ft.Text("Monthly Summaries", size=28, weight="bold"),
            self.summary_table,
        ]

    async def refresh(self):
        self.list.controls = [
            ft.Container(
                content=ft.ProgressRing(),
                alignment=ft.alignment.center,
                padding=20
            )
        ]
        await self.page.safe_update()

        from_d, to_d = None, None
        if self.from_date.value or self.to_date.value:
            try:
                if self.from_date.value:
                    from_d = date.fromisoformat(self.from_date.value)
                if self.to_date.value:
                    to_d = date.fromisoformat(self.to_date.value)
            except ValueError:
                await self.page.show_snack("Invalid date format (use YYYY-MM-DD)", "red")
                self.from_date.value = ""
                self.to_date.value = ""
                await self.page.safe_update()
                return

        data = await asyncio.to_thread(
            svc_get_transactions_with_running_balance_date_to_date, from_d, to_d
            )
        data = data[:100]

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
 
        self.list.controls = new_controls
        self.summary_table.rows.clear()
        self.controls[-1] = monthly_summary_table()
        await self.page.safe_update()