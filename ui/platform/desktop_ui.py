# ui/platform/desktop_ui.py
import flet as ft

from ui.sections.desktop.new_entry_desktop import NewEntryTab
from ui.sections.desktop.diary_desktop import DiaryTab
from ui.sections.desktop.monthly_desktop import MonthlyTab
from ui.sections.desktop.investments_desktop import InvestmentsTab
from ui.sections.desktop.tags_insights_desktop import TagsInsightsTab
from ui.sections.desktop.savings_brag_desktop import SavingsBragTab
from ui.sections.desktop.graphs_desktop import GraphsTab
from ui.sections.desktop.settings_desktop import SettingsTab

from controls.desktop import build_desktop_ui

def build_desktop(page: ft.Page):

    tabs = []

    async def refresh_all():
        for t in tabs:
            if hasattr(t, "refresh"):
                await t.refresh()
        await page.safe_update()

    # Instantiate tabs
    new_entry = NewEntryTab(page, refresh_all)
    diary = DiaryTab(page, refresh_all)
    monthly = MonthlyTab(page, refresh_all)
    investments = InvestmentsTab(page, refresh_all)
    tags_insights = TagsInsightsTab(page, refresh_all)
    savings_brag = SavingsBragTab(page, refresh_all)
    graphs = GraphsTab(page, refresh_all)
    settings = SettingsTab(page, refresh_all)

    tabs.extend([
        new_entry,
        diary,
        monthly,
        investments,
        tags_insights,
        savings_brag,
        graphs,
        settings,
    ])

    build_desktop_ui(
        page,
        new_entry,
        diary,
        monthly,
        investments,
        tags_insights,
        savings_brag,
        graphs,
        settings,
    )

    page.run_task(lambda: refresh_all())