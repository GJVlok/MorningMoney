# src/services/settings.py
# Minimal service for any future settings-related logic.
import flet as ft
from ui.utils.theme import apply_theme
from ui.utils.flet_compat import safe_update  # Keep your custom helper

def set_force_desktop(session, value: bool):
    session.set("force_desktop", value)  # Session is still useful for runtime, but persist with client_storage if needed

def set_force_mobile(session, value: bool):
    session.set("force_mobile", value)

def get_force_desktop(session):
    try:
        return session["force_desktop"]
    except (KeyError, TypeError):
        return False
    
def get_force_mobile(session):
    try:
        return session["force_mobile"]  # Fixed typo: was "force_desktop" duplicate
    except (KeyError, TypeError):
        return False

def init_theme(page: ft.Page):  # Removed async—client_storage is sync now
    """
    Initialize theme on app startup.
    Attaches toggle_theme to page.
    """
    # No need for _prefs_initialized or overlay—client_storage is always available
    theme_mode_str = page.client_storage.get("theme_mode") or "dark"  # Default to dark
    page.theme_mode = ft.ThemeMode.DARK if theme_mode_str == "dark" else ft.ThemeMode.LIGHT
    apply_theme(page, page.theme_mode)  # Your custom theme applicator

    def toggle_theme():  # Removed async—sync now
        try:
            new_mode = "dark" if page.theme_mode == ft.ThemeMode.LIGHT else "light"
            page.theme_mode = ft.ThemeMode.DARK if new_mode == "dark" else ft.ThemeMode.LIGHT
            apply_theme(page, page.theme_mode)
            page.client_storage.set("theme_mode", new_mode)  # Sync save
            page.show_snack_bar(ft.SnackBar(ft.Text(f"{new_mode.capitalize()} mode activated!"), bgcolor="#94d494"))  # Updated to show_snack_bar (Flet's method)
            page.update()
        except Exception as ex:
            print(f"Toggle theme error: {ex}")
            page.show_snack_bar(ft.SnackBar(ft.Text("Couldn't save theme preference"), bgcolor="red"))

    page.toggle_theme = toggle_theme  # Attach as sync method

# def get_username(page: ft.Page) -> str:  # Commented out, but if needed: use client_storage.get("username", "friend")
#     return page.client_storage.get("username") or "friend"