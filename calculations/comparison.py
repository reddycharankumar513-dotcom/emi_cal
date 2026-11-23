"""
Scenario Comparison Engine.
Provides unified comparison structures and aggregators between Original,
Option A (Reduce EMI), Option B (Reduce Tenure), and multiple custom prepayment strategies.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import pandas as pd
from .part_payment import RevisedLoanResult


@dataclass
class ScenarioComparison:
    """Detailed side-by-side comparison metrics between loan scenarios."""
    summary_df: pd.DataFrame
    scenarios: Dict[str, RevisedLoanResult]
    original_metrics: Dict[str, Any]
    option_a_metrics: Dict[str, Any]
    option_b_metrics: Dict[str, Any]


def compare_scenarios(
    principal: float,
    orig_schedule: pd.DataFrame,
    result_a: RevisedLoanResult,
    result_b: RevisedLoanResult,
    custom_results: Optional[Dict[str, RevisedLoanResult]] = None
) -> ScenarioComparison:
    """
    Constructs a detailed tabular comparison and metric dictionary across scenarios.
    """
    orig_emi = float(orig_schedule.iloc[0]["EMI"])
    orig_interest = float(orig_schedule["Interest"].sum().round(2))
    orig_total_pay = float(orig_schedule["Cumulative Total"].iloc[-1])
    orig_tenure = len(orig_schedule)
    orig_balance_at_prep = float(orig_schedule[orig_schedule["Month"] == result_a.part_payment_month].iloc[0]["Closing Balance"])

    # Prepare structured scenario data
    rows = [
        {
            "Metric": "Monthly EMI",
            "Original Loan": orig_emi,
            "Option A: Reduce EMI": result_a.revised_emi,
            "Option B: Reduce Tenure": result_b.revised_emi,
        },
        {
            "Metric": "Loan Tenure (Months)",
            "Original Loan": orig_tenure,
            "Option A: Reduce EMI": result_a.revised_tenure_months,
            "Option B: Reduce Tenure": result_b.revised_tenure_months,
        },
        {
            "Metric": "Loan Tenure (Years)",
            "Original Loan": round(orig_tenure / 12.0, 2),
            "Option A: Reduce EMI": round(result_a.revised_tenure_months / 12.0, 2),
            "Option B: Reduce Tenure": round(result_b.revised_tenure_months / 12.0, 2),
        },
        {
            "Metric": "Tenure Reduction (Months)",
            "Original Loan": 0,
            "Option A: Reduce EMI": 0,
            "Option B: Reduce Tenure": result_b.tenure_reduction_months,
        },
        {
            "Metric": "EMIs Eliminated",
            "Original Loan": 0,
            "Option A: Reduce EMI": 0,
            "Option B: Reduce Tenure": result_b.emis_eliminated,
        },
        {
            "Metric": "Balance After Part-Payment",
            "Original Loan": orig_balance_at_prep,
            "Option A: Reduce EMI": result_a.balance_after_part_payment,
            "Option B: Reduce Tenure": result_b.balance_after_part_payment,
        },
        {
            "Metric": "Part-Payment Amount Paid",
            "Original Loan": 0.0,
            "Option A: Reduce EMI": result_a.total_prepayment_paid,
            "Option B: Reduce Tenure": result_b.total_prepayment_paid,
        },
        {
            "Metric": "Total Principal Repaid",
            "Original Loan": principal,
            "Option A: Reduce EMI": principal,
            "Option B: Reduce Tenure": principal,
        },
        {
            "Metric": "Total Interest Payable",
            "Original Loan": orig_interest,
            "Option A: Reduce EMI": result_a.revised_total_interest,
            "Option B: Reduce Tenure": result_b.revised_total_interest,
        },
        {
            "Metric": "Total Interest Saved",
            "Original Loan": 0.0,
            "Option A: Reduce EMI": result_a.interest_saved,
            "Option B: Reduce Tenure": result_b.interest_saved,
        },
        {
            "Metric": "Interest Savings (%)",
            "Original Loan": 0.0,
            "Option A: Reduce EMI": result_a.interest_savings_pct,
            "Option B: Reduce Tenure": result_b.interest_savings_pct,
        },
        {
            "Metric": "Total Repayment Amount",
            "Original Loan": orig_total_pay,
            "Option A: Reduce EMI": result_a.revised_total_payment,
            "Option B: Reduce Tenure": result_b.revised_total_payment,
        },
        {
            "Metric": "EMI Reduction Amount",
            "Original Loan": 0.0,
            "Option A: Reduce EMI": result_a.emi_reduction_amount,
            "Option B: Reduce Tenure": 0.0,
        },
        {
            "Metric": "EMI Reduction (%)",
            "Original Loan": 0.0,
            "Option A: Reduce EMI": result_a.emi_reduction_pct,
            "Option B: Reduce Tenure": 0.0,
        },
    ]

    df_comp = pd.DataFrame(rows)

    # If any custom scenarios were passed, append columns
    scenarios_dict = {
        "Option A (Reduce EMI)": result_a,
        "Option B (Reduce Tenure)": result_b,
    }
    if custom_results:
        for name, res in custom_results.items():
            scenarios_dict[name] = res
            col_data = [
                res.revised_emi,
                res.revised_tenure_months,
                round(res.revised_tenure_months / 12.0, 2),
                res.tenure_reduction_months,
                res.emis_eliminated,
                res.balance_after_part_payment,
                res.total_prepayment_paid,
                principal,
                res.revised_total_interest,
                res.interest_saved,
                res.interest_savings_pct,
                res.revised_total_payment,
                res.emi_reduction_amount,
                res.emi_reduction_pct,
            ]
            df_comp[name] = col_data

    orig_metrics = {
        "emi": orig_emi,
        "tenure_months": orig_tenure,
        "total_interest": orig_interest,
        "total_payment": orig_total_pay,
        "principal": principal,
    }

    opt_a_metrics = {
        "revised_emi": result_a.revised_emi,
        "emi_reduction": result_a.emi_reduction_amount,
        "emi_reduction_pct": result_a.emi_reduction_pct,
        "interest_saved": result_a.interest_saved,
        "savings_pct": result_a.interest_savings_pct,
        "total_payment": result_a.revised_total_payment,
    }

    opt_b_metrics = {
        "revised_tenure": result_b.revised_tenure_months,
        "tenure_reduction": result_b.tenure_reduction_months,
        "emis_eliminated": result_b.emis_eliminated,
        "interest_saved": result_b.interest_saved,
        "savings_pct": result_b.interest_savings_pct,
        "total_payment": result_b.revised_total_payment,
    }

    return ScenarioComparison(
        summary_df=df_comp,
        scenarios=scenarios_dict,
        original_metrics=orig_metrics,
        option_a_metrics=opt_a_metrics,
        option_b_metrics=opt_b_metrics,
    )
