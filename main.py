# main.py  ← The clean version you always wanted
import flet as ft
import asyncio
from datetime import date

# ── Core data layer ─────────────────────────────────────
from src.models import (
    get_balance,
    get_total_projected_wealth,
    add_transaction,
    get_all_transactions,
    get_investments,
    add_or_update_investment,
    calculate_future_value,
)
from src.database import Transaction, Investment

# ── UI pieces (we will move these soon too) ─────────────
from ui.tabs import NewEntryTab, DiaryTab, InvestmentsTab          # ← create this folder next
from ui.dialogs import (
    edit_transaction_dialog, delete_transaction,
    edit_investment_dialog, delete_investment,
)

# ── Platform-specific layouts ───────────────────────────
from controls.desktop import build_desktop_ui
from controls.mobile import build_mobile_ui
# from controls.web import build_web_ui   # when you're ready

# ── Shared stuff ───────────────────────────────────────
from controls.common import daily_fire_container, splash


async def main(page: ft.Page):
    page.title = "MorningMoney"
    page.theme_mode = "dark"
    page.padding = 20 if page.platform in ("windows", "macos", "linux") else 10
    page.long_press_duration = 500

    # Splash screen
    await splash(page)

    # Choose the right layout automatically
    if page.platform in ("android", "ios"):
        build_ui = build_mobile_ui
    elif page.web:
        # build_ui = build_web_ui
        build_ui = build_desktop_ui  # fallback until web.py exists
    else:
        build_ui = build_desktop_ui

    # Shared refresh function used by all tabs
    async def refresh_all():
        await asyncio.gather(
            diary_tab.refresh(),
            investments_tab.refresh(),
        )
        if hasattr(page, "balance_updater"):
            page.balance_updater()

    # Create the three main tabs (logic lives in ui/tabs.py)
    new_entry_tab = NewEntryTab(page, refresh_all)
    diary_tab     = DiaryTab(page, refresh_all)
    investments_tab = InvestmentsTab(page, refresh_all)

    # Let the platform-specific file build the actual UI
    build_ui(page, new_entry_tab, diary_tab, investments_tab)

    # First data load
    await refresh_all()


# ── Start the app (auto-detects desktop / web / mobile) ──
ft.app(target=main)