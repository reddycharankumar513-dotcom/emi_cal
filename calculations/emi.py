"""
Loan EMI Calculation Engine.
Implements the reducing-balance EMI formula, zero-interest calculations,
and high-level loan summary generation.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
import datetime
from .interest import add_months, round_monetary


@dataclass
class LoanSummary:
    """Represents a high-level summary of the loan calculation."""
    loan_amount: float
    annual_rate: float
    tenure_months: int
    tenure_years: float
    monthly_emi: float
    monthly_interest_rate: float  # Percentage per month (e.g., 0.833%)
    total_interest: float
    total_repayment: float
    interest_to_principal_ratio: float  # (Total Interest / Principal) * 100
    start_date: Optional[datetime.date]
    completion_date: Optional[datetime.date]
    method: str


def calculate_emi(
    loan_amount: float | Decimal,
    annual_rate: float | Decimal,
    tenure_months: int,
    rounding_mode: str = "standard"
) -> float:
    """
    Calculate the monthly Equated Monthly Installment (EMI) using the reducing-balance formula:
    
        EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
        
    Where:
        P = Principal loan amount
        r = Monthly interest rate = Annual Rate / (12 * 100)
        n = Tenure in months
        
    For zero-interest loans (r == 0):
        EMI = P / n
    """
    p = Decimal(str(loan_amount))
    rate = Decimal(str(annual_rate))
    n = tenure_months

    # Validation
    if p <= Decimal("0"):
        raise ValueError("Loan amount must be greater than zero.")
    if rate < Decimal("0"):
        raise ValueError("Annual interest rate cannot be negative.")
    if n <= 0:
        raise ValueError("Loan tenure must be at least 1 month.")

    # Zero interest loan edge case
    if rate == Decimal("0"):
        emi = p / Decimal(n)
        return round_monetary(emi, rounding_mode)

    # Monthly interest rate as fraction
    r = rate / Decimal("1200")

    # (1 + r)^n
    # Using Decimal power or float conversion with Decimal precision
    one_plus_r_pow_n = (Decimal("1") + r) ** Decimal(n)
    numerator = p * r * one_plus_r_pow_n
    denominator = one_plus_r_pow_n - Decimal("1")

    emi = numerator / denominator
    return round_monetary(emi, rounding_mode)


def calculate_loan_summary(
    loan_amount: float,
    annual_rate: float,
    tenure_years: int,
    tenure_months_extra: int = 0,
    start_date: Optional[datetime.date] = None,
    method: str = "monthly_reducing",
    rounding_mode: str = "standard"
) -> LoanSummary:
    """
    Computes complete loan summary metrics from user inputs.
    """
    total_months = (tenure_years * 12) + tenure_months_extra
    if total_months <= 0:
        raise ValueError("Total tenure must be at least 1 month.")

    monthly_emi = calculate_emi(
        loan_amount=loan_amount,
        annual_rate=annual_rate,
        tenure_months=total_months,
        rounding_mode=rounding_mode
    )

    monthly_interest_rate = round(annual_rate / 12.0, 4)

    # Note: total_repayment and total_interest here represent initial theoretical totals.
    # The exact schedule sums may adjust by pennies in the final month to ensure exact zero closing balance.
    total_repayment = round(monthly_emi * total_months, 2)
    total_interest = round(total_repayment - loan_amount, 2)
    
    # Avoid negative total interest due to small rounding if rate == 0
    if annual_rate == 0.0 or total_interest < 0:
        total_interest = 0.0
        total_repayment = loan_amount

    ratio = round((total_interest / loan_amount) * 100.0, 2) if loan_amount > 0 else 0.0

    completion_date = None
    if start_date is not None:
        completion_date = add_months(start_date, total_months)

    return LoanSummary(
        loan_amount=round(loan_amount, 2),
        annual_rate=annual_rate,
        tenure_months=total_months,
        tenure_years=round(total_months / 12.0, 2),
        monthly_emi=monthly_emi,
        monthly_interest_rate=monthly_interest_rate,
        total_interest=total_interest,
        total_repayment=total_repayment,
        interest_to_principal_ratio=ratio,
        start_date=start_date,
        completion_date=completion_date,
        method=method
    )
