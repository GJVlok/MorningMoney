# main.py
import flet as ft
import asyncio
from controls.common import splash, init_page_extensions
from ui.tabs import NewEntryTab, DiaryTab, InvestmentsTab, SettingsTab
from controls.desktop import build_desktop_ui
from controls.mobile import build_mobile_ui


async def main(page: ft.Page):
    page.title = "MorningMoney"
    page.theme_mode = "dark"

    # Reliable desktop detection (works even if Flet says "web")
    def is_desktop():
        return (
            page.platform in ("windows", "macos", "linux") or
            page.window.width > 800 or
            page.window.height > 900
        )

    # Window settings
    page.window.min_width = 400
    page.window.resizable = True
    page.window.center()

    init_page_extensions(page)
    await splash(page)

    async def refresh_all():
        await asyncio.gather(
            diary_tab.refresh(),
            investments_tab.refresh(),
        )
        if hasattr(page, "balance_updater"):
            page.balance_updater()

    # Create all tabs
    new_entry_tab = NewEntryTab(page, refresh_all)
    diary_tab = DiaryTab(page, refresh_all)
    investments_tab = InvestmentsTab(page, refresh_all)
    settings_tab = SettingsTab(page, refresh_all)

    # Check for forced desktop mode from settings
    force_desktop = page.session.get("force_desktop") or False

    # FINAL DECISION
    use_desktop = force_desktop or is_desktop()

    if use_desktop:
        # Desktop layout — wide window + tabs including Settings
        page.window.width = 1200
        page.window.height = 800
        page.window.center()
        build_desktop_ui(page, new_entry_tab, diary_tab, investments_tab, settings_tab)
    else:
        # Mobile layout — but now includes Settings tab!
        build_mobile_ui(page, new_entry_tab, diary_tab, investments_tab, settings_tab)
        page.route = "/diary"  # default view

    await refresh_all()
    page.update()


ft.app(target=main)