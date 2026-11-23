"""
Unit tests for Plotly Chart generation.
Ensures no invalid property errors (such as titlefont) in Plotly 7.1.0.
"""

import pytest
import pandas as pd
from calculations.amortization import generate_amortization_schedule
from calculations.part_payment import (
    calculate_revised_schedule_reduce_emi,
    calculate_revised_schedule_reduce_tenure,
)
from calculations.comparison import compare_scenarios
from components.charts import (
    render_balance_chart,
    render_monthly_split_chart,
    render_total_pie_chart,
    render_cumulative_chart,
    render_scenario_comparison_chart,
    render_interest_savings_chart,
)


def test_all_chart_renderers_success():
    """Verify that all charts render without layout/property validation errors."""
    principal = 1000000.0
    rate = 10.0
    tenure = 60
    sched = generate_amortization_schedule(principal, rate, tenure)
    res_a = calculate_revised_schedule_reduce_emi(principal, rate, tenure, 18, 200000.0)
    res_b = calculate_revised_schedule_reduce_tenure(principal, rate, tenure, 18, 200000.0)
    comp = compare_scenarios(principal, sched, res_a, res_b)

    # 1. Balance chart
    fig1 = render_balance_chart(sched)
    assert fig1 is not None

    # 2. Monthly split chart (Principal vs Interest)
    fig2 = render_monthly_split_chart(sched)
    assert fig2 is not None

    # 3. Total pie chart
    fig3 = render_total_pie_chart(principal, 200000.0, 50000.0)
    assert fig3 is not None

    # 4. Cumulative chart
    fig4 = render_cumulative_chart(sched)
    assert fig4 is not None

    # 5. Scenario comparison chart
    fig5 = render_scenario_comparison_chart(sched, res_a.revised_schedule, res_b.revised_schedule)
    assert fig5 is not None

    # 6. Interest savings chart
    fig6 = render_interest_savings_chart(comp.summary_df)
    assert fig6 is not None
