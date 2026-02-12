# main.py
import flet as ft
import asyncio
import matplotlib; matplotlib.use('Agg')
import logging

from controls.common import init_page_extensions
from controls.desktop import build_desktop_ui
from ui.utils.theme import get_color_scheme

# logging.basicConfig(level=config.LOG_LEVEL)

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
            from ui.sections.web.new_entry_web import NewEntryTab
            from ui.sections.web.diary_web import DiaryTab
            from ui.sections.web.monthly_web import MonthlyTab
            from ui.sections.web.investments_web import InvestmentsTab
            from ui.sections.web.tags_insights_web import TagsInsightsTab
            from ui.sections.web.savings_brag_web import SavingsBragTab
            from ui.sections.web.graphs_web import GraphsTab
            from ui.sections.web.settings_web import SettingsTab
            platform_name = "web"
        else:
            from ui.sections.desktop.new_entry_desktop import NewEntryTab
            from ui.sections.desktop.diary_desktop import DiaryTab
            from ui.sections.desktop.monthly_desktop import MonthlyTab
            from ui.sections.desktop.investments_desktop import InvestmentsTab
            from ui.sections.desktop.tags_insights_desktop import TagsInsightsTab
            from ui.sections.desktop.savings_brag_desktop import SavingsBragTab
            from ui.sections.desktop.graphs_desktop import GraphsTab
            from ui.sections.desktop.settings_desktop import SettingsTab
            platform_name = "desktop"
    else:
        from ui.sections.mobile.new_entry_mobile import NewEntryTab
        from ui.sections.mobile.diary_mobile import DiaryTab
        from ui.sections.mobile.monthly_mobile import MonthlyTab
        from ui.sections.mobile.investments_mobile import InvestmentsTab
        from ui.sections.mobile.tags_insights_mobile import TagsInsightsTab
        from ui.sections.mobile.savings_brag_mobile import SavingsBragTab
        from ui.sections.mobile.graphs_mobile import GraphsTab
        from ui.sections.mobile.settings_mobile import SettingsTab
        platform_name = "mobile"

    # ---- create tabs ----
    new_entry_tab = NewEntryTab(page, None)
    diary_tab = DiaryTab(page, None)
    monthly_tab = MonthlyTab(page, None)
    investments_tab = InvestmentsTab(page, None)
    tabs_insights_tab = TagsInsightsTab(page, None)
    savings_brag_tab = SavingsBragTab(page, None)
    graphs_tab = GraphsTab(page, None)
    settings_tab = SettingsTab(page, None)

    tabs = [new_entry_tab,
            diary_tab,
            monthly_tab,
            investments_tab,
            tabs_insights_tab,
            savings_brag_tab,
            graphs_tab,
            settings_tab]

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

    await asyncio.sleep(0.1)

    try:
        saved_mode = await page.client_storage.get_async("theme_mode")
        page.theme_mode = saved_mode if saved_mode else "dark"
    except Exception as ex:
        print(f"Theme load failed (using dark)< {ex}")
        page.theme_mode = "dark"

    page.color_scheme = get_color_scheme(page.theme_mode)

    init_page_extensions(page)

    async def toggle_theme(e):
        try:
            new_mode = "light" if page.theme_mode == "dark" else "dark"
            page.theme_mode = new_mode
            page.color_scheme = get_color_scheme(new_mode)

            await page.client_storage.set_async("theme_mode", new_mode)

            await page.show_snack(f"{page.theme_mode.capitalize()} mode activated!", "#94d494")
            await page.safe_update()

        except TimeoutError:
            await page.show_snack("Theme saved, but storage timed out - try again?", "orange")
        except Exception as ex:
            print(f"Toggle theme error: {ex}")
            await page.show_snack("Couldn't save theme preference", "red")
    page.toggle_theme = toggle_theme
    await build_main_ui(page)

if __name__ == "__main__":
    ft.run(main)
