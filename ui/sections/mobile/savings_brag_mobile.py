# ui/sections/desktop/savings_brag_desktop.py
import flet as ft
from src.services.core import svc_get_total_saved
from controls.common import money_text

class SavingsBragTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self._page = page
        self.refresh_all = refresh_all
        self._build()

    def _build(self):
        total_saved = svc_get_total_saved()
        brag_text = ft.Text("Keep hunting those deals—your savings are growing!" if total_saved > 0 else "Start tracking discounts to build your brag rights!", italic=True)

        self.controls = [
            ft.Text("Savings Brag Rights", size=24, weight="bold"),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    money_text(total_saved, size=48),
                    brag_text,
                ], alignment="center", horizontal_alignment="center"),
                expand=True,
                alignment=ft.Alignment.CENTER,
            ),
            # Future: List of top savings transactions
        ]

    async def refresh(self):
        self._build()
        await self._page.safe_update()
