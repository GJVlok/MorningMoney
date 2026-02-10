# ui/platform/mobile_ui.py
import flet as ft

from ui.sections.mobile.new_entry_mobile import NewEntryTab
from ui.sections.mobile.diary_mobile import DiaryTab
from ui.sections.mobile.investments_mobile import InvestmentsTab
from ui.sections.mobile.graphs_mobile import GraphsTab
from ui.sections.mobile.settings_mobile import SettingsTab

from controls.mobile import build_mobile_ui


def build_mobile(page: ft.Page):
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

    build_mobile_ui(
        page,
        new_entry,
        diary,
        investments,
        graphs,
        settings,
    )

    page.route = "/diary"
    page.run_task(refresh_all)