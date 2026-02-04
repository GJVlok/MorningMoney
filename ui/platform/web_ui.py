# ui/platform/web_ui.py
import flet as ft

from ui.sections.web.new_entry import NewEntryTab
from ui.sections.web.diary import DiaryTab
from ui.sections.web.investments import InvestmentsTab
from ui.sections.web.graphs import GraphsTab
from ui.sections.web.settings import SettingsTab

from controls.web import build_web_ui


def build_web(page: ft.Page):
    new_entry = NewEntryTab(page, None)
    diary = DiaryTab(page, None)
    investments = InvestmentsTab(page, None)
    graphs = GraphsTab(page, None)
    settings = SettingsTab(page, None)

    tabs = [new_entry, diary, investments, graphs, settings]

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
        investments,
        graphs,
        settings,
    )

    page.run_task(refresh_all)