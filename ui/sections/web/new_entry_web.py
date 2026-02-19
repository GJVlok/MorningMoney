# ui/sections/web/new_entry_web.py
import flet as ft
from ui.components.new_entry_form import new_entry_form
from ui.components.investment_form import investment_form

class NewEntryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(
            expand=True,
            scroll="auto",
            spacing=20,
            )
        self._page = page
        self.refresh_all = refresh_all
        self._build()

    def _build(self):
        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text("Add Transaction", size=28, weight="bold"),
                    new_entry_form(self._page, self.refresh_all),
                ]),
                padding=20,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
                border_radius=12,
            ),

            ft.Divider(height=30, color="transparent"),

            ft.Container(
                content=ft.Column([
                    ft.Text("Add Investment", size=28, weight="bold"),
                    investment_form(self._page, self.refresh_all),
                ]),
                padding=20,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
                border_radius=12,
            ),
        ]

    async def refresh(self):
        self._build()
        await self._page.safe_update()
