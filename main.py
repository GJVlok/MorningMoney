# main.py
import flet as ft
import asyncio
from controls.common import init_page_extensions, is_currently_desktop
from ui.tabs import NewEntryTab, DiaryTab, InvestmentsTab, SettingsTab
from controls.desktop import build_desktop_ui
from controls.mobile import build_mobile_ui
from controls.web import build_web_ui


async def main(page: ft.Page):
    page.title = "MorningMoney"
    page.theme_mode = "dark"

    # Initialize helpers on page
    init_page_extensions(page)

    # Create tab instances
    new_entry_tab = NewEntryTab(page, None)  # refresh_all will be set below
    diary_tab = DiaryTab(page, None)
    investments_tab = InvestmentsTab(page, None)
    settings_tab = SettingsTab(page, None)

    tabs = [new_entry_tab, diary_tab, investments_tab, settings_tab]

    # Define refresh_all function
    async def refresh_all():
        for t in tabs:
            if hasattr(t, "refresh"):
                await t.refresh()
        await page.safe_update()

    # Attach refresh_all to tabs
    for t in tabs:
        t.refresh_all = refresh_all

    # Detect platform and decide layout
    force_desktop = page.session.get("force_desktop", False)
    force_mobile = page.session.get("force_mobile", False)

    def is_real_desktop():
        return (
            page.platform in ("windows", "macos", "linux") or
            (getattr(page, "window", None) and getattr(page.window, "width", 0) > 800) or
            (getattr(page, "window", None) and getattr(page.window, "height", 0) > 900)
        )

    if force_desktop:
        use_desktop = True
    elif force_mobile:
        use_desktop = False
    else:
        use_desktop = page.platform != "mobile" and is_real_desktop()

    # Build layout per platform
    if use_desktop:
        if page.platform == "web":
            page.window.width = 1200
            page.window.height = 800
            build_web_ui(page, *tabs)
        else:
            page.window.width = 1200
            page.window.height = 800
            page.window.center()
            build_desktop_ui(page, *tabs)
    else:
        page.window.width = 480
        page.window.height = 900
        build_mobile_ui(page, *tabs)
        page.route = "/diary"  # default tab for mobile

    # Initial refresh
    await refresh_all()


ft.app(target=main)
