# ui/sections/web/graphs.py
import flet as ft
from src.services.core import svc_get_monthly_summary
from src.graphs_core import generate_chart

class GraphsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self.page = page
        self.refresh_all = refresh_all
        self.chart_image = ft.Image(src="", width=600, height=400, fit=ft.ImageFit.CONTAIN) # Placeholder
        self.summary_view = ft.Text("Loading...", italic=True)

        self.controls = [
            ft.Text("Financial Graphs", size=28, weight="bold"),
            ft.Divider(),
            self.chart_image,
            self.summary_view,
        ]

    async def refresh(self):
        # Show loading
        self.controls[-1] = ft.ProgressRing()
        await self.page.safe_update()

        # Get data
        summaries = svc_get_monthly_summary()

        # Generate chart (now awaited properly!)
        chart_src = await generate_chart(self) # note: no self. prefix here

        # Update UI
        self.chart_image.src = chart_src

        # Replace loading text with actual summary (you can make a nice table later)
        if summaries:
            self.summary_view.value = f"Last month: Income R{summaries[0]['income']:,.0f}"
        else:
            self.summary_view.value = "No data yet"

        await self.page.safe_update()