# ui/sections/mobile/graphs.py
import flet as ft
from src.services.core import svc_get_monthly_summary

class GraphsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self.page = page
        self.refresh_all = refresh_all
        self.chart_placeholder = ft.Text("Chart will go here (e.g., Matplotlib image)")

        self.controls = [
            ft.Text("Financial Graphs", size=28, weight="bold"),
            ft.Divider(),
            self.chart_placeholder,  # Replace with real graph later
        ]

    async def refresh(self):
        summaries = svc_get_monthly_summary()
        # TODO: Generate chart (e.g., use code_execution to plot)
        # For now: self.chart_placeholder.value = f"Data: {summaries}"
        await self.page.safe_update()