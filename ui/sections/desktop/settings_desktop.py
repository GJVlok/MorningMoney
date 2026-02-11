# ui/sections/desktop/settings_desktop.py
import flet as ft
from ui.components.settings import settings_dev_tools

class SettingsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(expand=True, scroll="auto")
        self.page = page
        self.refresh_all = refresh_all

        self.controls = [
            ft.Text("Settings", size=32, weight="bold"),
            ft.Divider(height=20, color="transparent"),
            settings_dev_tools(page, refresh_all),
        ]

    async def refresh(self):
        await self.page.safe_update()