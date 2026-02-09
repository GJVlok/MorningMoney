# ui/components/monthly_summary.py
import flet as ft
import csv
from decimal import Decimal
from src.services.core import svc_get_monthly_summary
from controls.common import money_text

def get_monthly_summary_view(page: ft.Page):
    # Returns a container with the Desktop table and a Download button
    # 1. Setup FilePicker for saving CSV
    def on_save_result(e: ft.FilePickerResultEvent):
        if e.path:
            summaries = svc_get_monthly_summary()
            try:
                with open(e.path, "w", newline="") as f:
                    writer = csv.writer(f)
                    # Header row
                    writer.writerow(["Month", "Income", "Expenses", "Net"])

                    for s in summaries:
                        inc = Decimal(str(s['income']))
                        exp = Decimal(str(str['expenses']))
                        net = inc - exp
                        # Write row with formatted Decimals
                        writer.writerow([
                            s['month'],
                            f"{inc:.2f}",
                            f"{exp:.2f}",
                            f"{net:.2f}"
                        ])
                page.show_snack(f"Exported to {e.path}", "green")
            except Exception as ex:
                page.show_snack(f"Export failed: {str(ex)}", "red")

    file_picker = ft.FilePicker(on_result=on_save_result)
    page.overlay.append(file_picker)

    # 2. Build the DataTable (using your Decimal principles)
    def build_table():
        summaries = svc_get_monthly_summary()
        rows = []
        for s in summaries:
            inc = Decimal(str(s['income']))
            exp = Decimal(str(s['expenses']))
            net = inc - exp
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(s['month'])),
                ft.DataCell(ft.Text(f"R{inc:,.2f}", color="green")),
                ft.DataCell(ft.Text(f"R{-exp:,.2f}", color="red")),
                ft.DataCell(ft.Text(f"R{net:,.2f}", weight="bold"))
            ]))

        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Month")),
                ft.DataColumn(ft.Text("Income"), numeric=True),
                ft.DataColumn(ft.Text("Expenses"), numeric=True),
                ft.DataColumn(ft.Text("Net Balance"), numeric=True),
            ],
            rows=rows,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            column_spacing=50
        )
    
    # 3. Main Layout with Download Button
    return ft.Column([
        ft.Row([
            ft.Text("Monthly Financial Summary", size=24, weight="bold"),
            ft.ElevatedButton(
                "Download CSV",
                icon=ft.Icons.DOWNLOAD,
                on_click=lambda _: file_picker.save_file(
                    file_name="monthly_summary.csv",
                    allowed_extensions=["csv"]
                )
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        build_table()
    ], spacing=20, expand=True)

def monthly_summary_table() -> ft.DataTable:
    # 1. Fetch summaries (List of dicts containing Decimal objects)
    summaries = svc_get_monthly_summary()
    rows = []

    for summary in summaries:
        # 2. Ensure Decimal math for the Net column
        income = Decimal(str(summary.get('income', '0.00')))
        expenses = Decimal(str(summary.get('expenses', '0.00')))
        net = income - expenses

        rows.append(
            ft.DataRow(cells=[
                # Month string
                ft.DataCell(ft.Text(summary['month'], weight="w500")),
                
                # Income
                ft.DataCell(money_text(income, size=14)),
                
                # Expenses (Shown as negative)
                ft.DataCell(money_text(-expenses, size=14)),
                
                # Net Balance
                ft.DataCell(money_text(net, size=14, weight="bold")),
            ])
        )

    # 3. Return a styled DataTable with numeric alignment
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Month", weight="bold")),
            ft.DataColumn(ft.Text("Income", weight="bold"), numeric=True),
            ft.DataColumn(ft.Text("Expenses", weight="bold"), numeric=True),
            ft.DataColumn(ft.Text("Net Profit/Loss", weight="bold"), numeric=True),
        ],
        rows=rows,
        # Styling for Desktop
        heading_row_color=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE),
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        horizontal_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        column_spacing=40, # Added spacing for wider screens
    )

def monthly_summary_mobile() -> ft.ListView:
    summaries = svc_get_monthly_summary()  # List of dicts
    
    # We use a ListView so the user can scroll through the months easily
    lv = ft.ListView(expand=True, spacing=10, padding=10)

    if not summaries:
        lv.controls.append(ft.Text("No data available yet.", italic=True, text_align="center"))
        return lv

    for summary in summaries:
        # Calculate Net using Decimal math
        income = Decimal(str(summary.get('income', 0)))
        expenses = Decimal(str(summary.get('expenses', 0)))
        net = income - expenses

        # Create a "Card" for each month
        month_card = ft.Container(
            content=ft.Column([
                # Header: Month and Net Balance
                ft.Row([
                    ft.Text(summary['month'], size=18, weight="bold"),
                    money_text(net, size=18)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(height=1, color="white24"),
                
                # Details: Income and Expenses
                ft.Row([
                    ft.Column([
                        ft.Text("Income", size=12, color="grey"),
                        money_text(income, size=16),
                    ], horizontal_alignment="start"),
                    
                    ft.Column([
                        ft.Text("Expenses", size=12, color="grey"),
                        # Show expenses as negative for visual clarity
                        money_text(-expenses, size=16),
                    ], horizontal_alignment="end"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=8),
            padding=15,
            border_radius=10,
            border=ft.border.all(1, "white10"),
            bgcolor=ft.colors.SURFACE_VARIANT,
        )
        
        lv.controls.append(month_card)

    return lv