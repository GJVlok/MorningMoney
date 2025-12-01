# ui/tabs.py
import flet as ft
import asyncio
from datetime import date
from src.models import (
    get_all_transactions,
    get_investments,
    add_transaction,
    add_or_update_investment,
    calculate_future_value,
)
from src.database import Transaction, Investment
from ui.dialogs import (
    edit_transaction_dialog,
    delete_transaction,
    edit_investment_dialog,
    delete_investment,
    money_text,
)


# ── Helper: Mobile long-press BottomSheet for transactions ─────────────────────
def _mobile_transaction_menu(t: Transaction, page: ft.Page, refresh_all):
    def handler(e):
        bs = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.EDIT, color="blue"),
                            title=ft.Text("Edit"),
                            on_click=lambda _: (
                                edit_transaction_dialog(page, t, refresh_all),
                                setattr(bs, "open", False),
                                page.update(),
                            ),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DELETE, color="red"),
                            title=ft.Text("Delete", color="red"),
                            on_click=lambda _: (
                                delete_transaction(page, t, refresh_all),
                                setattr(bs, "open", False),
                                page.update(),
                            ),
                        ),
                    ],
                    tight=True,
                ),
                padding=20,
                bgcolor=ft.Colors.ON_SURFACE_VARIANT,
                border_radius=10,
            ),
            open=True,
            enable_drag=True,
            is_scroll_controlled=True,
        )
        page.bottom_sheet = bs
        page.update()

    return handler


# ── Helper: Mobile long-press BottomSheet for investments ───────────────────────
def _mobile_investment_menu(inv: Investment, page: ft.Page, refresh_all):
    def handler(e):
        bs = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.EDIT, color="blue"),
                            title=ft.Text("Edit"),
                            on_click=lambda _: (
                                edit_investment_dialog(page, inv, refresh_all),
                                setattr(bs, "open", False),
                                page.update(),
                            ),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DELETE, color="red"),
                            title=ft.Text("Delete", color="red"),
                            on_click=lambda _: (
                                delete_investment(page, inv, refresh_all),
                                setattr(bs, "open", False),
                                page.update(),
                            ),
                        ),
                    ],
                    tight=True,
                ),
                padding=20,
                bgcolor=ft.Colors.ON_SURFACE_VARIANT,
                border_radius=10,
            ),
            open=True,
            enable_drag=True,
            is_scroll_controlled=True,
        )
        page.bottom_sheet = bs
        page.update()

    return handler


# ── Build transaction row – platform-aware ─────────────────────────────────────
def build_transaction_tile(t: Transaction, page: ft.Page, refresh_all):
    base_tile = ft.ListTile(
        leading=ft.Icon(ft.Icons.RECEIPT, color="#ff0066"),
        title=ft.Text(t.category, weight="bold"),
        subtitle=ft.Text(t.description or t.date.strftime("%d %b %Y"), color="grey"),
        trailing=money_text(t.amount, size=18),
    )

    # Desktop → show icons on the right
    if page.platform in ("windows", "macos", "linux"):
        return ft.Container(
            content=ft.Row(
                [
                    base_tile,
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color="blue400",
                                tooltip="Edit",
                                on_click=lambda _: edit_transaction_dialog(page, t, refresh_all),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color="red400",
                                tooltip="Delete",
                                on_click=lambda _: delete_transaction(page, t, refresh_all),
                            ),
                        ],
                        spacing=4,
                    ),
                ],
                alignment="spaceBetween",
                expand=True,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=8,
            on_hover=lambda e: setattr(e.control, "bgcolor", "#2d2d3d" if e.data == "true" else None)
            or e.control.update(),
        )

    # Mobile → long-press menu
    base_tile.on_long_press = _mobile_transaction_menu(t, page, refresh_all)
    return base_tile


# ── Build investment card – platform-aware ─────────────────────────────────────
def build_investment_card(inv: Investment, page: ft.Page, refresh_all):
    fv = calculate_future_value(inv)

    content = ft.Column(
        [
            ft.Text(inv.name, size=22, weight="bold", color="white"),
            ft.Text(
                f"Current: R{inv.current_value:,.0f}  •  +R{inv.monthly_contribution:,.0f}/mo @ {inv.expected_annual_return}%",
                color="grey",
            ),
            ft.Divider(color="grey"),
            ft.Text("Projected", color="#00ff88"),
            money_text(fv, size=34),
            ft.Text(
                f"R{fv/1_000_000:.2f} million {'FIRE!' if fv >= 10_000_000 else 'on track'}",
                color="#00ff88" if fv >= 10_000_000 else "orange",
                italic=True,
            ),
        ],
        spacing=8,
    )

    if page.platform in ("windows", "macos", "linux"):
        # Desktop: icons on the right
        return ft.Card(
            elevation=8,
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(content, padding=20, expand=True),
                        ft.Column(
                            [
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    tooltip="Edit",
                                    on_click=lambda _: edit_investment_dialog(page, inv, refresh_all),
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    tooltip="Delete",
                                    on_click=lambda _: delete_investment(page, inv, refresh_all),
                                ),
                            ],
                            spacing=4,
                            alignment="end",
                        ),
                    ],
                    alignment="spaceBetween",
                ),
                bgcolor="#1e1e2e",
                border_radius=12,
                padding=10,
            ),
        )
    else:
        # Mobile: long-press
        card = ft.Card(
            elevation=6,
            content=ft.Container(
                content,
                padding=20,
                bgcolor="#1e1e2e",
                border_radius=12,
                on_long_press=_mobile_investment_menu(inv, page, refresh_all),
            ),
        )
        return card


# ── New Entry Tab ───────────────────────────────────────────────────────────────
class NewEntryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(scroll="auto")
        self.page = page
        self.refresh_all = refresh_all

        self.amount = ft.TextField(label="Amount (R)", keyboard_type="number")
        self.category = ft.Dropdown(
            label="Category",
            value="Groceries",
            options=[ft.dropdown.Option(c) for c in [
                "Salary", "Salary", "Freelance", "Other Income",
                "Groceries", "Transport", "Entertainment", "Rent",
                "Subscriptions", "Savings", "Investment"
            ]],
        )
        self.type_switch = ft.Switch(label="Income (on) / Expense (off)", value=False)
        self.notes = ft.TextField(label="Notes (optional)", multiline=True, min_lines=1, max_lines=3)
        self.message = ft.Text()

        self.controls = [
            ft.Text("Add Transaction", size=28, weight="bold"),
            self.amount,
            self.category,
            ft.Row([self.type_switch, ft.Text("Income Expense")]),
            self.notes,
            ft.ElevatedButton("Save Transaction", on_click=self.save),
            self.message,
        ]

    async def save(self, e):
        try:
            amt = float(self.amount.value or "0")
            if not self.type_switch.value:  # expense
                amt = -abs(amt)
        except:
            self.message.value = "Invalid amount!"
            self.message.color = "red"
            self.page.update()
            return

        add_transaction(
            date=date.today(),
            category=self.category.value or "Uncategorized",
            amount=amt,
            description=self.notes.value or "",
        )

        self.amount.value = ""
        self.notes.value = ""
        self.message.value = "Saved!"
        self.message.color = "green"
        self.page.update()
        await self.refresh_all()


# ── Diary Tab ───────────────────────────────────────────────────────────────────
class DiaryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(scroll="auto", expand=True)
        self.page = page
        self.refresh_all = refresh_all
        self.list = ft.Column(scroll="auto", expand=True)

        self.controls = [
            ft.Text("Recent Transactions", size=28, weight="bold"),
            ft.Divider(),
            self.list,
        ]

    async def refresh(self):
        self.list.controls.clear()
        for t in get_all_transactions()[:100]:
            self.list.controls.append(build_transaction_tile(t, self.page, self.refresh_all))
        self.page.update()


# ── Investments Tab ───────────────────────────────────────────────────────────────
class InvestmentsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(scroll="auto", expand=True)
        self.page = page
        self.refresh_all = refresh_all
        self.container = ft.Column(scroll="auto")

        self.controls = [
            ft.Text("Investments & Retirement", size=28, weight="bold"),
            self.container,
        ]

    async def refresh(self):
        self.container.controls.clear()
        investments = get_investments()
        if not investments:
            self.container.controls.append(ft.Text("No investments yet. Add your first one below!", italic=True, color="grey"))

        for inv in investments:
            self.container.controls.append(build_investment_card(inv, self.page, self.refresh_all))

        # ── Add / Update Investment Form ─────────────────────
        name = ft.TextField(label="Fund Name (e.g. RA – Discovery)")
        current = ft.TextField(label="Current Value", keyboard_type="number")
        monthly = ft.TextField(label="Monthly Contribution", value="0")
        rate = ft.TextField(label="Expected Return %", value="11")
        year = ft.TextField(label="Target Year", value="2050")

        self.container.controls.extend([
            ft.Divider(height=30, color="transparent"),
            ft.Text("Add / Update Investment", weight="bold", size=20),
            name, current, monthly, rate, year,
            ft.ElevatedButton(
                "Save Investment",
                on_click=lambda e: asyncio.create_task(
                    self.save_investment(name.value, current.value, monthly.value, rate.value, year.value)
                ),
            ),
        ])
        self.page.update()

    async def save_investment(self, name, current, monthly, rate, year):
        try:
            add_or_update_investment(
                name=name or "Unnamed",
                current_value=float(current or 0),
                monthly=float(monthly or 0),
                return_rate=float(rate or 11),
                target_year=int(year or 2050),
            )
            self.page.show_snack("Investment saved!", bgcolor="green")
            await self.refresh()
        except Exception as exc:
            self.page.show_snack("Invalid input", bgcolor="red")