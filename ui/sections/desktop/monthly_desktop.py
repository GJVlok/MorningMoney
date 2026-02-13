# ui/sections/desktop/monthly_desktop.py
import flet as ft
from ui.components.monthly_summary import monthly_summary_table  # Desktop table

class MonthlyTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self._page = page
        self.refresh_all = refresh_all
        self.future_content = ft.Column()  # Placeholder for future additions
        self._build()

    def _build(self):
        self.controls = [
            ft.Text("Monthly Summaries", size=28, weight="bold"),
            ft.Divider(),
            monthly_summary_table(),  # Always on top
            self.future_content,  # Add stuff here later (e.g., charts, filters)
        ]

    async def refresh(self):
        self._build()  # Rebuild to refresh summary
        await self._page.safe_update()
