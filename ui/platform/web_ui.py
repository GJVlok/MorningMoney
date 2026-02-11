# ui/platform/web_ui.py
import flet as ft

from ui.sections.web.new_entry_web import NewEntryTab
from ui.sections.web.diary_web import DiaryTab
from ui.sections.web.montly_web import MonthlyTab
from ui.sections.web.investments_web import InvestmentsTab
from ui.sections.web.tags_insights_web import TagsInsightsTab
from ui.sections.web.graphs_web import GraphsTab
from ui.sections.web.settings_web import SettingsTab

from controls.web import build_web_ui


def build_web(page: ft.Page):
    new_entry = NewEntryTab(page, None)
    diary = DiaryTab(page, None)
    monthly = MonthlyTab(page, None)
    investments = InvestmentsTab(page, None)
    tags_insights = TagsInsightsTab(page, None)
    graphs = GraphsTab(page, None)
    settings = SettingsTab(page, None)

    tabs = [new_entry,
            diary,
            monthly,
            investments,
            tags_insights,
            graphs,
            settings]

    async def refresh_all():
        for t in tabs:
            if hasattr(t, "refresh"):
                await t.refresh()
        await page.safe_update()

    for t in tabs:
        t.refresh_all = refresh_all

    build_web_ui(
        page,
        new_entry,
        diary,
        monthly,
        investments,
        tags_insights,
        graphs,
        settings,
    )

    page.run_task(refresh_all)