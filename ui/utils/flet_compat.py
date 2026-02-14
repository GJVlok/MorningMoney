# ui/utils/flet_compat.py
import asyncio
from pathlib import Path
from typing import Any

async def safe_update(page):  # Keep async for now, but could be sync
    """Async-safe wrapper around page.update()."""
    try:
        page.update()
    except Exception:
        await asyncio.sleep(0)
        try:
            page.update()
        except Exception:
            pass

def set_window_size(page, width: int, height: int):
    """Safe window size setter (no-op if API changed)."""
    win = getattr(page, "window", None)
    if not win:
        return
    try:
        page.window.width = width  # Updated: page.window (newer Flet API)
        page.window.height = height
    except Exception:
        pass  # Ignore if API changes

def center_window(page):
    win = getattr(page, "window", None)
    if not win:
        return
    try:
        page.window.center()  # Updated: page.window.center()
    except Exception:
        pass

def run_task(page, coro_or_callable, *args, **kwargs):
    try:
        if asyncio.iscoroutinefunction(coro_or_callable):
            asyncio.create_task(coro_or_callable(*args, **kwargs))  # Schedule async
        else:
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, lambda: coro_or_callable(*args, **kwargs))  # Sync in thread
    except Exception:
        pass

def pref_get(page, key: str, default: Any = None):  # Sync now
    """Use page.client_storage.get."""
    try:
        return page.client_storage.get(key) or default
    except Exception:
        return default

def pref_set(page, key: str, value: Any):  # Sync now
    """Use page.client_storage.set."""
    try:
        page.client_storage.set(key, value)
    except Exception:
        pass