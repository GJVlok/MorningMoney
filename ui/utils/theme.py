# ui/utils/theme.py
import flet as ft

def apply_theme(page: ft.Page, mode: ft.ThemeMode):
    page.theme_mode = mode

    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.GREEN,
        use_material3=True,
    )