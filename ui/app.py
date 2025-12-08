# ui/app.py
import flet as ft
from ui.platform import desktop_ui, mobile_ui, web_ui
from ui.utils.device_detect import detect_platform

def main(page: ft.Page):
    # Optional: init extensions (safe_update, show_snack) — use your existing init_page_extensions
    try:
        from controls.common import init_page_extensions
        init_page_extensions(page)
    except Exception:
        pass

    platform = detect_platform(page)

    if platform == "desktop":
        desktop_ui.build_desktop_ui(page)
    elif platform == "web":
        web_ui.build_web_ui(page)
    else:
        mobile_ui.build_mobile_ui(page)

if __name__ == "__main__":
    ft.app(target=main)
