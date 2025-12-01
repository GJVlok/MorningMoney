# ui/components/settings_dev_tools.py
import flet as ft

def settings_dev_tools(page: ft.Page, refresh_all):
    # Toggle to force desktop layout regardless of platform
    force_desktop = ft.Switch(
        label="Force Desktop Layout (for testing)",
        value=False,
        tooltip="Ignores actual device and forces wide desktop view + tabs",
    )

    def on_force_desktop_change(e):
        page.session.set("force_desktop", force_desktop.value)
        page.show_snack("Layout will update on next refresh", bgcolor="blue")
        page.update()

    force_desktop.on_change = on_force_desktop_change

    # Optional: Button to reset window size to desktop-friendly
    def reset_window(e):
        page.window.width = 1200
        page.window.height = 800
        page.window.center()
        page.update()
        page.show_snack("Window resized to desktop size", bgcolor="green")

    return ft.Column([
        ft.Text("Developer Tools", size=24, weight="bold"),
        ft.Divider(),
        force_desktop,
        ft.ElevatedButton("Reset Window to Desktop Size", on_click=reset_window, icon=ft.Icons.FULLSCREEN),
        ft.Text("Use these during development only", color="grey", italic=True, size=12),
    ], spacing=20)