# ui/utils/device_detect.py
from typing import Literal
import flet as ft

def detect_platform(page: ft.Page) -> Literal["desktop", "mobile", "web"]:
    platform = page.platform  # This is now ft.PagePlatform enum

    if platform is None:
        # Rare fallback (e.g., very early in lifecycle)
        platform_name = "unknown"
    else:
        platform_name = platform.name.lower()  # .name gives string like "WINDOWS", "ANDROID", "WEB"

    # Now use the lowercased string
    if platform_name in ("web", "android", "ios"):
        # Web vs mobile distinction via width (your existing heuristic)
        w = getattr(getattr(page, "window", None), "width", None) or 0
        if platform_name == "web" and w > 800:
            return "web"
        if platform_name in ("android", "ios"):
            return "mobile"
        return "web"

    # Desktop OSes
    if platform_name in ("windows", "macos", "linux"):
        return "desktop"

    # Fallback heuristic (your original width-based logic)
    w = getattr(getattr(page, "window", None), "width", 0) or 0
    if w > 900:
        return "desktop"
    if w <= 600:
        return "mobile"
    return "web"
