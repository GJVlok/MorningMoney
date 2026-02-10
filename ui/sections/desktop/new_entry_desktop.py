# ui/sections/desktop/new_entry_desktop.py
import flet as ft
from ui.components.new_entry_form import new_entry_form
from ui.components.investment_form import investment_form

class NewEntryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True)
        self.page = page
        self.refresh_all = refresh_all
        self._build()

    def _build(self):
        self.controls = [
            ft.Text("Add Transaction", size=28, weight="bold"),
            new_entry_form(self.page, self.refresh_all),
            ft.Divider(height=20, color="transparent"),
            ft.Text("Add Investment", size=28, weight="bold"),
            investment_form(self.page, self.refresh_all),
        ]

    async def refresh(self):
        self._build()
        await self.page.safe_update()