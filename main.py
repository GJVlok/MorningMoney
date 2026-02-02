# main.py
import flet as ft
import asyncio

from controls.common import init_page_extensions
from controls.desktop import build_desktop_ui
from controls.mobile import build_mobile_ui
from controls.web import build_web_ui

async def show_login_screen(page: ft.Page):
    page.clean()

    username_field = ft.TextField(
        label="Username",
        value=page.session.get("username") or "",
        autofocus=True,
        width=300
    )

    password_field = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=300
    )

    error_text = ft.Text(color="red", size=14)

    async def try_login(e):
        u = username_field.value.strip()
        p = password_field.value.strip()

        # Very basic check — in real life we'd compare to stored value
        stored_u = page.session.get("saved_username")
        stored_p = page.session.get("saved_password")

        if stored_u and stored_p:
            # already registered → check credentials
            if u == stored_u and p == stored_p:
                page.session.set("logged_in", True)
                page.session.set("username", u)
                build_main_ui(page)
                await page.show_snack(f"Welcome back, {u}!", "green")
            else:
                error_text.value = "Incorrect username or password"
                error_text.update()
        else:
            # First time → register
            if u and p:
                page.session.set("saved_username", u)
                page.session.set("saved_password", p)
                page.session.set("logged_in", True)
                page.session.set("username", u)
                await build_main_ui(page)
                await page.show_snack(f"Account created! Welcome, {u}!", "green")
            else:
                error_text.value = "Please enter username and password"
                error_text.update()

    login_button = ft.ElevatedButton(
        "Login / Create Account",
        on_click=try_login,
        width=300
    )

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("MorningMoney", size=36, weight="bold"),
                    ft.Text("Your personal finance companion", size=16, color="grey"),
                    ft.Container(height=40),
                    username_field,
                    password_field,
                    error_text,
                    ft.Container(height=20),
                    login_button,
                ],
                horizontal_alignment="center",
                alignment="center",
                spacing=16
            ),
            expand=True,
            alignment=ft.alignment.center
        )
    )

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
            from ui.sections.web.new_entry import NewEntryTab
            from ui.sections.web.diary import DiaryTab
            from ui.sections.web.investments import InvestmentsTab
            from ui.sections.web.settings import SettingsTab
            platform_name = "web"
        else:
            from ui.sections.desktop.new_entry import NewEntryTab
            from ui.sections.desktop.diary import DiaryTab
            from ui.sections.desktop.investments import InvestmentsTab
            from ui.sections.desktop.settings import SettingsTab
            platform_name = "desktop"
    else:
        from ui.sections.mobile.new_entry import NewEntryTab
        from ui.sections.mobile.diary import DiaryTab
        from ui.sections.mobile.investments import InvestmentsTab
        from ui.sections.mobile.settings import SettingsTab
        platform_name = "mobile"

    # ---- create tabs ----
    new_entry_tab = NewEntryTab(page, None)
    diary_tab = DiaryTab(page, None)
    investments_tab = InvestmentsTab(page, None)
    settings_tab = SettingsTab(page, None)

    tabs = [new_entry_tab, diary_tab, investments_tab, settings_tab]

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
        build_web_ui(page, *tabs)
    elif platform_name == "desktop":
        page.window.width = 1200
        page.window.height = 800
        page.window.center()
        build_desktop_ui(page, *tabs)
    else:  # mobile
        page.window.width = 480
        page.window.height = 900
        build_mobile_ui(page, *tabs)
        page.route = "/diary"

    page.run_task(refresh_all)

    # Optional: show username in header later
    await page.show_snack(f"Welcome, {page.session.get('username') or 'friend'}!", "green")

async def main(page: ft.Page):
    page.title = "MorningMoney"
    page.theme_mode = "dark"

    init_page_extensions(page)

    # Simple check: already logged in?
    if page.session.get("logged_in"):
        build_main_ui(page)
    else:
        await show_login_screen(page)

ft.app(target=main)
