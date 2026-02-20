# main.py
import flet as ft
import logging
import matplotlib
import inspect

matplotlib.use("Agg")

from controls.common import init_page_extensions
from src.services.settings import init_theme
from ui.utils.flet_compat import pref_get, pref_set, safe_update
from ui.utils.device_detect import detect_platform

from controls.desktop import build_desktop_ui
from controls.mobile import build_mobile_ui
from controls.web import build_web_ui

from ui.sections.desktop.new_entry_desktop import NewEntryTab
from ui.sections.desktop.diary_desktop import DiaryTab
from ui.sections.desktop.monthly_desktop import MonthlyTab
from ui.sections.desktop.investments_desktop import InvestmentsTab
from ui.sections.desktop.tags_insights_desktop import TagsInsightsTab
from ui.sections.desktop.savings_brag_desktop import SavingsBragTab
from ui.sections.desktop.graphs_desktop import GraphsTab
from ui.sections.desktop.settings_desktop import SettingsTab


# ---------------- LOGGING ---------------- #

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ],
    )


# ---------------- TABS ---------------- #

def create_tabs(page, refresh_all=None):
    return [
        NewEntryTab(page, refresh_all),
        DiaryTab(page, refresh_all),
        MonthlyTab(page, refresh_all),
        InvestmentsTab(page, refresh_all),
        TagsInsightsTab(page, refresh_all),
        SavingsBragTab(page, refresh_all),
        GraphsTab(page, refresh_all),
        SettingsTab(page, refresh_all),
    ]

# ---------------- WINDOW ---------------- #

async def configure_window(page, layout_mode):
    try:
        if layout_mode == "desktop":
            page.window.width = 1280
            page.window.height = 900
            await page.window.center()

        elif layout_mode == "mobile":
            page.window.width = 400
            page.window.height = 850

    except Exception:
        pass


# ---------------- MAIN UI ---------------- #

async def build_main_ui(page: ft.Page):

    page.clean()
    page.title = "MorningMoney"

    platform_name = detect_platform(page)

    # Layout resolution
    force_desktop = pref_get(page, "force_desktop", False)
    force_mobile = pref_get(page, "force_mobile", False)

    width = page.window.width or page.width or 1200

    if force_desktop:
        layout_mode = "desktop"
    elif force_mobile:
        layout_mode = "mobile"
    else:
        layout_mode = "desktop" if width > 900 else "mobile"

    await configure_window(page, layout_mode)

    # Tabs
    tabs_list = create_tabs(page)

    # Refresh system
    async def refresh_all():

        if hasattr(page, "balance_updater"):
            try:
                page.balance_updater()
            except Exception as ex:
                logging.error(f"Balance update error: {ex}")

        for tab in tabs_list:
            if hasattr(tab, "refresh"):
                try:
                    result = tab.refresh()
                    if inspect.isawaitable(result):
                        await result
                except Exception as ex:
                    logging.error(f"Refresh error in {tab.__class__.__name__}: {ex}")

        await safe_update(page)

    tabs_list = create_tabs(page, refresh_all)

    # Platform UI
    if layout_mode == "mobile":
        page.route = "/diary"
        build_mobile_ui(page, *tabs_list)

    elif layout_mode == "desktop":
        build_desktop_ui(page, *tabs_list)

    else:
        build_web_ui(page, *tabs_list)

    # Initial refresh
    await refresh_all()

    # Welcome
    if not pref_get(page, "seen_welcome", False):
        await page.show_snack(
            "Welcome to MorningMoney! Track transactions and aim for FIRE.",
            bgcolor="#94d494",
            duration_ms=6000,
        )
        pref_set(page, "seen_welcome", True)


# ---------------- ENTRY ---------------- #

async def main(page: ft.Page):

    init_page_extensions(page)

    await init_theme(page)

    await build_main_ui(page)

if __name__ == "__main__":
    setup_logging()
    ft.run(main)
