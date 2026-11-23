"""
Input Validation and Boundary Enforcement Module.
Ensures rigorous domain validation for monetary amounts, interest rates,
loan tenures, and prepayment constraints.
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ValidationResult:
    """Encapsulates validation outcome."""
    is_valid: bool
    error_message: Optional[str] = None


def validate_loan_inputs(
    loan_amount: float,
    annual_rate: float,
    tenure_years: int,
    tenure_months: int = 0
) -> ValidationResult:
    """
    Validates core loan setup parameters.
    """
    if loan_amount is None or loan_amount <= 0:
        return ValidationResult(
            is_valid=False,
            error_message="Loan amount must be a positive number greater than 0."
        )

    if loan_amount > 1_000_000_000:  # 100 Crore upper sanity bound
        return ValidationResult(
            is_valid=False,
            error_message="Loan amount exceeds maximum simulation limit (₹100 Crore)."
        )

    if annual_rate is None or annual_rate < 0:
        return ValidationResult(
            is_valid=False,
            error_message="Annual interest rate cannot be negative."
        )

    if annual_rate > 100:
        return ValidationResult(
            is_valid=False,
            error_message="Annual interest rate cannot exceed 100% per annum."
        )

    if tenure_years is None or tenure_years < 0:
        return ValidationResult(
            is_valid=False,
            error_message="Tenure years cannot be negative."
        )

    if tenure_months is None or tenure_months < 0:
        return ValidationResult(
            is_valid=False,
            error_message="Additional tenure months cannot be negative."
        )

    total_months = (tenure_years * 12) + tenure_months
    if total_months <= 0:
        return ValidationResult(
            is_valid=False,
            error_message="Total loan tenure must be at least 1 month."
        )

    if total_months > 600:  # 50 years sanity limit
        return ValidationResult(
            is_valid=False,
            error_message="Total loan tenure cannot exceed 50 years (600 months)."
        )

    return ValidationResult(is_valid=True)


def validate_part_payment_inputs(
    part_payment_month: int,
    part_payment_amount: float,
    current_outstanding_balance: float,
    total_tenure_months: int
) -> ValidationResult:
    """
    Validates prepayment month and amount against the loan balance and duration.
    """
    if part_payment_month is None or part_payment_month < 1:
        return ValidationResult(
            is_valid=False,
            error_message="Part-payment month must be at least 1."
        )

    if part_payment_month >= total_tenure_months:
        return ValidationResult(
            is_valid=False,
            error_message=(
                f"Part-payment month ({part_payment_month}) must be strictly less than the "
                f"loan tenure ({total_tenure_months} months)."
            )
        )

    if part_payment_amount is None or part_payment_amount <= 0:
        return ValidationResult(
            is_valid=False,
            error_message="Part-payment amount must be greater than zero."
        )

    if part_payment_amount > current_outstanding_balance:
        return ValidationResult(
            is_valid=False,
            error_message=(
                f"Part-payment amount (₹{part_payment_amount:,.2f}) cannot exceed the "
                f"outstanding principal balance (₹{current_outstanding_balance:,.2f}) at month {part_payment_month}."
            )
        )

    return ValidationResult(is_valid=True)
