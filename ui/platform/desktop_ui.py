# ui/platform/desktop_ui.py
import flet as ft

from ui.sections.desktop.new_entry import NewEntryTab
from ui.sections.desktop.diary import DiaryTab
from ui.sections.desktop.investments import InvestmentsTab
from ui.sections.desktop.graphs import GraphsTab
from ui.sections.desktop.settings import SettingsTab

from controls.desktop import build_desktop_ui


def build_desktop(page: ft.Page):
    # Instantiate tabs
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

    build_desktop_ui(
        page,
        new_entry,
        diary,
        investments,
        graphs,
        settings,
    )

    page.run_task(refresh_all)