# ui/utils/theme.py
import flet as ft

def get_theme(mode: str = "dark") -> ft.Theme:
    if mode == "light":
        return ft.Theme(
            use_material3=True,
            color_scheme=ft.ColorScheme(
                primary="#2e8b57",
                background="#f8fff8",
                surface="#ffffff",
                on_background="#000000",
                on_surface="#000000",
            ),
            page_transitions=ft.PageTransitionsTheme.cupertino,
        )
    else: # Dark mode
        return ft.Theme(
            use_material3=True,
            color_scheme=ft.ColorScheme(
                primary="#afdaaf",
                background="#1e1e2e",
                surface="#2d2d3d",
                on_background="#ffffff",
                on_surface="#ffffff",
            ),
            page_transitions=ft.PageTransitionsTheme.cupertino,
        )