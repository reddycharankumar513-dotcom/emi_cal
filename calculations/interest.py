"""
Interest Calculation Module.
Handles monthly and daily reducing balance calculations, date helpers,
and rounding conventions for retail banking standards.
"""

from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_FLOOR
from typing import Optional
import datetime
import calendar


def round_monetary(amount: float | Decimal, mode: str = "standard") -> float:
    """
    Rounds a monetary value according to the configured rounding convention.
    
    Modes:
    - 'standard': Round half up to 2 decimal places (standard financial practice)
    - 'round_rupee': Round to nearest integer (whole Rupee)
    - 'bankers': Banker's rounding (Round half to even, 2 decimal places)
    """
    dec_val = Decimal(str(amount))
    if mode == "round_rupee":
        return float(dec_val.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    elif mode == "bankers":
        return float(dec_val.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))
    else:
        # Default standard
        return float(dec_val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def get_month_days(year: int, month: int) -> int:
    """Return the number of days in the specified month and year."""
    return calendar.monthrange(year, month)[1]


def add_months(sourcedate: datetime.date, months: int) -> datetime.date:
    """
    Safely adds a number of months to a given date, handling end-of-month adjustments
    (e.g., Jan 31 + 1 month = Feb 28 or 29).
    """
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def calculate_monthly_interest(
    balance: float,
    annual_rate: float,
    convention: str = "monthly_reducing",
    current_date: Optional[datetime.date] = None,
    rounding_mode: str = "standard"
) -> float:
    """
    Calculates interest for a single period on the opening balance.
    
    Parameters:
    - balance: Outstanding principal balance at start of period
    - annual_rate: Annual nominal interest rate in percent (e.g. 10.5 for 10.5%)
    - convention: 'monthly_reducing' (rate / 12) or 'daily_reducing' (rate * days / 365)
    - current_date: The payment date (used for daily reducing calculations)
    - rounding_mode: Rounding convention ('standard', 'round_rupee', 'bankers')
    """
    if balance <= 0 or annual_rate <= 0:
        return 0.0

    dec_balance = Decimal(str(balance))
    dec_rate = Decimal(str(annual_rate))

    if convention == "daily_reducing" and current_date is not None:
        # Daily reducing: balance * (rate / 100) * (days_in_current_month / 365)
        days_in_month = get_month_days(current_date.year, current_date.month)
        days_in_year = 366 if calendar.isleap(current_date.year) else 365
        dec_interest = (
            dec_balance * (dec_rate / Decimal("100")) * (Decimal(days_in_month) / Decimal(days_in_year))
        )
    else:
        # Monthly reducing: balance * (annual_rate / 1200)
        dec_interest = dec_balance * (dec_rate / Decimal("1200"))

    return round_monetary(dec_interest, rounding_mode)
