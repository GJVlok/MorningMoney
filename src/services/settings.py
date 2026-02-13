# src/services/settings.py
# Minimal service for any future settings-related logic.
import flet as ft
from ui.utils.theme import apply_theme
from ui.utils.flet_compat import pref_get, pref_set, safe_update
import asyncio

def set_force_desktop(session, value: bool):
    session.set("force_desktop", value)

def set_force_mobile(session, value: bool):
    session.set("force_mobile", value)

def get_force_desktop(session):
    try:
        return session["force_desktop"]
    except (KeyError, TypeError):
        return False
    
def get_force_mobile(session):
    try:
        return session["force_desktop"]
    except (KeyError, TypeError):
        return False

async def init_theme(page: ft.Page):
    """
    Initialize theme on app startup.
    Attaches toggle_theme to page.
    """

    # Ensure SharedPreferences is mounted once
    if not hasattr(page, "_prefs_initialized"):
        prefs = ft.SharedPreferences()
        page.overlay.append(prefs)
        page._prefs_initialized = True

    # Load saved theme
    try:
        saved_mode = await pref_get(page, "theme_mode", "dark")
        page.theme_mode = saved_mode or "dark"
    except Exception as ex:
        print(f"Theme load failed (using dark) <{ex}>")
        page.theme_mode = "dark"

    apply_theme(page, page.theme_mode)

    # Attach toggle function to page
    page.toggle_theme = lambda e: page.run_task(toggle_theme, page)


async def toggle_theme(page: ft.Page):
    """
    Toggle between light and dark.
    """

    try:
        new_mode = "light" if page.theme_mode == "dark" else "dark"

        page.theme_mode = new_mode
        apply_theme(page, new_mode)

        await pref_set(page, "theme_mode", new_mode)

        await page.show_snack(
            f"{new_mode.capitalize()} mode activated!",
            "#94d494"
        )

        await safe_update(page)

    except TimeoutError:
        await page.show_snack(
            "Theme saved, but storage timed out - try again?",
            "orange"
        )

    except Exception as ex:
        print(f"Toggle theme error: {ex}")
        await page.show_snack(
            "Couldn't save theme preference",
            "red"
        )