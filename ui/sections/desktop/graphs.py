# ui/sections/desktop/graphs.py
import flet as ft
from src.services.core import svc_get_monthly_summary
from src.graphs_core import generate_chart

class GraphsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self.page = page
        self.refresh_all = refresh_all
        self.chart_image = ft.Image(src="", width=600, height=400) # Placeholder
        self.summaries = svc_get_monthly_summary()
        self.generate_chart = generate_chart()


        self.controls = [
            ft.Text("Financial Graphs", size=28, weight="bold"),
            ft.Divider(),
            self.chart_image,
            self.summaries,
            self.generate_chart,
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

        chart_src = await self.generate_chart(self)
        self.chart_image.src = chart_src
        await self.page.safe_update()