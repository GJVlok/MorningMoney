# ui/tabs.py
import flet as ft
from datetime import date
from src.models import (
    get_all_transactions, get_investments,
    add_transaction, add_or_update_investment,
    calculate_future_value
)
from ui.dialogs import (
    edit_transaction_dialog, delete_transaction,
    edit_investment_dialog, delete_investment,
    money_text
)

class NewEntryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(scroll="auto")
        self.page = page
        self.refresh_all = refresh_all
        self.amount = ft.TextField(label="Amount (R)", keyboard_type="number")
        self.category = ft.Dropdown(
            label="Category",
            options=[
                ft.dropdown.Option(c) for c in [
                    "Salary", "Freelance", "Other Income",
                    "Groceries", "Transport", "Entertainment",
                    "Rent", "Subscriptions", "Savings", "Investment"
                ]
            ],
            value="Groceries"
        )
        self.type_switch = ft.Switch(label="Income (on) / Expense (off)", value=False)
        self.notes = ft.TextField(label="Notes (optional)", multiline=True, min_lines=1, max_lines=3)
        self.message = ft.Text("")
        self.controls = [
            ft.Text("Add Transaction", size=28, weight="bold"),
            self.amount, self.category,
            ft.Row([self.type_switch, ft.Text("Income Expense")]),
            self.notes,
            ft.ElevatedButton("Save Transaction", on_click=self.save),
            self.message,
        ]

    async def save(self, e):
        try:
            amt = float(self.amount.value or "0")
            if not self.type_switch.value: # expense
                amt = -amt
        except:
            self.message.value = "Invalid amount!"
            self.message.color = "red"
            self.page.update()
            return
        add_transaction(
            date=date.today(),
            category=self.category.value,
            amount=amt,
            description=self.notes.value or ""
        )
        # Clear fields
        self.amount.value = ""
        self.notes.value = ""
        self.message.value = "Saved!"
        self.message.color = "green"
        self.page.update()
        await self.refresh_all()

class DiaryTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(scroll="auto", expand=True)
        self.page = page
        self.refresh_all = refresh_all
        self.list = ft.Column(scroll="auto", expand=True)
        self.controls = [
            ft.Text("Recent Transactions", size=28, weight="bold"),
            ft.Divider(),
            self.list
        ]

    async def refresh(self):
        self.list.controls.clear()
        for t in get_all_transactions()[:50]:
            def create_handler(trans=t): # default arg captures current t
                def handler(e):
                    bs = ft.BottomSheet(
                        ft.Container(
                            ft.Column([
                                ft.ListTile(leading=ft.Icon(ft.Icons.EDIT), title=ft.Text("Edit"),
                                            on_click=lambda _: (edit_transaction_dialog(self.page, trans, self.refresh_all), setattr(bs, 'open', False), self.page.update())),
                                ft.ListTile(leading=ft.Icon(ft.Icons.DELETE, color="red"), title=ft.Text("Delete", color="red"),
                                            on_click=lambda _: (delete_transaction(self.page, trans, self.refresh_all), setattr(bs, 'open', False), self.page.update())),
                            ], tight=True),
                            padding=20,
                            bgcolor=ft.Colors.ON_SURFACE_VARIANT,
                            border_radius=10,
                        ),
                        open=True,
                        enable_drag=True,
                        is_scroll_controlled=True,
                    )
                    self.page.bottom_sheet = bs
                    self.page.update()
                return handler
            tile = ft.ListTile(
                leading=ft.Icon(ft.Icons.RECEIPT),
                title=ft.Text(t.category),
                subtitle=ft.Text(t.description or t.date.strftime("%Y-%m-%d")),
                trailing=money_text(t.amount, size=18),
                on_long_press=create_handler(),
            )
            self.list.controls.append(tile)
        self.page.update()

class InvestmentsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(scroll="auto", expand=True)
        self.page = page
        self.refresh_all = refresh_all
        self.container = ft.Column(spacing=20)
        self.controls = [
            ft.Text("Investments & Retirement", size=28, weight="bold"),
            self.container
        ]

    async def refresh(self):
        self.container.controls.clear()
        investments = get_investments()
        if not investments:
            self.container.controls.append(ft.Text("No investments yet. Add your first one below!", italic=True))
        for inv in investments:
            fv = calculate_future_value(inv)
            def create_handler(investment=inv):
                def handler(e):
                    bs = ft.BottomSheet(
                        ft.Container(
                            ft.Column([
                                ft.ListTile(leading=ft.Icon(ft.Icons.EDIT), title=ft.Text("Edit"),
                                            on_click=lambda _: (edit_investment_dialog(self.page, investment, self.refresh_all), setattr(bs, 'open', False), self.page.update())),
                                ft.ListTile(leading=ft.Icon(ft.Icons.DELETE, color="red"), title=ft.Text("Delete", color="red"),
                                            on_click=lambda _: (delete_investment(self.page, investment, self.refresh_all), setattr(bs, 'open', False), self.page.update())),
                            ], tight=True),
                            padding=20,
                            bgcolor=ft.Colors.ON_SURFACE_VARIANT,
                            border_radius=10,
                        ),
                        open=True,
                        enable_drag=True,
                        is_scroll_controlled=True,
                    )
                    self.page.bottom_sheet = bs
                    self.page.update()
                return handler
            card = ft.Card(
                content=ft.Container(
                    padding=20,
                    bgcolor="#1e1e2e",
                    border_radius=12,
                    content=ft.Column([
                        ft.Text(inv.name, size=22, weight="bold", color="white"),
                        ft.Text(
                            f"Current: R{inv.current_value:,.0f} | +R{inv.monthly_contribution:,.0f}/mo @ {inv.expected_annual_return}%",
                            size=14, color="grey"
                        ),
                        ft.Divider(color="grey"),
                        ft.Text(f"Projected in {inv.target_year}", size=16, color="#00ff88"),
                        money_text(fv, size=36),
                        ft.Text(
                            f"R{fv/1_000_000:.2f} million {'FIRE' if fv >= 10_000_000 else 'on the way'}",
                            size=14, italic=True,
                            color="#00ff88" if fv >= 10_000_000 else "orange"
                        ),
                    ], spacing=10),
                    on_long_press=create_handler(),
                )
            )
            self.container.controls.append(card)
        # Add new investment form
        name = ft.TextField(label="Fund Name (e.g. RA - Discovery)")
        current = ft.TextField(label="Current Value", keyboard_type="number")
        monthly = ft.TextField(label="Monthly Contribution", value="0")
        rate = ft.TextField(label="Expected Return %", value="11")
        year = ft.TextField(label="Target Year", value="2050")
        self.container.controls.append(
            ft.Column([
                ft.Divider(),
                ft.Text("Add / Update Investment", weight="bold"),
                name, current, monthly, rate, year,
                ft.ElevatedButton("Save Investment", on_click=lambda e: self.page.run_task(
                    self.save_investment, name.value, current.value, monthly.value, rate.value, year.value))
            ])
        )
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
            self.page.snack_bar = ft.SnackBar(ft.Text("Saved!"))
            self.page.snack_bar.open = True
            self.page.update()
            await self.refresh()
        except Exception as exc:
            print("Save failed:", exc)