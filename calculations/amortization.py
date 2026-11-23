"""
Amortization Schedule Generation Module.
Produces full month-by-month repayment schedules with exact zero final balance,
tracking opening balances, EMI, interest, principal, prepayments, and cumulative values.
"""

from typing import Optional, Dict, Any, List
import datetime
import pandas as pd
from decimal import Decimal
from .emi import calculate_emi
from .interest import calculate_monthly_interest, add_months, round_monetary


def generate_amortization_schedule(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    start_date: Optional[datetime.date] = None,
    custom_emi: Optional[float] = None,
    prepayments: Optional[Dict[int, float]] = None,
    convention: str = "monthly_reducing",
    rounding_mode: str = "standard"
) -> pd.DataFrame:
    """
    Generates a month-by-month amortization schedule as a Pandas DataFrame.
    
    Parameters:
    - principal: Initial loan principal (P > 0)
    - annual_rate: Annual interest rate in percent (>= 0)
    - tenure_months: Scheduled duration in months (> 0)
    - start_date: First repayment date (optional)
    - custom_emi: Overridden monthly EMI amount (optional, e.g. for tenure reduction)
    - prepayments: Dict mapping month_number -> additional principal amount
    - convention: 'monthly_reducing' or 'daily_reducing'
    - rounding_mode: 'standard', 'round_rupee', or 'bankers'
    
    Returns:
    - pd.DataFrame containing:
      [Month, Payment Date, Opening Balance, EMI, Interest, Principal,
       Additional Payment, Total Principal, Closing Balance,
       Cumulative Interest, Cumulative Principal, Cumulative Total]
    """
    if principal <= 0:
        raise ValueError("Loan principal must be greater than zero.")
    if annual_rate < 0:
        raise ValueError("Interest rate cannot be negative.")
    if tenure_months <= 0:
        raise ValueError("Tenure months must be greater than zero.")

    if prepayments is None:
        prepayments = {}

    # Base scheduled EMI
    if custom_emi is not None and custom_emi > 0:
        scheduled_emi = custom_emi
    else:
        scheduled_emi = calculate_emi(
            loan_amount=principal,
            annual_rate=annual_rate,
            tenure_months=tenure_months,
            rounding_mode=rounding_mode
        )

    records: List[Dict[str, Any]] = []
    current_balance = round(float(principal), 2)
    cum_interest = 0.0
    cum_principal = 0.0
    cum_total = 0.0

    current_date = start_date
    month = 1
    # Max safety limit to prevent infinite loops (e.g. 100 years = 1200 months)
    max_months = max(tenure_months * 2, 1200)

    while current_balance > 0.0001 and month <= max_months:
        payment_date_val = None
        if start_date is not None:
            # 1st month is start_date, subsequent months add (month - 1)
            payment_date_val = add_months(start_date, month - 1)

        opening_balance = current_balance

        # 1. Interest calculation on opening balance
        interest_amount = calculate_monthly_interest(
            balance=opening_balance,
            annual_rate=annual_rate,
            convention=convention,
            current_date=payment_date_val,
            rounding_mode=rounding_mode
        )

        # 2. Scheduled principal component
        if annual_rate == 0:
            interest_amount = 0.0
            normal_principal = scheduled_emi
        else:
            normal_principal = round(scheduled_emi - interest_amount, 2)

        # Ensure normal principal does not exceed opening balance
        if normal_principal >= opening_balance or month == tenure_months and not prepayments:
            # Final payoff adjustment
            normal_principal = opening_balance
            actual_emi = round(opening_balance + interest_amount, 2)
        elif normal_principal < 0:
            # If EMI is less than interest (underpayment error prevention)
            normal_principal = 0.0
            actual_emi = interest_amount
        else:
            actual_emi = scheduled_emi

        # 3. Additional prepayment for this month
        extra_payment = round(float(prepayments.get(month, 0.0)), 2)
        if extra_payment < 0:
            raise ValueError(f"Additional payment for month {month} cannot be negative.")

        # Prepayment cannot exceed remaining balance after scheduled principal
        rem_after_scheduled = round(opening_balance - normal_principal, 2)
        if extra_payment > rem_after_scheduled:
            extra_payment = rem_after_scheduled

        # 4. Total principal repaid this month
        total_principal = round(normal_principal + extra_payment, 2)
        
        # 5. Closing balance
        closing_balance = round(opening_balance - total_principal, 2)
        if closing_balance < 0.001:
            # Ensure exact zero
            closing_balance = 0.0
            # Absorb any sub-cent rounding discrepancy
            discrepancy = round(opening_balance - (normal_principal + extra_payment), 4)
            if abs(discrepancy) > 0 and abs(discrepancy) < 0.05:
                normal_principal = round(normal_principal + discrepancy, 2)
                actual_emi = round(normal_principal + interest_amount, 2)
                total_principal = round(normal_principal + extra_payment, 2)

        # Update running cumulative totals
        cum_interest = round(cum_interest + interest_amount, 2)
        cum_principal = round(cum_principal + total_principal, 2)
        cum_total = round(cum_total + actual_emi + extra_payment, 2)

        records.append({
            "Month": month,
            "Payment Date": payment_date_val.strftime("%Y-%m-%d") if payment_date_val else f"Month {month}",
            "Opening Balance": opening_balance,
            "EMI": actual_emi,
            "Interest": interest_amount,
            "Principal": normal_principal,
            "Additional Payment": extra_payment,
            "Total Principal": total_principal,
            "Closing Balance": closing_balance,
            "Cumulative Interest": cum_interest,
            "Cumulative Principal": cum_principal,
            "Cumulative Total": cum_total,
        })

        current_balance = closing_balance
        if current_balance <= 0.0001:
            break

        month += 1

    df = pd.DataFrame(records)

    # Final reconciliation pass:
    # Guarantee that the sum of Total Principal exactly equals original principal
    if not df.empty:
        total_repaid_principal = df["Total Principal"].sum()
        diff = round(principal - total_repaid_principal, 2)
        if abs(diff) > 0 and abs(diff) < 1.0:
            last_idx = df.index[-1]
            df.loc[last_idx, "Principal"] = round(df.loc[last_idx, "Principal"] + diff, 2)
            df.loc[last_idx, "Total Principal"] = round(df.loc[last_idx, "Total Principal"] + diff, 2)
            df.loc[last_idx, "EMI"] = round(df.loc[last_idx, "EMI"] + diff, 2)
            df.loc[last_idx, "Cumulative Principal"] = round(principal, 2)
            df.loc[last_idx, "Cumulative Total"] = round(df.loc[last_idx, "Cumulative Total"] + diff, 2)
            df.loc[last_idx, "Closing Balance"] = 0.0

    return df
