# ui/utils/ui_helpers.py
import asyncio
import flet as ft

def attach_page_helpers(page: ft.Page):
    # safe update wrapper and show_snack - reuses existing pattern
    async def safe_update():
        try:
            page.update()
        except Exception:
            await asyncio.sleep(0)
            page.update()

    async def show_snack(message: str, bgcolor: str = "green", duration_ms: int = 4000):
        page.snack_bar = ft.SnackBar(ft.Text(message, color="white"), bgcolor=bgcolor, open=True, duration=duration_ms)
        page.snack_bar.open = True
        page.update()
        await asyncio.sleep(0)

    page.safe_update = safe_update
    page.show_snack = show_snack
