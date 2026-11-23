"""
Part-Payment and Prepayment Calculation Engine.
Implements Option A (Reduce EMI) and Option B (Reduce Tenure),
supporting one-time part-payments, recurring prepayments, custom schedules, and foreclosure.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Any
import datetime
import pandas as pd
from .emi import calculate_emi
from .interest import calculate_monthly_interest, add_months, round_monetary
from .amortization import generate_amortization_schedule


@dataclass
class PrepaymentEntry:
    """Represents a scheduled extra principal payment."""
    month: int
    amount: float
    description: str = "Prepayment"


@dataclass
class RevisedLoanResult:
    """Encapsulates the financial outcomes of a loan revision scenario."""
    option_type: str  # 'reduce_emi' or 'reduce_tenure'
    original_emi: float
    revised_emi: float
    emi_reduction_amount: float
    emi_reduction_pct: float
    original_tenure_months: int
    revised_tenure_months: int
    tenure_reduction_months: int
    emis_eliminated: int
    original_total_interest: float
    revised_total_interest: float
    interest_saved: float
    interest_savings_pct: float
    original_total_payment: float
    revised_total_payment: float
    total_prepayment_paid: float
    balance_after_part_payment: float
    part_payment_month: int
    revised_schedule: pd.DataFrame
    original_completion_date: Optional[datetime.date]
    revised_completion_date: Optional[datetime.date]


def get_outstanding_balance_after_month(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    target_month: int,
    rounding_mode: str = "standard"
) -> float:
    """
    Computes the outstanding principal balance immediately after the target_month regular EMI
    has been paid (before any additional part-payment in that month).
    """
    if target_month <= 0:
        return float(principal)
    if target_month >= tenure_months:
        return 0.0

    orig_schedule = generate_amortization_schedule(
        principal=principal,
        annual_rate=annual_rate,
        tenure_months=tenure_months,
        rounding_mode=rounding_mode
    )
    month_row = orig_schedule[orig_schedule["Month"] == target_month]
    if month_row.empty:
        return 0.0
    return float(month_row.iloc[0]["Closing Balance"])


def calculate_revised_schedule_reduce_emi(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    part_payment_month: int,
    part_payment_amount: float,
    start_date: Optional[datetime.date] = None,
    convention: str = "monthly_reducing",
    rounding_mode: str = "standard"
) -> RevisedLoanResult:
    """
    Option A: Keep original loan completion date, reduce monthly EMI for remaining months.
    
    1. Generates original schedule up to part_payment_month.
    2. Subtracts part_payment_amount from the closing balance of part_payment_month.
    3. Calculates new lower EMI for remaining months: (tenure_months - part_payment_month).
    4. Completes schedule with new EMI, ensuring exact original maturity date.
    """
    if part_payment_month < 1 or part_payment_month >= tenure_months:
        raise ValueError(f"Part-payment month must be between 1 and {tenure_months - 1}.")
    if part_payment_amount <= 0:
        raise ValueError("Part-payment amount must be greater than zero.")

    # 1. Original baseline
    orig_schedule = generate_amortization_schedule(
        principal=principal,
        annual_rate=annual_rate,
        tenure_months=tenure_months,
        start_date=start_date,
        convention=convention,
        rounding_mode=rounding_mode
    )
    orig_emi = float(orig_schedule.iloc[0]["EMI"])
    orig_interest = float(orig_schedule["Interest"].sum())
    orig_total_pay = float(orig_schedule["EMI"].sum())
    orig_comp_date = add_months(start_date, tenure_months) if start_date else None

    # Check balance at target month
    balance_before_prep = float(orig_schedule[orig_schedule["Month"] == part_payment_month].iloc[0]["Closing Balance"])
    if part_payment_amount > balance_before_prep:
        raise ValueError(
            f"Additional payment of ₹{part_payment_amount:,.2f} exceeds outstanding principal "
            f"of ₹{balance_before_prep:,.2f} at month {part_payment_month}."
        )

    balance_after_prep = round(balance_before_prep - part_payment_amount, 2)
    remaining_months = tenure_months - part_payment_month

    # If completely paid off
    if balance_after_prep <= 0.01:
        # Loan foreclosed at part_payment_month
        revised_schedule = generate_amortization_schedule(
            principal=principal,
            annual_rate=annual_rate,
            tenure_months=tenure_months,
            start_date=start_date,
            prepayments={part_payment_month: part_payment_amount},
            convention=convention,
            rounding_mode=rounding_mode
        )
        new_emi = 0.0
        rev_interest = float(revised_schedule["Interest"].sum())
        rev_total_pay = float(revised_schedule["EMI"].sum() + revised_schedule["Additional Payment"].sum())
        rev_tenure = len(revised_schedule)
        rev_comp_date = add_months(start_date, rev_tenure) if start_date else None

        return RevisedLoanResult(
            option_type="reduce_emi",
            original_emi=orig_emi,
            revised_emi=0.0,
            emi_reduction_amount=orig_emi,
            emi_reduction_pct=100.0,
            original_tenure_months=tenure_months,
            revised_tenure_months=rev_tenure,
            tenure_reduction_months=tenure_months - rev_tenure,
            emis_eliminated=tenure_months - rev_tenure,
            original_total_interest=orig_interest,
            revised_total_interest=rev_interest,
            interest_saved=round(orig_interest - rev_interest, 2),
            interest_savings_pct=round(((orig_interest - rev_interest) / orig_interest) * 100, 2) if orig_interest > 0 else 0.0,
            original_total_payment=orig_total_pay,
            revised_total_payment=rev_total_pay,
            total_prepayment_paid=part_payment_amount,
            balance_after_part_payment=0.0,
            part_payment_month=part_payment_month,
            revised_schedule=revised_schedule,
            original_completion_date=orig_comp_date,
            revised_completion_date=rev_comp_date
        )

    # Calculate new EMI for the remaining duration
    new_emi = calculate_emi(
        loan_amount=balance_after_prep,
        annual_rate=annual_rate,
        tenure_months=remaining_months,
        rounding_mode=rounding_mode
    )

    # Build full composite schedule:
    # First part: month 1 to part_payment_month from original schedule
    part1_df = orig_schedule[orig_schedule["Month"] <= part_payment_month].copy()
    # At part_payment_month, add the extra prepayment
    part1_df.loc[part1_df["Month"] == part_payment_month, "Additional Payment"] = part_payment_amount
    part1_df.loc[part1_df["Month"] == part_payment_month, "Total Principal"] = round(
        part1_df.loc[part1_df["Month"] == part_payment_month, "Principal"] + part_payment_amount, 2
    )
    part1_df.loc[part1_df["Month"] == part_payment_month, "Closing Balance"] = balance_after_prep

    # Second part: remaining months starting from balance_after_prep with new_emi
    part2_start_date = add_months(start_date, part_payment_month) if start_date else None
    part2_df = generate_amortization_schedule(
        principal=balance_after_prep,
        annual_rate=annual_rate,
        tenure_months=remaining_months,
        start_date=part2_start_date,
        custom_emi=new_emi,
        convention=convention,
        rounding_mode=rounding_mode
    )
    # Adjust month numbers for part 2
    part2_df["Month"] = part2_df["Month"] + part_payment_month

    # Combine schedules
    combined_df = pd.concat([part1_df, part2_df], ignore_index=True)

    # Recompute cumulative totals
    combined_df["Cumulative Interest"] = combined_df["Interest"].cumsum().round(2)
    combined_df["Cumulative Principal"] = combined_df["Total Principal"].cumsum().round(2)
    combined_df["Cumulative Total"] = (combined_df["EMI"] + combined_df["Additional Payment"]).cumsum().round(2)

    rev_interest = float(combined_df["Interest"].sum().round(2))
    rev_total_pay = float((combined_df["EMI"] + combined_df["Additional Payment"]).sum().round(2))
    interest_saved = max(0.0, round(orig_interest - rev_interest, 2))
    savings_pct = round((interest_saved / orig_interest) * 100, 2) if orig_interest > 0 else 0.0

    emi_diff = max(0.0, round(orig_emi - new_emi, 2))
    emi_diff_pct = round((emi_diff / orig_emi) * 100, 2) if orig_emi > 0 else 0.0

    return RevisedLoanResult(
        option_type="reduce_emi",
        original_emi=orig_emi,
        revised_emi=new_emi,
        emi_reduction_amount=emi_diff,
        emi_reduction_pct=emi_diff_pct,
        original_tenure_months=tenure_months,
        revised_tenure_months=tenure_months,
        tenure_reduction_months=0,
        emis_eliminated=0,
        original_total_interest=orig_interest,
        revised_total_interest=rev_interest,
        interest_saved=interest_saved,
        interest_savings_pct=savings_pct,
        original_total_payment=orig_total_pay,
        revised_total_payment=rev_total_pay,
        total_prepayment_paid=part_payment_amount,
        balance_after_part_payment=balance_after_prep,
        part_payment_month=part_payment_month,
        revised_schedule=combined_df,
        original_completion_date=orig_comp_date,
        revised_completion_date=orig_comp_date
    )


def calculate_revised_schedule_reduce_tenure(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    part_payment_month: int,
    part_payment_amount: float,
    start_date: Optional[datetime.date] = None,
    convention: str = "monthly_reducing",
    rounding_mode: str = "standard"
) -> RevisedLoanResult:
    """
    Option B: Keep original monthly EMI unchanged, reduce loan tenure.
    
    1. Same original schedule up to part_payment_month.
    2. Subtracts part_payment_amount from outstanding principal at part_payment_month.
    3. Continues with original monthly EMI until balance reaches exact zero.
    4. Calculates new number of EMIs, revised maturity date, and interest saved.
    """
    if part_payment_month < 1 or part_payment_month >= tenure_months:
        raise ValueError(f"Part-payment month must be between 1 and {tenure_months - 1}.")
    if part_payment_amount <= 0:
        raise ValueError("Part-payment amount must be greater than zero.")

    orig_schedule = generate_amortization_schedule(
        principal=principal,
        annual_rate=annual_rate,
        tenure_months=tenure_months,
        start_date=start_date,
        convention=convention,
        rounding_mode=rounding_mode
    )
    orig_emi = float(orig_schedule.iloc[0]["EMI"])
    orig_interest = float(orig_schedule["Interest"].sum())
    orig_total_pay = float(orig_schedule["EMI"].sum())
    orig_comp_date = add_months(start_date, tenure_months) if start_date else None

    # Check balance at target month
    balance_before_prep = float(orig_schedule[orig_schedule["Month"] == part_payment_month].iloc[0]["Closing Balance"])
    if part_payment_amount > balance_before_prep:
        raise ValueError(
            f"Additional payment of ₹{part_payment_amount:,.2f} exceeds outstanding principal "
            f"of ₹{balance_before_prep:,.2f} at month {part_payment_month}."
        )

    balance_after_prep = round(balance_before_prep - part_payment_amount, 2)

    # Generate schedule with prepayment at part_payment_month while maintaining original EMI
    revised_schedule = generate_amortization_schedule(
        principal=principal,
        annual_rate=annual_rate,
        tenure_months=tenure_months,
        start_date=start_date,
        custom_emi=orig_emi,
        prepayments={part_payment_month: part_payment_amount},
        convention=convention,
        rounding_mode=rounding_mode
    )

    rev_tenure = len(revised_schedule)
    rev_interest = float(revised_schedule["Interest"].sum().round(2))
    rev_total_pay = float((revised_schedule["EMI"] + revised_schedule["Additional Payment"]).sum().round(2))
    
    interest_saved = max(0.0, round(orig_interest - rev_interest, 2))
    savings_pct = round((interest_saved / orig_interest) * 100, 2) if orig_interest > 0 else 0.0

    tenure_reduced = max(0, tenure_months - rev_tenure)
    rev_comp_date = add_months(start_date, rev_tenure) if start_date else None

    return RevisedLoanResult(
        option_type="reduce_tenure",
        original_emi=orig_emi,
        revised_emi=orig_emi,  # EMI stays unchanged
        emi_reduction_amount=0.0,
        emi_reduction_pct=0.0,
        original_tenure_months=tenure_months,
        revised_tenure_months=rev_tenure,
        tenure_reduction_months=tenure_reduced,
        emis_eliminated=tenure_reduced,
        original_total_interest=orig_interest,
        revised_total_interest=rev_interest,
        interest_saved=interest_saved,
        interest_savings_pct=savings_pct,
        original_total_payment=orig_total_pay,
        revised_total_payment=rev_total_pay,
        total_prepayment_paid=part_payment_amount,
        balance_after_part_payment=balance_after_prep,
        part_payment_month=part_payment_month,
        revised_schedule=revised_schedule,
        original_completion_date=orig_comp_date,
        revised_completion_date=rev_comp_date
    )


def calculate_custom_prepayment_schedule(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    prepayments: Dict[int, float],
    start_date: Optional[datetime.date] = None,
    convention: str = "monthly_reducing",
    rounding_mode: str = "standard"
) -> RevisedLoanResult:
    """
    Simulates custom multi-prepayment scenarios (e.g. monthly extra ₹5k, yearly ₹50k, arbitrary list).
    """
    orig_schedule = generate_amortization_schedule(
        principal=principal,
        annual_rate=annual_rate,
        tenure_months=tenure_months,
        start_date=start_date,
        convention=convention,
        rounding_mode=rounding_mode
    )
    orig_emi = float(orig_schedule.iloc[0]["EMI"])
    orig_interest = float(orig_schedule["Interest"].sum())
    orig_total_pay = float(orig_schedule["EMI"].sum())
    orig_comp_date = add_months(start_date, tenure_months) if start_date else None

    revised_schedule = generate_amortization_schedule(
        principal=principal,
        annual_rate=annual_rate,
        tenure_months=tenure_months,
        start_date=start_date,
        custom_emi=orig_emi,
        prepayments=prepayments,
        convention=convention,
        rounding_mode=rounding_mode
    )

    total_prep_paid = float(revised_schedule["Additional Payment"].sum().round(2))
    rev_tenure = len(revised_schedule)
    rev_interest = float(revised_schedule["Interest"].sum().round(2))
    rev_total_pay = float((revised_schedule["EMI"] + revised_schedule["Additional Payment"]).sum().round(2))

    interest_saved = max(0.0, round(orig_interest - rev_interest, 2))
    savings_pct = round((interest_saved / orig_interest) * 100, 2) if orig_interest > 0 else 0.0
    tenure_reduced = max(0, tenure_months - rev_tenure)
    rev_comp_date = add_months(start_date, rev_tenure) if start_date else None

    return RevisedLoanResult(
        option_type="custom_prepayments",
        original_emi=orig_emi,
        revised_emi=orig_emi,
        emi_reduction_amount=0.0,
        emi_reduction_pct=0.0,
        original_tenure_months=tenure_months,
        revised_tenure_months=rev_tenure,
        tenure_reduction_months=tenure_reduced,
        emis_eliminated=tenure_reduced,
        original_total_interest=orig_interest,
        revised_total_interest=rev_interest,
        interest_saved=interest_saved,
        interest_savings_pct=savings_pct,
        original_total_payment=orig_total_pay,
        revised_total_payment=rev_total_pay,
        total_prepayment_paid=total_prep_paid,
        balance_after_part_payment=0.0,
        part_payment_month=min(prepayments.keys()) if prepayments else 1,
        revised_schedule=revised_schedule,
        original_completion_date=orig_comp_date,
        revised_completion_date=rev_comp_date
    )
