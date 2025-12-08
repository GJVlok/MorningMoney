import flet as ft
from ui.components.new_entry_form import new_entry_form

class NewEntryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True)
        self.page = page
        self.refresh_all = refresh_all
        self.controls = []
        self._initialize_form()

    def _initialize_form(self):
        self.controls.append(new_entry_form(self.page, self.refresh_all, variant="web"))

    async def refresh(self):
        self.controls.clear()
        self._initialize_form()
        await self.page.safe_update()
