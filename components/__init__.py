"""
Components Package
Reusable UI components, interactive Plotly charts, data tables, sidebar controls,
and report generation cards.
"""

from .charts import (
    render_monthly_split_chart,
    render_total_pie_chart,
    render_balance_chart,
    render_cumulative_chart,
    render_scenario_comparison_chart,
    render_interest_savings_chart,
)
from .tables import render_amortization_table, render_comparison_table
from .sidebar import render_sidebar
from .dashboard import render_dashboard_view
from .reports import render_reports_view

__all__ = [
    "render_monthly_split_chart",
    "render_total_pie_chart",
    "render_balance_chart",
    "render_cumulative_chart",
    "render_scenario_comparison_chart",
    "render_interest_savings_chart",
    "render_amortization_table",
    "render_comparison_table",
    "render_sidebar",
    "render_dashboard_view",
    "render_reports_view",
]
