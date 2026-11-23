"""
Unit tests for part-payment calculations:
- Option A: EMI Reduction
- Option B: Tenure Reduction
- Multiple Prepayments & Recurring Prepayments
- Foreclosure simulation
- Strict verification that both options share identical history up to the prepayment month.
"""

import pytest
import datetime
from calculations.part_payment import (
    calculate_revised_schedule_reduce_emi,
    calculate_revised_schedule_reduce_tenure,
    calculate_custom_prepayment_schedule,
    get_outstanding_balance_after_month,
)
from calculations.amortization import generate_amortization_schedule


def test_part_payment_example_from_specification():
    """
    Test exact prompt specification:
    Original loan: ₹10,00,000, 10% interest, 5 years (60 months).
    Part-payment: ₹2,00,000 at month 18.
    """
    principal = 1_000_000.0
    rate = 10.0
    tenure = 60
    prep_month = 18
    prep_amount = 200_000.0

    # 1. Outstanding balance check
    orig_schedule = generate_amortization_schedule(principal, rate, tenure)
    balance_m18 = float(orig_schedule[orig_schedule["Month"] == 18]["Closing Balance"].iloc[0])
    assert balance_m18 > prep_amount

    # 2. Option A: Reduce EMI
    result_a = calculate_revised_schedule_reduce_emi(
        principal=principal,
        annual_rate=rate,
        tenure_months=tenure,
        part_payment_month=prep_month,
        part_payment_amount=prep_amount
    )

    # Tenure remains 60 months
    assert result_a.revised_tenure_months == 60
    assert result_a.tenure_reduction_months == 0
    # EMI is reduced
    assert result_a.revised_emi < result_a.original_emi
    assert result_a.emi_reduction_amount > 0
    assert result_a.emi_reduction_pct > 0
    # Interest is saved
    assert result_a.interest_saved > 0
    # Final balance is 0.00
    assert result_a.revised_schedule["Closing Balance"].iloc[-1] == 0.0

    # 3. Option B: Reduce Tenure
    result_b = calculate_revised_schedule_reduce_tenure(
        principal=principal,
        annual_rate=rate,
        tenure_months=tenure,
        part_payment_month=prep_month,
        part_payment_amount=prep_amount
    )

    # EMI remains unchanged
    assert result_b.revised_emi == result_b.original_emi
    # Tenure is reduced
    assert result_b.revised_tenure_months < 60
    assert result_b.tenure_reduction_months > 0
    assert result_b.emis_eliminated > 0
    # Interest is saved
    assert result_b.interest_saved > 0
    # Option B tenure reduction saves even more interest than Option A
    assert result_b.interest_saved > result_a.interest_saved
    # Final balance is 0.00
    assert result_b.revised_schedule["Closing Balance"].iloc[-1] == 0.0

    # 4. Strict requirement: Both options use the exact same balance after part-payment
    assert result_a.balance_after_part_payment == result_b.balance_after_part_payment
    assert result_a.balance_after_part_payment == round(balance_m18 - prep_amount, 2)

    # 5. Strict requirement: Both options share identical history up to month 18
    sched_a = result_a.revised_schedule
    sched_b = result_b.revised_schedule
    for m in range(1, prep_month):
        row_a = sched_a[sched_a["Month"] == m].iloc[0]
        row_b = sched_b[sched_b["Month"] == m].iloc[0]
        assert row_a["Opening Balance"] == row_b["Opening Balance"]
        assert row_a["EMI"] == row_b["EMI"]
        assert row_a["Interest"] == row_b["Interest"]
        assert row_a["Principal"] == row_b["Principal"]
        assert row_a["Closing Balance"] == row_b["Closing Balance"]


def test_prepayment_exceeding_balance_raises_error():
    """Verify that part-payments greater than the outstanding balance are rejected."""
    principal = 500_000.0
    rate = 10.0
    tenure = 36

    # Attempt prepayment greater than loan principal
    with pytest.raises(ValueError, match="exceeds outstanding principal"):
        calculate_revised_schedule_reduce_emi(
            principal=principal,
            annual_rate=rate,
            tenure_months=tenure,
            part_payment_month=12,
            part_payment_amount=600_000.0
        )


def test_full_loan_foreclosure():
    """
    Test complete loan payoff / foreclosure at month 12.
    """
    principal = 1_000_000.0
    rate = 9.0
    tenure = 60
    
    orig_sched = generate_amortization_schedule(principal, rate, tenure)
    balance_m12 = float(orig_sched[orig_sched["Month"] == 12]["Closing Balance"].iloc[0])

    # Prepay full remaining balance
    result_foreclose = calculate_revised_schedule_reduce_tenure(
        principal=principal,
        annual_rate=rate,
        tenure_months=tenure,
        part_payment_month=12,
        part_payment_amount=balance_m12
    )

    # Tenure reduced to 12 months
    assert result_foreclose.revised_tenure_months == 12
    assert result_foreclose.tenure_reduction_months == 48
    assert result_foreclose.revised_schedule["Closing Balance"].iloc[-1] == 0.0
    assert result_foreclose.interest_saved > 0


def test_multiple_part_payments():
    """
    Test custom multi-prepayment schedule (e.g. extra ₹50k at months 12, 24, 36).
    """
    principal = 1_000_000.0
    rate = 10.0
    tenure = 60
    prepayments = {12: 50_000.0, 24: 50_000.0, 36: 50_000.0}

    result = calculate_custom_prepayment_schedule(
        principal=principal,
        annual_rate=rate,
        tenure_months=tenure,
        prepayments=prepayments
    )

    assert result.total_prepayment_paid == 150_000.0
    assert result.revised_tenure_months < 60
    assert result.interest_saved > 0
    assert result.revised_schedule["Closing Balance"].iloc[-1] == 0.0
