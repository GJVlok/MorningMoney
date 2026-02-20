# ui/sections/desktop/new_entry_desktop.py
import flet as ft
import logging
from ui.components.new_entry_form import new_entry_form
from ui.components.investment_form import investment_form

class NewEntryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all=None):
        super().__init__(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=24,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,  # optional: full width
        )

        self._page = page
        self.padding = ft.padding.only(top=16, bottom=32, left=16, right=16)
        self.refresh_all = refresh_all

        # Containers for partial rebuild
        self.transaction_container = ft.Container(
            padding=20,
            bgcolor=ft.Colors.with_opacity(
                0.08, ft.Colors.PRIMARY_CONTAINER
            ),
            border_radius=12,
            expand=False,
        )

        self.investment_container = ft.Container(
            padding=20,
            bgcolor=ft.Colors.with_opacity(
                0.08, ft.Colors.PRIMARY_CONTAINER
            ),
            border_radius=12,
            expand=False,
        )

        self.controls = [
            ft.Text("New Entry", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
            self.transaction_container,
            ft.Divider(height=32, color=ft.Colors.TRANSPARENT),
            self.investment_container,
        ]

        self._rebuild_content()

    # ---------------- REBUILD ---------------- #

    def _rebuild_content(self):
        try:
            # Transaction section
            self.transaction_container.content = ft.Column(
                [
                    ft.Text(
                        "Add Transaction",
                        size=24,
                        weight=ft.FontWeight.W_600,
                    ),
                    new_entry_form(self._page, self.refresh_all),
                ],
                spacing=16,
            )

            # Investment section
            self.investment_container.content = ft.Column(
                [
                    ft.Text(
                        "Add Investment",
                        size=24,
                        weight=ft.FontWeight.W_600,
                    ),
                    investment_form(self._page, self.refresh_all),
                ],
                spacing=16,
            )

        except Exception as ex:
            logging.exception("Error rebuilding NewEntryTab")
            error_msg = f"Error loading forms: {str(ex)}"

            self.transaction_container.content = ft.Text(
                error_msg,
                color=ft.Colors.RED_400,
            )

            self.investment_container.content = ft.Text(
                "Investment form unavailable",
                color=ft.Colors.RED_400,
            )

    # ---------------- REFRESH ---------------- #

    async def refresh(self):
        self._rebuild_content()
        self.update()
