# ui/components/monthly_summary.py
import flet as ft
from src.services.core import svc_get_monthly_summary
from controls.common import money_text

def monthly_summary_table() -> ft.DataTable:
    summaries = svc_get_monthly_summary()  # List of dicts
    rows = []
    for summary in summaries:
        net = summary['income'] - summary['expenses']
        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(summary['month'])),
                ft.DataCell(money_text(summary['income'], size=14)),
                ft.DataCell(money_text(-summary['expenses'], size=14)),  # Show as negative
                ft.DataCell(money_text(net, size=14)),
            ])
        )
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Month")),
            ft.DataColumn(ft.Text("Income")),
            ft.DataColumn(ft.Text("Expenses")),
            ft.DataColumn(ft.Text("Net")),
        ],
        rows=rows,
        border=ft.border.all(1, "grey"),
        heading_row_color="grey200",
    )

def monthly_summary_table_mobile() -> ft.ListView:
    summaries = svc_get_monthly_summary()  # List of dicts
    rows = []
    for summary in summaries:
        net = summary['income'] - summary['expenses']
        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(summary['month'])),
                ft.DataCell(money_text(summary['income'], size=14)),
                ft.DataCell(money_text(-summary['expenses'], size=14)),  # Show as negative
                ft.DataCell(money_text(net, size=14)),
            ])
        )
    return ft.ListView(
        columns=[
            ft.DataColumn(ft.Text("Month")),
            ft.DataColumn(ft.Text("Income")),
            ft.DataColumn(ft.Text("Expenses")),
            ft.DataColumn(ft.Text("Net")),
        ],
        rows=rows,
        border=ft.border.all(1, "grey"),
        heading_row_color="grey200",
    )