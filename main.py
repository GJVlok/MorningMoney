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
# --- LAYOUT DECISION LOGIC ---
    force_desktop = page.session.get("force_desktop") or False
    force_mobile = page.session.get("force_mobile") or False

    def is_real_desktop():
        return (
            page.platform in ("windows", "macos", "linux") or
            (page.window.width and page.window.width > 800) or
            (page.window.height and page.window.height > 900)
        )

    # Priority: manual override > auto detection
    if force_desktop:
        use_desktop = True
    elif force_mobile:
        use_desktop = False
    else:
        use_desktop = is_real_desktop()

    # Apply layout
    if use_desktop:
        page.window.width = 1200
        page.window.height = 800
        page.window.center()
        build_desktop_ui(page, new_entry_tab, diary_tab, investments_tab, settings_tab)
    else:
        page.window.width = 480
        page.window.height = 900
        build_mobile_ui(page, new_entry_tab, diary_tab, investments_tab, settings_tab)
        page.route = "/diary"

    await refresh_all()
    page.update()


ft.app(target=main)