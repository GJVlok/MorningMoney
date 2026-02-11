# ui/sections/desktop/monthly_mobile.py
import flet as ft
from ui.components.monthly_summary import monthly_summary_mobile  # Desktop table

class MonthlyTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self.page = page
        self.refresh_all = refresh_all
        self.future_content = ft.Column()  # Placeholder for future additions
        self._build()

    def _build(self):
        self.controls = [
            ft.Text("Monthly Summaries", size=24, weight="bold"),
            ft.Divider(),
            monthly_summary_mobile(),  # Always on top
            self.future_content,  # Add stuff here later (e.g., charts, filters)
        ]

    async def refresh(self):
        self._build()  # Rebuild to refresh summary
        await self.page.safe_update()