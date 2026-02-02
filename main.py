# main.py
import flet as ft
import asyncio

from controls.common import init_page_extensions
from controls.desktop import build_desktop_ui
from controls.mobile import build_mobile_ui
from controls.web import build_web_ui


CLIENT_ID = "Admin"
CLIENT_SECRET = "Secret"

async def main(page: ft.Page):
    page.title = "MorningMoney"
    page.theme_mode = "dark"

        # ---- platform detection ----

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
            from ui.sections.web.settings import SettingsTab
            platform = "web"
        else:
            from ui.sections.desktop.new_entry import NewEntryTab
            from ui.sections.desktop.diary import DiaryTab
            from ui.sections.desktop.investments import InvestmentsTab
            from ui.sections.desktop.settings import SettingsTab
            platform = "desktop"
    else:
        from ui.sections.mobile.new_entry import NewEntryTab
        from ui.sections.mobile.diary import DiaryTab
        from ui.sections.mobile.investments import InvestmentsTab
        from ui.sections.mobile.settings import SettingsTab
        platform = "mobile"

        # ---- create tabs ----

        new_entry_tab = NewEntryTab(page, None)
        diary_tab = DiaryTab(page, None)
        investments_tab = InvestmentsTab(page, None)
        settings_tab = SettingsTab(page, None)

        tabs = [new_entry_tab, diary_tab, investments_tab, settings_tab]

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

        if platform == "web":
            page.window.width = 1200
            page.window.height = 800
            build_web_ui(page, *tabs)

        elif platform == "desktop":
            page.window.width = 1200
            page.window.height = 800
            page.window.center()
            build_desktop_ui(page, *tabs)

        else:  # mobile
            page.window.width = 480
            page.window.height = 900
            build_mobile_ui(page, *tabs)
            page.route = "/diary"

        page.run_task(refresh_all)

        # ---- create tabs ----

        new_entry_tab = NewEntryTab(page, None)
        diary_tab = DiaryTab(page, None)
        investments_tab = InvestmentsTab(page, None)
        settings_tab = SettingsTab(page, None)

        tabs = [new_entry_tab, diary_tab, investments_tab, settings_tab]

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

        if platform == "web":
            page.window.width = 1200
            page.window.height = 800
            build_web_ui(page, *tabs)

        elif platform == "desktop":
            page.window.width = 1200
            page.window.height = 800
            page.window.center()
            build_desktop_ui(page, *tabs)

        else:  # mobile
            page.window.width = 480
            page.window.height = 900
            build_mobile_ui(page, *tabs)
            page.route = "/diary"

        page.run_task(refresh_all)
        page.show_snack(f"Welcome back, {page.auth.user.email or 'friend'}!", "green")


ft.app(target=main)
