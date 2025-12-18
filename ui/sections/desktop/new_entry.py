# ui/sections/desktop/new_entry.py
import flet as ft
from ui.components.new_entry_form import new_entry_form

class NewEntryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True)
        self.page = page
        self.refresh_all = refresh_all
        self._build()

    def _build(self):
        self.controls = [
            new_entry_form(self.page, self.refresh_all, variant="desktop")
        ]

    async def refresh(self):
        self._build()
        await self.page.safe_update()