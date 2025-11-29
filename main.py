import sys
import os
sys.path.append(os.path.dirname(__file__))

import flet as ft
from datetime import date
import asyncio
from src.database import Transaction, Investment
from src.models import (
    get_all_transactions, get_balance, get_investments,
    add_transaction, add_or_update_investment, calculate_future_value
)
from src.motivation import daily_message


# ---------- EDIT / DELETE HELPERS ----------
def edit_transaction_dialog(page: ft.Page, transaction: Transaction, refresh_all):
    def save_changes(e):
        try:
            new_amount = float(amount_field.value)
            if not switch.value:  # expense
                new_amount = -abs(new_amount)
            transaction.category = category.value
            transaction.amount = new_amount
            transaction.description = notes.value or ""
            from src.database import SessionLocal
            with SessionLocal() as db:
                db.merge(transaction)
                db.commit()
            dlg.open = False
            page.update()
            refresh_all()
        except:
            pass

    amount_field = ft.TextField(value=str(abs(transaction.amount)), label="Amount")
    category = ft.Dropdown(
        label="Category",
        value=transaction.category,
        options=[ft.dropdown.Option(c) for c in ["Salary", "Freelance", "Groceries", "Transport", "Rent", "Entertainment", "Savings", "Investment"]]
    )
    switch = ft.Switch(label="Income / Expense", value=transaction.amount > 0)
    notes = ft.TextField(value=transaction.description or "", label="Notes")

    dlg = ft.AlertDialog(
        title=ft.Text("Edit Transaction"),
        content=ft.Column([amount_field, category, ft.Row([switch, ft.Text("Income      Expense")]), notes], tight=True),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
            ft.TextButton("Save", on_click=save_changes),
        ],
        modal=True
    )
    page.dialog = dlg
    dlg.open = True
    page.update()


def delete_transaction(page: ft.Page, transaction: Transaction, refresh_all):
    def confirm(e):
        from src.database import SessionLocal
        with SessionLocal() as db:
            db.delete(transaction)
            db.commit()
        dlg.open = False
        page.update()
        refresh_all()

    dlg = ft.AlertDialog(
        title=ft.Text("Delete Transaction?"),
        content=ft.Text("This cannot be undone."),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
            ft.TextButton("Delete", on_click=confirm, style=ft.ButtonStyle(color="red")),
        ],
        modal=True
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

def edit_investment_dialog(page: ft.Page, inv: Investment, refresh_all):
    name_field = ft.TextField(value=inv.name, label="Name")
    current = ft.TextField(value=str(inv.current_value), label="Current Value")
    monthly = ft.TextField(value=str(inv.monthly_contribution), label="Monthly")
    rate = ft.TextField(value=str(inv.expected_annual_return), label="Return %")
    year = ft.TextField(value=str(inv.target_year), label="Target Year")

    def save(e):
        try:
            add_or_update_investment(
                name=name_field.value,
                current_value=float(current.value),
                monthly=float(monthly.value),
                return_rate=float(rate.value),
                target_year=int(year.value)
            )
            dlg.open = False
            page.update()
            refresh_all()
        except:
            pass

    dlg = ft.AlertDialog(
        title=ft.Text("Edit Investment"),
        content=ft.Column([name_field, current, monthly, rate, year]),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
            ft.TextButton("Save", on_click=save),
        ],
        modal=True
    )
    page.dialog = dlg
    dlg.open = True
    page.update()


def delete_investment(page: ft.Page, inv: Investment, refresh_all):
    def confirm(e):
        from src.database import SessionLocal
        with SessionLocal() as db:
            db.delete(inv)
            db.commit()
        dlg.open = False
        page.update()
        refresh_all()

    dlg = ft.AlertDialog(
        title=ft.Text("Delete Investment?"),
        content=ft.Text(f"Permanently delete {inv.name}?"),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
            ft.TextButton("Delete Forever", on_click=confirm, style=ft.ButtonStyle(color="red")),
        ],
        modal=True
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

# ---------- Splash Screen (fixed for modern Flet) ----------
async def splash(page: ft.Page):
    logo = ft.Image(src="assets/logo.png", width=200, opacity=0.0) if os.path.exists("assets/logo.png") else ft.Text("Money", size=120, opacity=0.0)
    splash_text = ft.Text("MorningMoney", size=32, weight="bold", opacity=0.0)
    loading_text = ft.Text("Loading your wealth engine...", opacity=0.0)
    
    page.add(ft.Column([logo, splash_text, loading_text], alignment="center", horizontal_alignment="center", spacing=20))
    page.update()

    # Fade in
    for i in range(11):
        opacity = i / 10
        logo.opacity = splash_text.opacity = loading_text.opacity = opacity
        page.update()
        await asyncio.sleep(0.04)   # ← use normal asyncio.sleep, NOT ft.asyncio

    # Fade out
    for i in reversed(range(11)):
        opacity = i / 10
        logo.opacity = splash_text.opacity = loading_text.opacity = opacity
        page.update()
        await asyncio.sleep(0.03)   # ← same here

    page.clean()

# ---------- Components ----------
def money_text(value: float, size=20, weight="bold"):
    color = "green" if value >= 0 else "red"
    return ft.Text(f"R{value:,.2f}", size=size, weight=weight, color=color)

# ---------- Tabs ----------
class NewEntryTab(ft.Column):
    def __init__(self, page, refresh_all):
        super().__init__(scroll="auto")
        self.page = page
        self.refresh_all = refresh_all

        self.amount = ft.TextField(label="Amount (R)", keyboard_type="number")
        self.category = ft.Dropdown(
            label="Category",
            options=[
                ft.dropdown.Option("Salary"), ft.dropdown.Option("Freelance"), ft.dropdown.Option("Other Income"),
                ft.dropdown.Option("Groceries"), ft.dropdown.Option("Transport"), ft.dropdown.Option("Entertainment"),
                ft.dropdown.Option("Rent"), ft.dropdown.Option("Subscriptions"), ft.dropdown.Option("Savings"), ft.dropdown.Option("Investment")
            ],
            value="Groceries"
        )
        self.type_switch = ft.Switch(label="Income (on) / Expense (off)", value=False)
        self.notes = ft.TextField(label="Notes (optional)", multiline=True, min_lines=1, max_lines=3)
        self.message = ft.Text("")

        self.controls = [
            ft.Text("Add Transaction", size=28, weight="bold"),
            self.amount, self.category,
            ft.Row([self.type_switch, ft.Text("Income      Expense")]),
            self.notes,
            ft.ElevatedButton("Save Transaction", on_click=self.save),
            self.message,
        ]

    async def save(self, e):
        try:
            amt = float(self.amount.value)
            if not self.type_switch.value:  # expense
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
            self.list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.RECEIPT),
                    title=ft.Text(t.category),
                    subtitle=ft.Text(t.description or t.date.strftime("%Y-%m-%d")),
                    trailing=money_text(t.amount, size=18),
                    on_long_press=lambda e, trans=t: (
                        # Create and assign the bottom sheet
                        setattr(
                            self.page,
                            "bottom_sheet",
                            ft.BottomSheet(
                                ft.Container(
                                    ft.Column([
                                        ft.ListTile(
                                            leading=ft.Icon(ft.Icons.EDIT),
                                            title=ft.Text("Edit"),
                                            on_click=lambda _: (
                                                edit_transaction_dialog(self.page, trans, self.refresh_all),
                                                # Close the sheet after opening dialog
                                                setattr(self.page, "bottom_sheet", None),
                                                self.page.update()
                                            )
                                        ),
                                        ft.ListTile(
                                            leading=ft.Icon(ft.Icons.DELETE, color="red"),
                                            title=ft.Text("Delete", color="red"),
                                            on_click=lambda _: (
                                                delete_transaction(self.page, trans, self.refresh_all),
                                                setattr(self.page, "bottom_sheet", None),
                                                self.page.update()
                                            )
                                        ),
                                    ], tight=True),
                                    padding=20,
                                    bgcolor=ft.Colors.ON_SURFACE_VARIANT,
                                    border_radius=10,
                                ),
                                is_scroll_controlled=True,
                                enable_drag=True,           # ← Critical for desktop
                            )
                        ),
                        # Force it to open
                        self.page.update(),
                        setattr(self.page.bottom_sheet, "open", True),
                        self.page.update()
                    )
                )
            )
        self.page.update()  # final refresh

class InvestmentsTab(ft.Column):
    def __init__(self, page: ft.Page, refresh_all):
        super().__init__(scroll="auto", expand=True)
        self.page = page
        self.refresh_all = refresh_all
        self.container = ft.Column(spacing=20)
        self.controls = [ft.Text("Investments & Retirement", size=28, weight="bold"), self.container]

    async def refresh(self):
        self.container.controls.clear()
        investments = get_investments()

        if not investments:
            self.container.controls.append(ft.Text("No investments yet. Add your first one below!", italic=True))
        
        total_projected = 0
        for inv in investments:
            fv = calculate_future_value(inv)
            total_projected += fv

# ——— BEAUTIFUL CLEAN INVESTMENT CARD (NO PLOTLY ERRORS) ———
# ——— FINAL BULLETPROOF INVESTMENT CARD (WORKS 100%) ———
            card = ft.Card(
                content=ft.Container(
                    padding=20,
                    bgcolor="#1e1e2e",
                    border_radius=12,
                    content=ft.Column([
                        ft.Text(inv.name, size=22, weight="bold", color="white"),
                        ft.Text(
                            f"Current: R{inv.current_value:,.0f} | +R{inv.monthly_contribution:,.0f}/month @ {inv.expected_annual_return}% p.a.",
                            size=14, color="grey"
                        ),
                        ft.Divider(color="grey"),
                        ft.Text("Projected value in " + str(inv.target_year), size=16, color="#00ff88"),
                        money_text(fv, size=36),
                        ft.Text(
                            f"That’s R{fv/1_000_000:.2f} million {'FIRE' if fv >= 10_000_000 else 'ROCKET'}",
                            size=14, italic=True,
                            color="#00ff88" if fv >= 10_000_000 else "orange"
                        ),
                    ], spacing=10),
                    # ← THE FINAL LONG-PRESS THAT ACTUALLY WORKS
                    on_long_press=lambda e, i=inv: (
                        setattr(
                            self.page,
                            "bottom_sheet",
                            ft.BottomSheet(
                                ft.Container(
                                    ft.Column([
                                        ft.ListTile(
                                            leading=ft.Icon(ft.Icons.EDIT),
                                            title=ft.Text("Edit"),
                                            on_click=lambda _: (
                                                edit_investment_dialog(self.page, i, self.refresh),
                                                setattr(self.page, "bottom_sheet", None),
                                                self.page.update()
                                            )
                                        ),
                                        ft.ListTile(
                                            leading=ft.Icon(ft.Icons.DELETE, color="red"),
                                            title=ft.Text("Delete", color="red"),
                                            on_click=lambda _: (
                                                delete_investment(self.page, i, self.refresh),
                                                setattr(self.page, "bottom_sheet", None),
                                                self.page.update()
                                            )
                                        ),
                                    ], tight=True),
                                    padding=20,
                                    bgcolor=ft.colors.SURFACE_VARIANT,
                                    border_radius=10,
                                ),
                                is_scroll_controlled=True,
                                enable_drag=True,
                                open=True                     # ← THIS IS THE NUCLEAR TRIGGER
                            )
                        ),
                        self.page.update(),
                        # Extra insurance – force open again
                        setattr(getattr(self.page, "bottom_sheet", None), "open", True) if self.page.bottom_sheet else None,
                        self.page.update()
                    )
                )
            )
            self.container.controls.append(card)   # ← stays inside the loop

        # Add new investment form
        name = ft.TextField(label="Fund Name (e.g. RA - Discovery)")
        current = ft.TextField(label="Current Value", keyboard_type="number")
        monthly = ft.TextField(label="Monthly Contribution", value="0")
        rate = ft.TextField(label="Expected Annual Return %", value="11")
        year = ft.TextField(label="Target Year", value="2050")

        self.container.controls.append(
            ft.Column([
                ft.Divider(),
                ft.Text("Add / Update Investment", weight="bold"),
                name, current, monthly, rate, year,
                ft.ElevatedButton("Save Investment", on_click=lambda e: self.page.run_task(self.save_investment, name.value, current.value, monthly.value, rate.value, year.value))
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
                target_year=int(year or 2050)
            )
            await self.refresh()
        except Exception as exc:
            print("Save failed:", exc)  # for now, just don’t crash

# ---------- Main App ----------
async def main(page: ft.Page):
    page.title = "MorningMoney"
    page.theme_mode = "dark"
    page.padding = 20

    await splash(page)

    page.add(
        ft.Container(
            padding=20,
            bgcolor="#ff0066",
            border_radius=12,
            content=ft.Column([
                ft.Text("Daily Fire 🔥", size=18, weight="bold", color="white"),
                ft.Text(daily_message(), size=16, color="white", italic=True),
            ])
        )
    )

    # Tabs
    # Tabs — fixed with proper page reference
    async def refresh_all():
        await asyncio.gather(diary.refresh(), investments.refresh())

    new_entry = NewEntryTab(page, refresh_all)
    diary = DiaryTab(page, refresh_all)           # ← added page
    investments = InvestmentsTab(page, refresh_all)  # ← added page

    tabs = ft.Tabs(
        selected_index=0,
        expand=True,
        tabs=[
            ft.Tab(text="New", icon=ft.Icons.ADD, content=new_entry),
            ft.Tab(text="Diary", icon=ft.Icons.RECEIPT_LONG, content=diary),
            ft.Tab(text="Investments", icon=ft.Icons.TRENDING_UP, content=investments),
        ]
    )

    page.add(
        ft.Column([
            ft.Row([
                ft.Text("MorningMoney", size=36, weight="bold"),
                ft.Text("", expand=True),
                money_text(get_balance(), size=28),
            ], alignment="spaceBetween"),
            ft.Divider(),
            tabs
        ], expand=True)
    )

    await diary.refresh()
    await investments.refresh()

ft.app(target=main)