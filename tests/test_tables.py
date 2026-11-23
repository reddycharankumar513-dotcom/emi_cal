"""
Unit tests for Table rendering formatting without dtype collision.
"""

import pytest
import pandas as pd
from calculations.amortization import generate_amortization_schedule
from calculations.part_payment import (
    calculate_revised_schedule_reduce_emi,
    calculate_revised_schedule_reduce_tenure,
)
from calculations.comparison import compare_scenarios
from components.tables import render_comparison_table, render_amortization_table


def test_comparison_table_formatting_no_dtype_error():
    """
    Directly tests that scenario comparison dataframe can be formatted
    without Pandas float64 LossySetitemError or TypeError.
    """
    principal = 1000000.0
    rate = 10.0
    tenure = 60
    sched = generate_amortization_schedule(principal, rate, tenure)
    res_a = calculate_revised_schedule_reduce_emi(principal, rate, tenure, 18, 200000.0)
    res_b = calculate_revised_schedule_reduce_tenure(principal, rate, tenure, 18, 200000.0)
    comp = compare_scenarios(principal, sched, res_a, res_b)

    # Calling render_comparison_table should not throw any exception
    render_comparison_table(comp.summary_df)
