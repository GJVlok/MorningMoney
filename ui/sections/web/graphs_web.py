# ui/sections/web/graphs_web.py
import flet as ft

class GraphsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self._page = page
        self.refresh_all = refresh_all
        self._build()

    def _build(self):
        self.controls = [
            ft.Text("Financial Graphs", size=28, weight="bold"),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.BAR_CHART, size=80, color="grey"),
                    ft.Text("Graphs Coming Soon!", size=24, weight="bold", color="orange"),
                    ft.Text("We're building visualizations for your income, expenses, and trends. Stay tuned!", 
                            size=16, italic=True, text_align="center"),
                ], alignment="center", horizontal_alignment="center"),
                expand=True,
                alignment=ft.Alignment.CENTER,
            ),
        ]

    async def refresh(self):
        self._build()  # Rebuild if needed
        await self._page.safe_update()
