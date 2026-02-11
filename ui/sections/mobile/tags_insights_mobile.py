# ui/sections/mobile/tags_insights_mobile.py
import flet as ft
from src.services.core import svc_get_tag_summary  # New service wrapper

class TagsInsightsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self.page = page
        self.refresh_all = refresh_all
        self._build()

    def _build(self):
        summaries = svc_get_tag_summary()  # Fetch
        # Build table or list of tag: total
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tag")),
                ft.DataColumn(
                    ft.Text("Total Amount"),
                    numeric=True
                ),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["tag"])),
                        ft.DataCell(ft.Text(f"R{item["total"]:,.2f}")),
                    ],
                ) for item in summaries
            ]
        )  # Similar to monthly_summary
        self.controls = [
            ft.Text("Tags & Insights", size=28, weight="bold"),
            ft.Divider(),
            table,
            # Future: Graphs, comparisons (e.g., shop pie)
        ]

    async def refresh(self):
        self._build()
        await self.page.safe_update()