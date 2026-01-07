# ui/components/settings_dev_tools.py
import flet as ft
from src.services.settings import (
    set_force_desktop,
    set_force_mobile,
    get_force_desktop,
    get_force_mobile,
)


def settings_dev_tools(page: ft.Page, refresh_all=None) -> ft.Column:
    force_desktop = get_force_desktop(page.session)
    force_mobile = get_force_mobile(page.session)

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

    def apply_desktop_override(enabled: bool):
        set_force_desktop(page.session, enabled)
        if enabled:
            set_force_mobile(page.session, False)
            switch_mobile.value = False
        page.run_task(page.show_snack, "Desktop mode applied! Restart app.", "blue")

    def apply_mobile_override(enabled: bool):
        set_force_mobile(page.session, enabled)
        if enabled:
            set_force_desktop(page.session, False)
            switch_desktop.value = False
        page.run_task(page.show_snack, "Mobile mode applied! Restart app.", "blue")

    def on_desktop_toggle(e):
        apply_desktop_override(switch_desktop.value)

    def on_mobile_toggle(e):
        apply_mobile_override(switch_mobile.value)

    switch_desktop.on_change = on_desktop_toggle
    switch_mobile.on_change = on_mobile_toggle

    def reset_layout(e):
        set_force_desktop(page.session, False)
        set_force_mobile(page.session, False)
        switch_desktop.value = False
        switch_mobile.value = False
        page.run_task(page.show_snack, "Auto-detect restored! Restart app.", "orange")

    def apply_desktop_size(e):
        page.window.width = 1200
        page.window.height = 800
        page.window.center()
        page.update()
        page.run_task(page.show_snack, "Window resized to 1200x800", "green")

    return ft.Column(
        spacing=15,
        scroll="auto",
        controls=[
            ft.Text("Developer Tools", size=26, weight="bold"),
            ft.Divider(),
            ft.Text("Layout Override", size=18, weight="bold"),
            switch_desktop,
            switch_mobile,
            ft.Divider(height=20),
            ft.ElevatedButton(
                "Auto Detect Device",
                icon=ft.Icons.PHONE_ANDROID,
                bgcolor="orange",
                color="white",
                on_click=reset_layout,
            ),
            ft.ElevatedButton(
                "Apply Desktop Size (1200x800)",
                icon=ft.Icons.FULLSCREEN,
                on_click=apply_desktop_size,
            ),
            ft.Divider(height=20),
            ft.Text(
                "Changes require app restart.\nUse during development only!",
                size=12,
                color="grey",
                italic=True,
                text_align="center",
            ),
        ],
    )
