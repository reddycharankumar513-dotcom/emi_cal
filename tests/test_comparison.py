"""
Unit tests for Scenario Comparison Engine.
Verifies integrity of side-by-side matrices, calculations, and custom scenario additions.
"""

import pytest
from calculations.amortization import generate_amortization_schedule
from calculations.part_payment import (
    calculate_revised_schedule_reduce_emi,
    calculate_revised_schedule_reduce_tenure,
)
from calculations.comparison import compare_scenarios


def test_scenario_comparison_metrics():
    """
    Verify structure and calculations in Scenario Comparison dataframe.
    """
    principal = 1_000_000.0
    rate = 10.0
    tenure = 60
    prep_month = 18
    prep_amount = 200_000.0

    orig_sched = generate_amortization_schedule(principal, rate, tenure)
    res_a = calculate_revised_schedule_reduce_emi(principal, rate, tenure, prep_month, prep_amount)
    res_b = calculate_revised_schedule_reduce_tenure(principal, rate, tenure, prep_month, prep_amount)

    comp = compare_scenarios(principal, orig_sched, res_a, res_b)

    df = comp.summary_df
    assert not df.empty
    assert "Metric" in df.columns
    assert "Original Loan" in df.columns
    assert "Option A: Reduce EMI" in df.columns
    assert "Option B: Reduce Tenure" in df.columns

    # Check key metrics exist
    metrics_list = list(df["Metric"])
    assert "Monthly EMI" in metrics_list
    assert "Total Interest Saved" in metrics_list
    assert "Total Repayment Amount" in metrics_list
    assert "Tenure Reduction (Months)" in metrics_list

    # Ensure Option B saved interest > 0
    opt_b_saved = df[df["Metric"] == "Total Interest Saved"]["Option B: Reduce Tenure"].iloc[0]
    assert opt_b_saved > 0
