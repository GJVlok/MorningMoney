# ui/platform/desktop_ui.py
import flet as ft

from ui.sections.desktop.new_entry_desktop import NewEntryTab
from ui.sections.desktop.diary_desktop import DiaryTab
from ui.sections.desktop.monthly_desktop import MonthlyTab
from ui.sections.desktop.investments_desktop import InvestmentsTab
from ui.sections.desktop.graphs_desktop import GraphsTab
from ui.sections.desktop.settings_desktop import SettingsTab

from controls.desktop import build_desktop_ui


def build_desktop(page: ft.Page):
    # Instantiate tabs
    new_entry = NewEntryTab(page, None)
    diary = DiaryTab(page, None)
    monthly = MonthlyTab(page, None)
    investments = InvestmentsTab(page, None)
    graphs = GraphsTab(page, None)
    settings = SettingsTab(page, None)

    tabs = [new_entry, diary, monthly, investments, graphs, settings]

    async def refresh_all():
        for t in tabs:
            if hasattr(t, "refresh"):
                await t.refresh()
        await page.safe_update()

    for t in tabs:
        t.refresh_all = refresh_all

    build_desktop_ui(
        page,
        new_entry,
        diary,
        monthly,
        investments,
        graphs,
        settings,
    )

    page.run_task(refresh_all)