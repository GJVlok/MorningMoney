# ui/utils/flet_compat.py
import asyncio
from pathlib import Path
from typing import Any

async def safe_update(page):
    """Async-safe wrapper around page.update()."""
    try:
        page.update()
    except Exception:
        # best-effort retry in next loop tick
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
        win.width = width
        win.height = height
    except Exception:
        # some Flet versions expose different API; ignore safely
        try:
            if hasattr(win, "set_size"):
                win.set_size(width, height)
        except Exception:
            pass

def center_window(page):
    win = getattr(page, "window", None)
    if not win:
        return
    try:
        win.center()
    except Exception:
        try:
            if hasattr(win, "center_window"):
                win.center_window()
        except Exception:
            pass

def run_task(page, coro_or_callable, *args, **kwargs):
    """
    Unified runner: try page.run_task if available; otherwise fallback to asyncio.create_task.
    Accepts coroutine function or coroutine object.
    """
    try:
        # prefer page.run_task when available
        if hasattr(page, "run_task"):
            return page.run_task(coro_or_callable, *args, **kwargs)
    except Exception:
        pass

    # fallback
    try:
        if asyncio.iscoroutine(coro_or_callable):
            return asyncio.create_task(coro_or_callable)
        if asyncio.iscoroutinefunction(coro_or_callable):
            return asyncio.create_task(coro_or_callable(*args, **kwargs))
        # sync callable -> run in thread
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, lambda: coro_or_callable(*args, **kwargs))
    except Exception:
        return None

async def pref_get(page, key: str, default: Any = None):
    """Try awaiting shared_preferences.get if it's async, otherwise return directly."""
    try:
        prefs = getattr(page, "shared_preferences", None)
        if prefs is None:
            return default
        val = prefs.get(key, default)
        if hasattr(val, "__await__"):
            return await val
        return val
    except Exception:
        return default

async def pref_set(page, key: str, value: Any):
    """Try set() and await if necessary; swallow errors."""
    try:
        prefs = getattr(page, "shared_preferences", None)
        if prefs is None:
            return
        res = prefs.set(key, value)
        if hasattr(res, "__await__"):
            await res
    except Exception:
        pass