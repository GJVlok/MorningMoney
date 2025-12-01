# ui/components/settings_dev_tools.py
import flet as ft


def settings_dev_tools(page: ft.Page, refresh_all):
    # Read current state
    force_desktop = page.session.get("force_desktop") or False
    force_mobile = page.session.get("force_mobile") or False

    switch_desktop = ft.Switch(
        label="Force Desktop Layout",
        value=force_desktop,
        tooltip="Forces wide window + tabs even on phone",
    )

    switch_mobile = ft.Switch(
        label="Force Mobile Layout",
        value=force_mobile,
        tooltip="Forces narrow phone view + bottom nav even on desktop",
    )

    # Helper to show snackbar (Flet 0.28.3 safe)
    def show_snack(text: str, bg="blue"):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(text, color="white"),
            bgcolor=bg,
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    # Toggle handlers
    def on_desktop_toggle(e):
        new_val = switch_desktop.value
        page.session.set("force_desktop", new_val)
        if new_val:
            page.session.set("force_mobile", False)
            switch_mobile.value = False
        show_snack("Desktop mode applied! Restart app.", "blue")

    def on_mobile_toggle(e):
        new_val = switch_mobile.value
        page.session.set("force_mobile", new_val)
        if new_val:
            page.session.set("force_desktop", False)
            switch_desktop.value = False
        show_snack("Mobile mode applied! Restart app.", "blue")

    switch_desktop.on_change = on_desktop_toggle
    switch_mobile.on_change = on_mobile_toggle

    # Reset to auto-detect
    def reset_layout(e):
        page.session.set("force_desktop", False)
        page.session.set("force_mobile", False)
        switch_desktop.value = False
        switch_mobile.value = False
        show_snack("Auto-detect restored! Restart app.", "orange")

    # Resize window
    def apply_desktop_size(e):
        page.window.width = 1200
        page.window.height = 800
        page.window.center()
        page.update()
        show_snack("Window resized to 1200×800", "green")

    return ft.Column([
        ft.Text("Developer Tools", size=26, weight="bold"),
        ft.Divider(),
        ft.Text("Layout Override", size=18, weight="bold"),
        switch_desktop,
        switch_mobile,
        ft.Divider(height=20),
        ft.ElevatedButton("Auto Detect Device", icon=ft.Icons.PHONE_ANDROID, on_click=reset_layout, bgcolor="orange", color="white"),
        ft.ElevatedButton("Apply Desktop Size (1200x800)", icon=ft.Icons.FULLSCREEN, on_click=apply_desktop_size),
        ft.Divider(height=20),
        ft.Text(
            "Changes require app restart.\n"
            "Use during development only!",
            size=12, color="grey", italic=True, text_align="center"
        ),
    ], spacing=15, scroll="auto")