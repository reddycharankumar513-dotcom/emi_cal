"""
Unit tests for standard EMI calculation, zero-interest loans,
loan summaries, and input validation.
"""

import pytest
import datetime
from calculations.emi import calculate_emi, calculate_loan_summary
from utils.validation import validate_loan_inputs


def test_standard_emi_calculation():
    """
    Test standard retail loan: ₹10,00,000 at 10% annual interest for 5 years (60 months).
    Theoretical EMI: ₹21,247.04
    """
    principal = 1_000_000.0
    rate = 10.0
    tenure_months = 60

    emi = calculate_emi(principal, rate, tenure_months)
    assert abs(emi - 21247.04) < 0.05


def test_zero_interest_emi_calculation():
    """
    Test 0% interest loan: ₹1,20,000 for 12 months -> EMI = ₹10,000.00 exactly.
    """
    principal = 120_000.0
    rate = 0.0
    tenure_months = 12

    emi = calculate_emi(principal, rate, tenure_months)
    assert emi == 10000.0


def test_invalid_loan_inputs():
    """
    Ensure proper exceptions are raised for out-of-bound inputs.
    """
    # Negative or zero loan amount
    with pytest.raises(ValueError, match="Loan amount must be greater than zero"):
        calculate_emi(0, 10.0, 60)

    with pytest.raises(ValueError, match="Loan amount must be greater than zero"):
        calculate_emi(-50000, 10.0, 60)

    # Negative interest rate
    with pytest.raises(ValueError, match="Annual interest rate cannot be negative"):
        calculate_emi(500000, -2.5, 60)

    # Zero or negative tenure
    with pytest.raises(ValueError, match="Loan tenure must be at least 1 month"):
        calculate_emi(500000, 10.0, 0)

    with pytest.raises(ValueError, match="Loan tenure must be at least 1 month"):
        calculate_emi(500000, 10.0, -12)


def test_loan_summary_generation():
    """
    Verify complete loan summary generation including calendar completion date.
    """
    start_date = datetime.date(2025, 1, 1)
    summary = calculate_loan_summary(
        loan_amount=1_000_000.0,
        annual_rate=10.0,
        tenure_years=5,
        tenure_months_extra=0,
        start_date=start_date
    )

    assert summary.loan_amount == 1_000_000.0
    assert summary.annual_rate == 10.0
    assert summary.tenure_months == 60
    assert summary.monthly_emi == 21247.04
    assert summary.monthly_interest_rate == round(10.0 / 12, 4)
    assert summary.start_date == start_date
    assert summary.completion_date == datetime.date(2030, 1, 1)
    assert summary.total_repayment > summary.loan_amount
    assert summary.total_interest > 0


def test_validation_utility():
    """Test validation utility helper."""
    assert validate_loan_inputs(100000, 8.5, 3, 0).is_valid
    assert not validate_loan_inputs(-100, 8.5, 3, 0).is_valid
    assert not validate_loan_inputs(100000, -1.0, 3, 0).is_valid
    assert not validate_loan_inputs(100000, 8.5, 0, 0).is_valid
