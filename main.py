# main.py
import flet as ft
import asyncio

from flet.auth.providers.google_oauth_provider import GoogleOAuthProvider
# Optional: also import for GitHub if you want to add later
# from flet.auth.providers.github_oauth_provider import GitHubOAuthProvider

from controls.common import init_page_extensions
from controls.desktop import build_desktop_ui
from controls.mobile import build_mobile_ui
from controls.web import build_web_ui


CLIENT_ID = "82937931108-q9ugkk302g2a011k5pds3ka4i9molnjn.apps.googleusercontent.com"
CLIENT_SECRET = "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"

async def show_login_screen(page: ft.Page):
    page.clean()

    # Create Google provider once (can be moved higher if you want)
    google_provider = GoogleOAuthProvider(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_url="http://localhost:8555/oauth_callback", # <- important: use this path now!
        # Optional scopes - add if you need more user info
        # scopes=["openid", "email", "profile"]
    )

        # In newer Flet the callback changed from /api/oauth/redirect → /oauth_callback
        # Use port 8555 (or whatever flet run uses; default desktop is 8555, web often 8000—check your terminal when app starts)
        # For production later you'll change this to your deployed domain

    page.add(
        ft.Column(
            [
                ft.Text("Welcome to MorningMoney", size=32, weight="bold", text_align="center"),
                ft.Text("Track your finances. Build your future.", size=16, color="grey", text_align="center"),
                ft.Container(height=40),
                ft.ElevatedButton(
                    text="Login",
                    icon=ft.Icons.LOGIN,
                    bgcolor="#4285F4",
                    color="white",
                    width=300,
                    height=50,
                    on_click=lambda e: page.login(google_provider),
                ),
                ft.Container(height=20),
                ft.Text("Secure • Private • Yours", size=12, color="grey", text_align="center"),
            ],
            alignment="center",
            horizontal_alignment="center",
            expand=True,
        )
    )


async def main(page: ft.Page):
    page.title = "MorningMoney"
    page.theme_mode = "dark"

    # Detect current port (works for flet run / desktop)
    redirect_port = page.web.split(":")[-1].split("/")[0] if page.web else "8555"
    redirect_url = f"http://localhost:{redirect_port}/oauth_callback"

    init_page_extensions(page)

        # ---- platform detection ----

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
            platform = "web"
        else:
            from ui.sections.desktop.new_entry import NewEntryTab
            from ui.sections.desktop.diary import DiaryTab
            from ui.sections.desktop.investments import InvestmentsTab
            from ui.sections.desktop.settings import SettingsTab
            platform = "desktop"
    else:
        from ui.sections.mobile.new_entry import NewEntryTab
        from ui.sections.mobile.diary import DiaryTab
        from ui.sections.mobile.investments import InvestmentsTab
        from ui.sections.mobile.settings import SettingsTab
        platform = "mobile"

    def on_login(e: ft.LoginEvent):
        if e.error:
            page.show_snack(f"Login failed: {e.error}", "red")
            return
        
        if page.auth and page.auth.user: # Successful login!
            page.session.set("user_id", page.auth.user.id) # Save who logged in
            page.session.set("user_email", page.auth.user.email if hasattr(page.auth.user, 'email') else None) # Optional - nice for future
            page.clean() # Clear login screen

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

            if platform == "web":
                page.window.width = 1200
                page.window.height = 800
                build_web_ui(page, *tabs)

            elif platform == "desktop":
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
            page.show_snack(f"Welcome back, {page.auth.user.email or 'friend'}!", "green")
        else:
            page.show_snack("Login succeeded but no user info recieved", "orange")

    page.on_login = on_login

    def logout(e):
        page.logout()
        page.session.clear() # or remove specific keys
        page.clean()
        page.run_task(show_login_screen, page) # or just await show_login_screen(page)
        page.show_snack("Logged out. See you soon!", "blue")
    
    # Example button
    ft.ElevatedButton("Logout", on_click=logout, icon=ft.Icons.LOGOUT)

    # Show login first
    if not page.auth or not page.auth.user: # If not already logged in
        await show_login_screen(page)
    else:
        # User is already logged in -> restore session & show main UI
        page.session.set("user_id", page.auth.user.id)   # or .sub, .uid - depends on provider
        page.session.set("user_email", page.auth.user.email if hasattr(page.auth.user, 'email') else None)

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

        if platform == "web":
            page.window.width = 1200
            page.window.height = 800
            build_web_ui(page, *tabs)

        elif platform == "desktop":
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
        page.show_snack(f"Welcome back, {page.auth.user.email or 'friend'}!", "green")


ft.app(target=main)
