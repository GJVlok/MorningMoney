# main.py
import flet as ft
import asyncio
import matplotlib; matplotlib.use('Agg')  # Non-interactive backend – good for server-side charts

from controls.common import init_page_extensions
from src.services.settings import init_theme
from ui.utils.flet_compat import pref_get, safe_update
from ui.utils.device_detect import detect_platform
from src.services.core import svc_get_balance  # For initial balance

# Import your platform builders (adjust paths if needed)
from controls.desktop import build_desktop_ui
from controls.mobile import build_mobile_ui
from controls.web import build_web_ui

# Import tab classes (these should match your actual file structure)
from ui.sections.desktop.new_entry_desktop import NewEntryTab
from ui.sections.desktop.diary_desktop import DiaryTab
from ui.sections.desktop.monthly_desktop import MonthlyTab
from ui.sections.desktop.investments_desktop import InvestmentsTab
from ui.sections.desktop.tags_insights_desktop import TagsInsightsTab
from ui.sections.desktop.savings_brag_desktop import SavingsBragTab
from ui.sections.desktop.graphs_desktop import GraphsTab
from ui.sections.desktop.settings_desktop import SettingsTab

# You may want mobile/web variants too – for now assuming shared tabs or conditional
# If mobile needs different tabs, import them conditionally later


async def build_main_ui(page: ft.Page):
    page.clean()
    page.title = "MorningMoney"

    # 1. Platform & layout detection (robust version)
    platform_name = detect_platform(page)

    # Force overrides from prefs (sync)
    force_desktop = pref_get(page, "force_desktop", False)
    force_mobile = pref_get(page, "force_mobile", False)

    if force_desktop:
        layout_mode = "desktop"
    elif force_mobile:
        layout_mode = "mobile"
    else:
        # Heuristic fallback
        is_wide = page.window.width > 900 if page.window else False
        layout_mode = "desktop" if platform_name in ("desktop", "web") and is_wide else "mobile"

    # 2. Set sensible window size (responsive-ish)
    try:
        if layout_mode == "desktop" or platform_name == "web":
            page.window.width = 1280
            page.window.height = 900
            page.window.center()
        elif layout_mode == "mobile":
            page.window.width = 400
            page.window.height = 850
            # No center on mobile – usually full-screen
    except Exception:
        pass  # Some platforms (web) ignore window size

    # 3. Instantiate tabs (shared across platforms for simplicity – customize per platform if needed)
    new_entry = NewEntryTab(page, None)
    diary = DiaryTab(page, None)
    monthly = MonthlyTab(page, None)
    investments = InvestmentsTab(page, None)
    tags_insights = TagsInsightsTab(page, None)
    savings_brag = SavingsBragTab(page, None)
    graphs = GraphsTab(page, None)
    settings = SettingsTab(page, None)

    tabs_list = [
        new_entry, diary, monthly, investments,
        tags_insights, savings_brag, graphs, settings
    ]

    # 4. Global refresh – calls each tab's .refresh() if exists
    async def refresh_all():
        try:
            page.balance_updater()  # Update global balance display
        except AttributeError:
            pass  # If not set yet

        for tab in tabs_list:
            if hasattr(tab, "refresh") and callable(tab.refresh):
                try:
                    await tab.refresh()
                except Exception as ex:
                    print(f"Refresh error in {tab.__class__.__name__}: {ex}")

        await safe_update(page)

    # Attach refresh_all to each tab
    for tab in tabs_list:
        tab.refresh_all = refresh_all

    # 5. Build platform-specific UI
    if layout_mode == "mobile" or platform_name == "mobile":
        page.route = "/diary"  # Default route for mobile bottom nav
        build_mobile_ui(
            page,
            new_entry_tab=new_entry,
            diary_tab=diary,
            monthly_tab=monthly,
            investments_tab=investments,
            tags_insights_tab=tags_insights,
            savings_brag_tab=savings_brag,
            graphs_tab=graphs,
            settings_tab=settings,
        )
    elif platform_name == "web" or layout_mode == "desktop":
        if platform_name == "web":
            # Web often ignores window size – but set for desktop-like feel
            pass
        else:
            await page.window.center()

        build_desktop_ui(
            page,
            new_entry_tab=new_entry,
            diary_tab=diary,
            monthly_tab=monthly,
            investments_tab=investments,
            tags_insights_tab=tags_insights,
            savings_brag_tab=savings_brag,
            graphs_tab=graphs,
            settings_tab=settings,
        )
    else:
        # Fallback: web-like tabs
        build_web_ui(
            page,
            new_entry_tab=new_entry,
            diary_tab=diary,
            monthly_tab=monthly,
            investments_tab=investments,
            tags_insights_tab=tags_insights,
            savings_brag_tab=savings_brag,
            graphs_tab=graphs,
            settings_tab=settings,
        )

    # 6. Final initial refresh + balance
    await refresh_all()

    # Optional: First-time welcome
    if not pref_get(page, "seen_welcome", False):
        await page.show_snack(
            "Welcome to MorningMoney! Track transactions, watch investments grow, and aim for FIRE.",
            bgcolor="#94d494",
            duration=6000
        )
        pref_get(page, "seen_welcome", True)  # Mark as seen (sync set)

async def main(page: ft.Page):
    # Core init
    init_page_extensions(page)
    init_theme(page)  # Sync – applies dark/light

    # Optional: log startup
    # logging.basicConfig(level=logging.DEBUG)

    await build_main_ui(page)


if __name__ == "__main__":
    ft.app(target=main)  # Modern entry point – perfect!