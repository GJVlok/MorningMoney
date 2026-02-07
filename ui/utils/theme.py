# ui/utils/theme.py
import flet as ft

def get_theme(mode="dark"):
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#afdaaf", # Green for positive feedback
            error="red",
            background="#1e1e2e" if mode == "dark" else "white",
        ),
        use_material3=True, # Modern look
    )