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

async def init_theme(page: ft.Page):  # Removed async—client_storage is sync now
    """
    Initialize theme on app startup.
    Attaches toggle_theme to page.
    """
    
    prefs = page.shared_preferences
    theme_mode_str = await prefs.get("theme_mode") or "dark"
    
    if theme_mode_str == "dark":
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT

    apply_theme(page, page.theme_mode)

# Attach toggle function (make it async too)
    async def toggle_theme():
        try:
            current = page.theme_mode
            new_mode = "light" if current == ft.ThemeMode.DARK else "dark"
            page.theme_mode = ft.ThemeMode.LIGHT if new_mode == "light" else ft.ThemeMode.DARK
            apply_theme(page, page.theme_mode)

            # Save async
            await prefs.set("theme_mode", new_mode)
            await page.show_snack(f"{new_mode.capitalize()} mode activated!", bgcolor="#94d494")
            await page.update_async()  # Safer in async world
        except Exception as ex:
            print(f"Toggle theme error: {ex}")
            await page.show_snack("Couldn't save theme preference", bgcolor="red")

    page.toggle_theme = toggle_theme  # Still attach to page

# def get_username(page: ft.Page) -> str:  # Commented out, but if needed: use client_storage.get("username", "friend")
#     return page.client_storage.get("username") or "friend"