"""
Calculations Package
Houses the financial calculation engine for Loan EMI, Amortization Schedules,
Part-Payments, Prepayments, and Scenario Comparisons.
"""

from .emi import calculate_emi, calculate_loan_summary, LoanSummary
from .interest import calculate_monthly_interest, round_monetary
from .amortization import generate_amortization_schedule
from .part_payment import (
    calculate_revised_schedule_reduce_emi,
    calculate_revised_schedule_reduce_tenure,
    PrepaymentEntry,
    RevisedLoanResult,
)
from .comparison import compare_scenarios, ScenarioComparison

__all__ = [
    "calculate_emi",
    "calculate_loan_summary",
    "LoanSummary",
    "calculate_monthly_interest",
    "round_monetary",
    "generate_amortization_schedule",
    "calculate_revised_schedule_reduce_emi",
    "calculate_revised_schedule_reduce_tenure",
    "PrepaymentEntry",
    "RevisedLoanResult",
    "compare_scenarios",
    "ScenarioComparison",
]
