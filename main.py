# main.py
import flet as ft
import asyncio

from controls.common import init_page_extensions
from controls.desktop import build_desktop_ui

async def build_main_ui(page: ft.Page):
    page.clean()

    # ---- platform detection ---- (move your existing detection code here)
    force_desktop = page.session.get("force_desktop") or False
    force_mobile = page.session.get("force_mobile") or False

    def is_real_desktop():
        return (
            page.platform in ("windows", "macos", "linux")
            or (getattr(page, "window", None) and page.window.width > 800)
            or (getattr(page, "window", None) and page.window.height > 900)
        )

    if force_desktop:
        use_desktop = True
    elif force_mobile:
        use_desktop = False
    else:
        use_desktop = page.platform != "mobile" and is_real_desktop()

    # ---- import correct tab classes ----
    if use_desktop:
        if page.platform == "web":
            from ui.sections.web.new_entry import NewEntryTab
            from ui.sections.web.diary import DiaryTab
            from ui.sections.web.investments import InvestmentsTab
            from ui.sections.web.graphs import GraphsTab
            from ui.sections.web.settings import SettingsTab
            platform_name = "web"
        else:
            from ui.sections.desktop.new_entry import NewEntryTab
            from ui.sections.desktop.diary import DiaryTab
            from ui.sections.desktop.investments import InvestmentsTab
            from ui.sections.desktop.graphs import GraphsTab
            from ui.sections.desktop.settings import SettingsTab
            platform_name = "desktop"
    else:
        from ui.sections.mobile.new_entry import NewEntryTab
        from ui.sections.mobile.diary import DiaryTab
        from ui.sections.mobile.investments import InvestmentsTab
        from ui.sections.mobile.graphs import GraphsTab
        from ui.sections.mobile.settings import SettingsTab
        platform_name = "mobile"

    # ---- create tabs ----
    new_entry_tab = NewEntryTab(page, None)
    diary_tab = DiaryTab(page, None)
    investments_tab = InvestmentsTab(page, None)
    graphs_tab = GraphsTab(page, None)
    settings_tab = SettingsTab(page, None)

    tabs = [new_entry_tab, diary_tab, investments_tab, graphs_tab, settings_tab]

    # ---- refresh coordinator ----
    async def refresh_all():
        if hasattr(page, "balance_updater"):
            page.balance_updater()
        for t in tabs:
            if hasattr(t, "refresh"):
                await t.refresh()
        await page.safe_update()

    for t in tabs:
        t.refresh_all = refresh_all

    # ---- build platform UI ----
    if platform_name == "web":
        page.window.width = 1200
        page.window.height = 800
    elif platform_name == "desktop":
        page.window.width = 1200
        page.window.height = 800
        page.window.center()
        build_desktop_ui(page, *tabs)
    else:  # mobile
        page.window.width = 480
        page.window.height = 900
        page.route = "/diary"

    page.run_task(refresh_all)

    # # Optional: show username in header later
    # await page.show_snack(f"Welcome, {page.session.get('username') or 'friend'}!", "green")

async def main(page: ft.Page):
    page.title = "MorningMoney"
    page.theme_mode = "dark"

    init_page_extensions(page)

    await build_main_ui(page)

if __name__ == "__main__":
    ft.app(target=main)
