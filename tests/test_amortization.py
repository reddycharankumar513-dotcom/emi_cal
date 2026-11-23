"""
Unit tests for amortization schedule generation, final EMI adjustments,
zero final balance guarantees, and conservation of principal.
"""

import pytest
import datetime
from calculations.amortization import generate_amortization_schedule
from calculations.interest import calculate_monthly_interest


def test_amortization_schedule_integrity():
    """
    Verify complete conservation principles for standard amortization:
    1. Total principal repaid == initial principal.
    2. Final closing balance == 0.00 exactly.
    3. No negative balances at any point.
    4. Month count matches scheduled tenure.
    """
    principal = 1_000_000.0
    rate = 10.0
    tenure = 60

    df = generate_amortization_schedule(
        principal=principal,
        annual_rate=rate,
        tenure_months=tenure,
        start_date=datetime.date(2025, 1, 1)
    )

    assert len(df) == tenure
    # Balance never negative
    assert (df["Closing Balance"] >= 0).all()
    # Final closing balance is exactly 0.00
    assert df["Closing Balance"].iloc[-1] == 0.0
    # Sum of principal components equals original loan principal
    assert round(df["Total Principal"].sum(), 2) == round(principal, 2)
    # Total repayment equals principal + total interest
    total_interest = df["Interest"].sum()
    total_repaid = df["EMI"].sum()
    assert abs(total_repaid - (principal + total_interest)) < 0.05


def test_zero_interest_amortization():
    """
    Verify amortization for 0% loan:
    - Interest is 0 in all months.
    - Principal per month equals EMI.
    - Final balance is 0.00.
    """
    principal = 60_000.0
    rate = 0.0
    tenure = 6

    df = generate_amortization_schedule(
        principal=principal,
        annual_rate=rate,
        tenure_months=tenure
    )

    assert len(df) == 6
    assert (df["Interest"] == 0.0).all()
    assert (df["Principal"] == 10000.0).all()
    assert df["Closing Balance"].iloc[-1] == 0.0
    assert df["Total Principal"].sum() == 60000.0


def test_final_emi_adjustment():
    """
    Verify that slight fractional cent discrepancies in reducing balance
    are absorbed into the final EMI so that closing balance is exactly 0.00.
    """
    # A loan with odd numbers that causes repeating decimals
    principal = 333_333.33
    rate = 9.73
    tenure = 37

    df = generate_amortization_schedule(
        principal=principal,
        annual_rate=rate,
        tenure_months=tenure
    )

    assert df["Closing Balance"].iloc[-1] == 0.0
    assert round(df["Total Principal"].sum(), 2) == round(principal, 2)


def test_daily_reducing_convention():
    """
    Verify daily reducing balance calculation produces valid schedule.
    """
    principal = 500_000.0
    rate = 8.5
    tenure = 24
    start_date = datetime.date(2025, 1, 1)

    df = generate_amortization_schedule(
        principal=principal,
        annual_rate=rate,
        tenure_months=tenure,
        start_date=start_date,
        convention="daily_reducing"
    )

    assert len(df) == tenure
    assert df["Closing Balance"].iloc[-1] == 0.0
    assert round(df["Total Principal"].sum(), 2) == round(principal, 2)
