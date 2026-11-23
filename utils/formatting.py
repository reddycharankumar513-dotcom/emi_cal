"""
Currency, Date, and Metric Formatting Utilities.
Specializes in Indian Rupee (₹) formatting with traditional Lakh/Crore grouping.
"""

from typing import Union, Optional
import datetime
from decimal import Decimal


def format_indian_number(num: Union[float, int, Decimal], decimals: int = 2) -> str:
    """
    Formats a numeric value using the Indian numbering system.
    Example:
        1234567.89 -> '12,34,567.89'
        100000 -> '1,00,000.00'
        500 -> '500.00'
    """
    if num is None:
        return "0.00"

    try:
        val = float(num)
    except (ValueError, TypeError):
        return str(num)

    is_negative = val < 0
    val = abs(val)

    # Format to fixed decimals
    formatted = f"{val:.{decimals}f}"
    parts = formatted.split(".")
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else ""

    if len(integer_part) <= 3:
        grouped = integer_part
    else:
        # Last 3 digits
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        
        # Group remaining in chunks of 2 from right to left
        groups = []
        while len(remaining) > 2:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.append(remaining)
        groups.reverse()
        grouped = ",".join(groups) + "," + last_three

    result = f"{grouped}.{decimal_part}" if decimals > 0 else grouped
    return f"-{result}" if is_negative else result


def format_currency(
    amount: Union[float, int, Decimal, None],
    style: str = "standard_inr",
    include_symbol: bool = True,
    decimals: int = 2
) -> str:
    """
    Formats monetary amounts with currency symbol and appropriate denomination.
    
    Styles:
    - 'standard_inr': ₹ 10,00,000.00
    - 'lakhs_crores': ₹ 10.00 Lakhs or ₹ 1.25 Cr
    - 'millions': ₹ 1.00 M
    """
    if amount is None:
        return "₹ 0.00" if include_symbol else "0.00"

    val = float(amount)
    symbol = "₹ " if include_symbol else ""

    if style == "lakhs_crores":
        abs_val = abs(val)
        sign = "-" if val < 0 else ""
        if abs_val >= 10_000_000:  # 1 Crore
            return f"{sign}{symbol}{abs_val / 10_000_000:.2f} Cr"
        elif abs_val >= 100_000:   # 1 Lakh
            return f"{sign}{symbol}{abs_val / 100_000:.2f} Lakh"
        elif abs_val >= 1_000:
            return f"{sign}{symbol}{format_indian_number(abs_val, decimals)}"
        else:
            return f"{sign}{symbol}{abs_val:.{decimals}f}"

    elif style == "millions":
        abs_val = abs(val)
        sign = "-" if val < 0 else ""
        if abs_val >= 1_000_000_000:
            return f"{sign}{symbol}{abs_val / 1_000_000_000:.2f} B"
        elif abs_val >= 1_000_000:
            return f"{sign}{symbol}{abs_val / 1_000_000:.2f} M"
        elif abs_val >= 1_000:
            return f"{sign}{symbol}{abs_val / 1_000:.2f} K"
        else:
            return f"{sign}{symbol}{abs_val:.{decimals}f}"

    else:
        # Default standard INR
        return f"{symbol}{format_indian_number(val, decimals)}"


def format_percentage(val: Union[float, int, None], decimals: int = 2) -> str:
    """Format percentage with % sign."""
    if val is None:
        return "0.00%"
    return f"{float(val):.{decimals}f}%"


def format_tenure(months: int) -> str:
    """
    Formats total months into human-readable years and months.
    Example: 65 -> '5 yrs 5 mos (65 months)'
    """
    if months <= 0:
        return "0 months"
    years = months // 12
    rem_months = months % 12
    if years > 0 and rem_months > 0:
        return f"{years} yr{'s' if years > 1 else ''} {rem_months} mo{'s' if rem_months > 1 else ''} ({months} mos)"
    elif years > 0:
        return f"{years} year{'s' if years > 1 else ''} ({months} mos)"
    else:
        return f"{rem_months} month{'s' if rem_months > 1 else ''}"


def format_date_standard(dt: Optional[Union[datetime.date, datetime.datetime, str]]) -> str:
    """Formats date in standard legible Indian/UK format (DD-MMM-YYYY)."""
    if dt is None:
        return "N/A"
    if isinstance(dt, str):
        try:
            dt = datetime.datetime.strptime(dt, "%Y-%m-%d").date()
        except ValueError:
            return dt
    return dt.strftime("%d-%b-%Y")
