# ui/utils/theme.py
import flet as ft

def get_color_scheme(mode: str = "dark") -> ft.ColorScheme:
    if mode == "light":
        return ft.ColorScheme(
                primary="#2e8b57",
                background="#f8fff8",
                surface="#ffffff",
                on_background="#000000",
                on_surface="#000000",
            ),

    else: # Dark mode
        return ft.ColorScheme(
                primary="#94d494",
                background="#1e1e2e",
                surface="#2d2d3d",
                on_background="#ffffff",
                on_surface="#ffffff",
            ),