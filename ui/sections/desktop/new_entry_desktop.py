# ui/sections/desktop/new_entry_desktop.py
import flet as ft
from ui.components.new_entry_form import new_entry_form
from ui.components.investment_form import investment_form


class NewEntryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all=None):
        super().__init__(
            expand=True,
            scroll=ft.ScrollMode.AUTO,          # more explicit than string "auto"
            spacing=24,                         # slightly more breathing room
        )
        self._page = page
        self.refresh_all = refresh_all

        # We'll keep references so we can refresh content without rebuilding everything
        self.transaction_container = ft.Container(
            padding=20,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY_CONTAINER),
            border_radius=12,
        )
        self.investment_container = ft.Container(
            padding=20,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY_CONTAINER),
            border_radius=12,
        )

        self.controls = [
            ft.Text("New Entry", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
            self.transaction_container,
            ft.Divider(height=32, color=ft.Colors.TRANSPARENT),
            self.investment_container,
        ]

        # Build initial content
        self._rebuild_content()

    def _rebuild_content(self):
        """Rebuild only the inner forms — preserves focus/state where possible."""
        try:
            # Transaction section
            self.transaction_container.content = ft.Column([
                ft.Text("Add Transaction", size=24, weight=ft.FontWeight.W_600),
                new_entry_form(self._page, self.refresh_all),
            ], spacing=16)

            # Investment section
            self.investment_container.content = ft.Column([
                ft.Text("Add Investment", size=24, weight=ft.FontWeight.W_600),
                investment_form(self._page, self.refresh_all),
            ], spacing=16)

        except Exception as ex:
            # Graceful fallback — better than blank screen
            error_msg = f"Error loading forms: {str(ex)}"
            print(error_msg)  # for debugging
            self.transaction_container.content = ft.Text(error_msg, color=ft.Colors.RED_400)
            self.investment_container.content = ft.Text("Investment form unavailable", color=ft.Colors.RED_400)

        self._page.update()  # or await self._page.safe_update() if you prefer

    async def refresh(self):
        """
        Called from global refresh_all.
        We rebuild content instead of whole widget → faster & preserves more state.
        """
        await self._page.run_task(self._rebuild_content)  # run in task if heavy
        if self.refresh_all:
            # Optional: let parent know we're done
            await self.refresh_all()


# Optional: if you want even lighter refresh (only update dynamic parts)
# You could add methods like:
# async def refresh_transaction_form_only(self):
#     self.transaction_container.content.controls[1] = new_entry_form(self._page, self.refresh_all)
#     self._page.update()