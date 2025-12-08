# ui/utils/device_detect.py
from typing import Literal
import flet as ft

def detect_platform(page: ft.Page) -> Literal["desktop","mobile","web"]:
    # lightweight canonical detection
    # web platform (if served as web) - page.platform may be "web"
    plat = getattr(page, "platform", "").lower()
    if plat in ("web", "android", "ios"):
        # Distinguish mobile vs web using window width for web-served apps:
        w = getattr(getattr(page, "window", None), "width", None)
        if plat == "web" and w and w > 800:
            return "web"
        if plat in ("android", "ios"):
            return "mobile"
        return "web"
    # desktop OSes -> desktop
    if plat in ("windows", "macos", "linux"):
        return "desktop"

    # fallback: use window size heuristics
    w = getattr(getattr(page, "window", None), "width", 0) or 0
    h = getattr(getattr(page, "window", None), "height", 0) or 0
    if w > 900 or h > 900:
        return "desktop"
    if w <= 600:
        return "mobile"
    return "web"
