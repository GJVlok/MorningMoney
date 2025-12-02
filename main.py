# main.py
import flet as ft
import asyncio
from controls.common import init_page_extensions
from ui.tabs import NewEntryTab, DiaryTab, InvestmentsTab, SettingsTab
from controls.desktop import build_desktop_ui
from controls.mobile import build_mobile_ui

async def main(page: ft.Page):
    page.title = "MorningMoney"
    page.theme_mode = "dark"

    # Initialize helpers on page
    init_page_extensions(page)

    # Create tab instances (refresh_all will be attached next)
    new_entry_tab = NewEntryTab(page, None)
    diary_tab = DiaryTab(page, None)
    investments_tab = InvestmentsTab(page, None)
    settings_tab = SettingsTab(page, None)

    async def refresh_all():
        # canonical refresh sequence (explicit)
        if hasattr(new_entry_tab, "refresh"):
            await new_entry_tab.refresh()
        if hasattr(diary_tab, "refresh"):
            await diary_tab.refresh()
        if hasattr(investments_tab, "refresh"):
            await investments_tab.refresh()
        if hasattr(settings_tab, "refresh"):
            await settings_tab.refresh()
        await page.safe_update()

    # attach refresh_all to tabs so components can call it
    for t in (new_entry_tab, diary_tab, investments_tab, settings_tab):
        t.refresh_all = refresh_all

    # Layout decision (honour session overrides)
    force_desktop = page.session.get("force_desktop") or False
    force_mobile = page.session.get("force_mobile") or False

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
        use_desktop = is_real_desktop()

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

    # initial load
    await refresh_all()

ft.app(target=main)
