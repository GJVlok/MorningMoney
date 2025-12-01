# main.py
import flet as ft
import asyncio
from controls.common import splash, init_page_extensions
from ui.tabs import NewEntryTab, DiaryTab, InvestmentsTab
from controls.desktop import build_desktop_ui
from controls.mobile import build_mobile_ui


async def main(page: ft.Page):
    page.title = "MorningMoney"
    page.theme_mode = "dark"
    page.padding = 20 if page.platform in ("windows", "macos", "linux") else 10
    page.window.width = 500
    page.window.height = 900
    page.window.min_width = 400
    page.window.resizable = True
    page.window.center()

    init_page_extensions(page)
    await splash(page)

    # Shared refresh
    async def refresh_all():
        await asyncio.gather(
            diary_tab.refresh(),
            investments_tab.refresh(),
        )
        if hasattr(page, "balance_updater"):
            page.balance_updater()

    # Create tabs
    new_entry_tab = NewEntryTab(page, refresh_all)
    diary_tab = DiaryTab(page, refresh_all)
    investments_tab = InvestmentsTab(page, refresh_all)

    # Choose platform
    if page.platform in ("android", "ios"):
        build_mobile_ui(page, new_entry_tab, diary_tab, investments_tab)
        page.route = "/diary"
    else:
        build_desktop_ui(page, new_entry_tab, diary_tab, investments_tab)

    await refresh_all()


ft.app(target=main)